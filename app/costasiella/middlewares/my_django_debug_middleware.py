from django.db import connections

from promise import Promise

from graphene_django.debug.sql.tracking import unwrap_cursor, wrap_cursor
from graphene_django.debug.exception.formating import wrap_exception
from graphene_django.debug.types import DjangoDebug


class DjangoDebugContext(object):
    def __init__(self):
        self.debug_promise = None
        self.promises = []
        self.object = DjangoDebug(sql=[], exceptions=[])
        self.enable_instrumentation()

    def get_debug_promise(self):
        if not self.debug_promise:
            self.debug_promise = Promise.all(self.promises)
            self.promises = []
        return self.debug_promise.then(self.on_resolve_all_promises).get()

    def on_resolve_error(self, value):
        if hasattr(self, "object"):
            self.object.exceptions.append(wrap_exception(value))
        return Promise.reject(value)

    def on_resolve_all_promises(self, values):
        if self.promises:
            self.debug_promise = None
            return self.get_debug_promise()
        self.disable_instrumentation()
        return self.object

    def add_promise(self, promise):
        if self.debug_promise:
            self.promises.append(promise)

    def enable_instrumentation(self):
        # This is thread-safe because database connections are thread-local.
        for connection in connections.all():
            wrap_cursor(connection, self)

    def disable_instrumentation(self):
        for connection in connections.all():
            unwrap_cursor(connection)


class DjangoDebugMiddleware(object):
    def resolve(self, next, root, info, **args):
        context = info.context
        django_debug = getattr(context, "django_debug", None)
        if not django_debug:
            if context is None:
                raise Exception("DjangoDebug cannot be executed in None contexts")
            try:
                context.django_debug = DjangoDebugContext()
            except Exception:
                raise Exception(
                    "DjangoDebug need the context to be writable, context received: {}.".format(
                        context.__class__.__name__
                    )
                )
        if info.schema.get_type("DjangoDebug") == info.return_type:
            return context.django_debug.get_debug_promise()
        promise = next(root, info, **args)
        # https://github.com/graphql-python/graphene-django/issues/1367
        #try:
        #    promise = next(root, info, **args)
        #except Exception as e:
        #    return context.django_debug.on_resolve_error(e)
        context.django_debug.add_promise(promise)
        return promise

