import * as React from 'react';
import * as PropTypes from 'prop-types';
import ApolloClient, { ObservableQuery, ApolloError, ApolloQueryResult, NetworkStatus, FetchMoreOptions, FetchMoreQueryOptions } from 'apollo-client';
import { DocumentNode } from 'graphql';
import { OperationVariables, QueryOpts } from './types';
import { RenderPromises } from './getDataFromTree';
export declare type ObservableQueryFields<TData, TVariables> = Pick<ObservableQuery<TData, TVariables>, 'startPolling' | 'stopPolling' | 'subscribeToMore' | 'updateQuery' | 'refetch' | 'variables'> & {
    fetchMore: (<K extends keyof TVariables>(fetchMoreOptions: FetchMoreQueryOptions<TVariables, K> & FetchMoreOptions<TData, TVariables>) => Promise<ApolloQueryResult<TData>>) & (<TData2, TVariables2, K extends keyof TVariables2>(fetchMoreOptions: {
        query: DocumentNode;
    } & FetchMoreQueryOptions<TVariables2, K> & FetchMoreOptions<TData2, TVariables2>) => Promise<ApolloQueryResult<TData2>>);
};
export interface QueryResult<TData = any, TVariables = OperationVariables> extends ObservableQueryFields<TData, TVariables> {
    client: ApolloClient<any>;
    data: TData | undefined;
    error?: ApolloError;
    loading: boolean;
    networkStatus: NetworkStatus;
}
export interface QueryProps<TData = any, TVariables = OperationVariables> extends QueryOpts<TVariables> {
    children: (result: QueryResult<TData, TVariables>) => React.ReactNode;
    query: DocumentNode;
    displayName?: string;
    skip?: boolean;
    onCompleted?: (data: TData | {}) => void;
    onError?: (error: ApolloError) => void;
}
export interface QueryContext {
    client?: ApolloClient<Object>;
    operations?: Map<string, {
        query: DocumentNode;
        variables: any;
    }>;
    renderPromises?: RenderPromises;
}
export default class Query<TData = any, TVariables = OperationVariables> extends React.Component<QueryProps<TData, TVariables>> {
    static contextTypes: {
        client: PropTypes.Requireable<object>;
        operations: PropTypes.Requireable<object>;
        renderPromises: PropTypes.Requireable<object>;
    };
    static propTypes: {
        client: PropTypes.Requireable<object>;
        children: PropTypes.Validator<(...args: any[]) => any>;
        fetchPolicy: PropTypes.Requireable<string>;
        notifyOnNetworkStatusChange: PropTypes.Requireable<boolean>;
        onCompleted: PropTypes.Requireable<(...args: any[]) => any>;
        onError: PropTypes.Requireable<(...args: any[]) => any>;
        pollInterval: PropTypes.Requireable<number>;
        query: PropTypes.Validator<object>;
        variables: PropTypes.Requireable<object>;
        ssr: PropTypes.Requireable<boolean>;
        partialRefetch: PropTypes.Requireable<boolean>;
    };
    context: QueryContext | undefined;
    private client;
    private queryObservable?;
    private querySubscription?;
    private previousData;
    private refetcherQueue?;
    private hasMounted;
    private operation?;
    constructor(props: QueryProps<TData, TVariables>, context: QueryContext);
    fetchData(): Promise<ApolloQueryResult<any>> | boolean;
    componentDidMount(): void;
    componentWillReceiveProps(nextProps: QueryProps<TData, TVariables>, nextContext: QueryContext): void;
    componentWillUnmount(): void;
    componentDidUpdate(): void;
    render(): React.ReactNode;
    private extractOptsFromProps;
    private initializeQueryObservable;
    private setOperations;
    private updateQuery;
    private startQuerySubscription;
    private removeQuerySubscription;
    private resubscribeToQuery;
    private updateCurrentData;
    private getQueryResult;
}
