from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Organization
from ..modules.gql_tools import require_login_and_permission, get_rid, get_content_file_from_base64_str
from ..modules.messages import Messages

m = Messages()


class OrganizationNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    url_logo_login = graphene.String()
    # url_logo_login_thumbnail_small = graphene.String()
    url_logo_invoice = graphene.String()
    url_logo_email = graphene.String()
    url_logo_shop_header = graphene.String()
    url_logo_self_checkin = graphene.String()


class OrganizationNode(DjangoObjectType):
    class Meta:
        model = Organization
        fields = (
            'archived',
            'name',
            'address',
            'phone',
            'email',
            'registration',
            'tax_registration',
            'logo_login',
            'logo_invoice',
            'logo_email',
            'logo_shop_header',
            'logo_self_checkin',
            'branding_color_background',
            'branding_color_text',
            'branding_color_accent',
            'branding_color_secondary',
        )
        filter_fields = ['archived', 'id']
        interfaces = (graphene.relay.Node, OrganizationNodeInterface,)

    @classmethod
    def get_node(self, info, id):
        # user = info.context.user
        # require_login_and_permission(user, 'costasiella.view_organization')

        return self._meta.model.objects.get(id=id)

    def resolve_url_logo_login(self, info):
        if self.logo_login:
            return self.logo_login.url
        else:
            # TODO: Set a default url with the costasiella logo
            return ''

    def resolve_url_logo_invoice(self, info):
        if self.logo_invoice:
            return self.logo_invoice.url
        else:
            # TODO: Set a default url with the costasiella logo
            return ''

    def resolve_url_logo_email(self, info):
        if self.logo_email:
            return self.logo_email.url
        else:
            # TODO: Set a default url with the costasiella logo
            return ''

    def resolve_url_logo_shop_header(self, info):
        if self.logo_shop_header:
            return self.logo_shop_header.url
        else:
            # TODO: Set a default url with the costasiella logo
            return ''

    def resolve_url_logo_self_checkin(self, info):
        if self.logo_self_checkin:
            return self.logo_self_checkin.url
        else:
            # TODO: Set a default url with the costasiella logo
            return ''
    #
    # def resolve_url_logo_login_thumbnail_small(self, info):
    #     if self.logo_login:
    #         return get_thumbnail(self.logo_login, '50x50', crop='center', quality=99).url
    #     else:
    #         return ''


class OrganizationQuery(graphene.ObjectType):
    organizations = DjangoFilterConnectionField(OrganizationNode)
    organization = graphene.relay.Node.Field(OrganizationNode)

    def resolve_organization(self, info, archived=False, **kwargs):
        # user = info.context.user
        # require_login_and_permission(user, 'costasiella.view_organization')

        ## return everything:
        # if user.has_perm('costasiella.view_organization'):
        return Organization.objects.filter(archived=archived).order_by('name')

        # return None


def validate_create_update_input(input):
    """
    Validate input
    """
    result = {}

    if 'logo_login' in input or 'logo_login_file_name' in input:
        if not (input.get('logo_login', None) and input.get('logo_login_file_name', None)):
            raise Exception(
                _('When setting "logoLogin" or "logoLoginFileName", both fields need to be present and set.')
            )
    if 'logo_invoice' in input or 'logo_invoice_file_name' in input:
        if not (input.get('logo_invoice', None) and input.get('logo_invoice_file_name', None)):
            raise Exception(
                _('When setting "logoInvoice" or "logoInvoiceFileName", both fields need to be present and set.')
            )
    if 'logo_email' in input or 'logo_email_file_name' in input:
        if not (input.get('logo_email', None) and input.get('logo_email_file_name', None)):
            raise Exception(
                _('When setting "logoEmail" or "logoEmailFileName", both fields need to be present and set.')
            )
    if 'logo_shop_header' in input or 'logo_shop_header_file_name' in input:
        if not (input.get('logo_shop_header', None) and input.get('logo_shop_header_file_name', None)):
            raise Exception(
                _('When setting "logoShopHeader" or "logoShopHeaderFileName", both fields need to be present and set.')
            )
    if 'logo_self_checkin' in input or 'logo_self_checkin_file_name' in input:
        if not (input.get('logo_self_checkin', None) and input.get('logo_self_checkin_file_name', None)):
            raise Exception(
                _('When setting "logoSelfCheckin" or "logoSelfCheckinFileName", both fields need to be present and set.')
            )

    return result


