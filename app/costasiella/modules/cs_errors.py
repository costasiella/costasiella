from graphql import GraphQLError

class CSClassBookingSubscriptionAlreadyBookedError(GraphQLError):
    pass

class CSClassBookingSubscriptionNoCreditsError(GraphQLError):
    pass

class CSClassBookingSubscriptionBlockedError(GraphQLError):
    pass

class CSClassBookingSubscriptionPausedError(GraphQLError):
    pass
