import gql from "graphql-tag"

export const GET_SUBSCRIPTION_GROUPS_QUERY = gql`
  query OrganizationSubscriptionGroups($after: String, $before: String) {
    organizationSubscriptionGroups(first: 15, before: $before, after: $after) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
          description
        }
      }
    }
  }
`


export const GET_SUBSCRIPTION_GROUP_QUERY = gql`
  query OrganizationSubscriptionGroup($id: ID!) {
    organizationSubscriptionGroup(id:$id) {
      id
      name
      description
    }
  }
`


export const GET_SUBSCRIPTION_GROUP_SUBSCRIPTIONS_QUERY = gql`
  query GetPassesAndGroupMembership($after: String, $before: String, $id:ID!) {
    organizationSubscriptions(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
        }
      }
    }
    organizationSubscriptionGroup(id: $id) {
      id
      name
      description
      organizationSubscriptions {
        edges {
          node {
            id
            name
          }
        }
      }
    }
  }
`

export const DELETE_SUBSCRIPTION_GROUP = gql`
  mutation DeleteSubscriptionGroup($input: DeleteOrganizationSubscriptionGroupInput!) {
    deleteOrganizationSubscriptionGroup(input: $input) {
      ok
    }
  }
`