# class CreateOrganization(graphene.relay.ClientIDMutation):
#     class Input:
#         name = graphene.String(required=True)
#         address = graphene.String(required=False)
#         phone = graphene.String(required=False)
#         email = graphene.String(required=False)
#         registration = graphene.String(required=False)
#         tax_registration = graphene.String(required=False)
#         logo_login = graphene.String(required=False)
#         logo_login_file_name = graphene.String(required=False)
#
#     organization = graphene.Field(OrganizationNode)
#
#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.add_organization')
#
#         validate_create_update_input(input)
#
#         organization = Organization(
#             name=input['name'],
#         )
#
#         if 'address' in input:
#             organization.address = input['address']
#
#         if 'phone' in input:
#             organization.phone = input['phone']
#
#         if 'email' in input:
#             organization.email = input['email']
#
#         if 'registration' in input:
#             organization.registration = input['registration']
#
#         if 'tax_registration' in input:
#             organization.tax_registration = input['tax_registration']
#
#         if 'logo_login' in input:
#             organization.logo_login = get_content_file_from_base64_str(data_str=input['logo_login'],
#                                                                        file_name=input['logo_login_file_name'])
#
#         organization.save()
#
#         return CreateOrganization(organization=organization)


class UpdateOrganization(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        address = graphene.String(required=False)
        phone = graphene.String(required=False)
        email = graphene.String(required=False)
        registration = graphene.String(required=False)
        tax_registration = graphene.String(required=False)
        logo_login = graphene.String(required=False)
        logo_login_file_name = graphene.String(required=False)
        logo_invoice = graphene.String(required=False)
        logo_invoice_file_name = graphene.String(required=False)
        logo_email = graphene.String(required=False)
        logo_email_file_name = graphene.String(required=False)
        logo_shop_header = graphene.String(required=False)
        logo_shop_header_file_name = graphene.String(required=False)
        logo_self_checkin = graphene.String(required=False)
        logo_self_checkin_file_name = graphene.String(required=False)
        branding_color_background = graphene.String(required=False)
        branding_color_text = graphene.String(required=False)
        branding_color_accent = graphene.String(required=False)
        branding_color_secondary = graphene.String(required=False)

    organization = graphene.Field(OrganizationNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organization')

        rid = get_rid(input['id'])

        organization = Organization.objects.filter(id=rid.id).first()
        if not organization:
            raise Exception('Invalid Organization ID!')

        validate_create_update_input(input)

        if 'name' in input:
            organization.name = input['name']

        if 'address' in input:
            organization.address = input['address']

        if 'phone' in input:
            organization.phone = input['phone']

        if 'email' in input:
            organization.email = input['email']

        if 'registration' in input:
            organization.registration = input['registration']

        if 'tax_registration' in input:
            organization.tax_registration = input['tax_registration']

        if 'logo_login' in input:
            organization.logo_login = get_content_file_from_base64_str(data_str=input['logo_login'],
                                                                       file_name=input['logo_login_file_name'])
        if 'logo_invoice' in input:
            organization.logo_invoice = get_content_file_from_base64_str(data_str=input['logo_invoice'],
                                                                       file_name=input['logo_invoice_file_name'])
        if 'logo_email' in input:
            organization.logo_email = get_content_file_from_base64_str(data_str=input['logo_email'],
                                                                       file_name=input['logo_email_file_name'])
        if 'logo_shop_header' in input:
            organization.logo_shop_header = get_content_file_from_base64_str(data_str=input['logo_shop_header'],
                                                                       file_name=input['logo_shop_header_file_name'])
        if 'logo_self_checkin' in input:
            organization.logo_self_checkin = get_content_file_from_base64_str(data_str=input['logo_self_checkin'],
                                                                       file_name=input['logo_self_checkin_file_name'])

        if 'branding_color_background' in input:
            organization.branding_color_background = input['branding_color_background']

        if 'branding_color_text' in input:
            organization.branding_color_text = input['branding_color_text']

        if 'branding_color_accent' in input:
            organization.branding_color_accent = input['branding_color_accent']

        if 'branding_color_secondary' in input:
            organization.branding_color_secondary = input['branding_color_secondary']

        organization.save()

        return UpdateOrganization(organization=organization)


# class ArchiveOrganization(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)
#         archived = graphene.Boolean(required=True)

#     organization = graphene.Field(OrganizationNode)

#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.delete_organization')

#         rid = get_rid(input['id'])

#         organization = Organization.objects.filter(id=rid.id).first()
#         if not organization:
#             raise Exception('Invalid Organization  ID!')

#         organization.archived = input['archived']
#         organization.save(force_update=True)

#         return ArchiveOrganization(organization=organization)


class OrganizationMutation(graphene.ObjectType):
    # archive_organization = ArchiveOrganization.Field()
    # create_organization = CreateOrganization.Field()
    update_organization = UpdateOrganization.Field()
