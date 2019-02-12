import * as React from 'react';
export interface Context {
    [key: string]: any;
}
export declare function walkTree(element: React.ReactNode, context: Context, visitor: (element: React.ReactNode, instance: React.Component<any> | null, newContextMap: Map<any, any>, context: Context, childContext?: Context) => boolean | void, newContext?: Map<any, any>): void;
