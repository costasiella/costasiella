from graphql import GraphQLError

class CSClassDoesNotTakePlaceOnDateError(GraphQLError):
    pass

class CSClassFullyBookedError(GraphQLError):
    pass

class CSClassBookingSubscriptionAlreadyBookedError(GraphQLError):
    pass

class CSClassBookingSubscriptionNoCreditsError(GraphQLError):
    pass

class CSClassBookingSubscriptionBlockedError(GraphQLError):
    pass

class CSClassBookingSubscriptionPausedError(GraphQLError):
    pass

class CSSubscriptionNotValidOnDateError(GraphQLError):
    pass
