from graphql import GraphQLError

class CSClassBookingSubscriptionNoCreditsError(GraphQLError):
    pass

class CSClassBookingSubscriptionBlockedError(GraphQLError):
    pass

class CSClassBookingSubscriptionPausedError(GraphQLError):
    pass
