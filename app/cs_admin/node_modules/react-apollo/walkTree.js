import * as React from 'react';
function getProps(element) {
    return element.props || element.attributes;
}
function isReactElement(element) {
    return !!element.type;
}
function isComponentClass(Comp) {
    return Comp.prototype && (Comp.prototype.render || Comp.prototype.isReactComponent);
}
function providesChildContext(instance) {
    return !!instance.getChildContext;
}
export function walkTree(element, context, visitor, newContext) {
    if (newContext === void 0) { newContext = new Map(); }
    if (!element) {
        return;
    }
    if (Array.isArray(element)) {
        element.forEach(function (item) { return walkTree(item, context, visitor, newContext); });
        return;
    }
    if (isReactElement(element)) {
        if (typeof element.type === 'function') {
            var Comp = element.type;
            var props = Object.assign({}, Comp.defaultProps, getProps(element));
            var childContext_1 = context;
            var child = void 0;
            if (isComponentClass(Comp)) {
                var instance_1 = new Comp(props, context);
                Object.defineProperty(instance_1, 'props', {
                    value: instance_1.props || props,
                });
                instance_1.context = instance_1.context || context;
                instance_1.state = instance_1.state || null;
                instance_1.setState = function (newState) {
                    if (typeof newState === 'function') {
                        newState = newState(instance_1.state, instance_1.props, instance_1.context);
                    }
                    instance_1.state = Object.assign({}, instance_1.state, newState);
                };
                if (Comp.getDerivedStateFromProps) {
                    var result = Comp.getDerivedStateFromProps(instance_1.props, instance_1.state);
                    if (result !== null) {
                        instance_1.state = Object.assign({}, instance_1.state, result);
                    }
                }
                else if (instance_1.UNSAFE_componentWillMount) {
                    instance_1.UNSAFE_componentWillMount();
                }
                else if (instance_1.componentWillMount) {
                    instance_1.componentWillMount();
                }
                if (providesChildContext(instance_1)) {
                    childContext_1 = Object.assign({}, context, instance_1.getChildContext());
                }
                if (visitor(element, instance_1, newContext, context, childContext_1) === false) {
                    return;
                }
                child = instance_1.render();
            }
            else {
                if (visitor(element, null, newContext, context) === false) {
                    return;
                }
                child = Comp(props, context);
            }
            if (child) {
                if (Array.isArray(child)) {
                    child.forEach(function (item) { return walkTree(item, childContext_1, visitor, newContext); });
                }
                else {
                    walkTree(child, childContext_1, visitor, newContext);
                }
            }
        }
        else if (element.type._context || element.type.Consumer) {
            if (visitor(element, null, newContext, context) === false) {
                return;
            }
            var child = void 0;
            if (!!element.type._context) {
                newContext = new Map(newContext);
                newContext.set(element.type, element.props.value);
                child = element.props.children;
            }
            else {
                var value = element.type._currentValue;
                if (newContext.has(element.type.Provider)) {
                    value = newContext.get(element.type.Provider);
                }
                child = element.props.children(value);
            }
            if (child) {
                if (Array.isArray(child)) {
                    child.forEach(function (item) { return walkTree(item, context, visitor, newContext); });
                }
                else {
                    walkTree(child, context, visitor, newContext);
                }
            }
        }
        else {
            if (visitor(element, null, newContext, context) === false) {
                return;
            }
            if (element.props && element.props.children) {
                React.Children.forEach(element.props.children, function (child) {
                    if (child) {
                        walkTree(child, context, visitor, newContext);
                    }
                });
            }
        }
    }
    else if (typeof element === 'string' || typeof element === 'number') {
        visitor(element, null, newContext, context);
    }
}
//# sourceMappingURL=walkTree.js.map