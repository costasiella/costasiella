// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Badge,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../general/ContentCard"
import CardHeaderSeparator from "../../general/CardHeaderSeparator"
import OrganizationMenu from "../OrganizationMenu"

import { GET_SUBSCRIPTION_GROUPS_QUERY } from "./queries"

const ARCHIVE_SUBSCRIPTION_GROUP = gql`
  mutation ArchiveSubscriptionGroup($input: ArchiveOrganizationSubscriptionGroupInput!) {
    archiveOrganizationSubscriptionGroup(input: $input) {
      organizationSubscriptionGroup {
        id
        archived
      }
    }
  }
`


const OrganizationSubscriptionsGroups = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("organization.title")}>
          <div className="page-options d-flex">
            <Link to="/organization/subscriptions" 
                  className='btn btn-outline-secondary btn-sm'>
                <Icon prefix="fe" name="arrow-left" /> {t('general.back_to')} {t('organization.subscriptions.title')}
            </Link>
          </div>
        </Page.Header>
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_SUBSCRIPTION_GROUPS_QUERY} variables={{ archived }}>
             {({ loading, error, data: {organizationSubscriptionGroups: subscription_groups}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('organization.subscription_groups.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('organization.subscription_groups.title')}>
                    <p>{t('organization.subscription_groups.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  <Button color={(!archived) ? 'primary': 'secondary'}  
                          size="sm"
                          onClick={() => {archived=false; refetch({archived});}}>
                    {t('general.current')}
                  </Button>
                  <Button color={(archived) ? 'primary': 'secondary'} 
                          size="sm" 
                          className="ml-2" 
                          onClick={() => {archived=true; refetch({archived});}}>
                    {t('general.archive')}
                  </Button>
                </Card.Options>
                
                // Empty list
                if (!subscription_groups.edges.length) { return (
                  <ContentCard cardTitle={t('organization.subscription_groups.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('organization.subscription_groups.empty_list') : t("organization.subscription_groups.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('organization.subscription_groups.title')}
                               headerContent={headerOptions}
                               pageInfo={subscription_groups.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: subscription_groups.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.organizationSubscriptionGroups.edges
                                    const pageInfo = fetchMoreResult.organizationSubscriptionGroups.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new subscription_groups at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          organizationSubscriptionGroups: {
                                            __typename: previousResult.organizationSubscriptionGroups.__typename,
                                            edges: [ ...previousResult.organizationSubscriptionGroups.edges, ...newEdges ],
                                            pageInfo
                                          }
                                        }
                                      : previousResult
                                  }
                                })
                              }} >
                        <Table>
                          <Table.Header>
                            <Table.Row key={v4()}>
                              <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {subscription_groups.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {node.name}
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(node.archived) ? 
                                      <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                      <span>
                                        <Button className='btn-sm' 
                                                onClick={() => history.push("/organization/subscriptions/groups/edit/" + node.id)}
                                                color="secondary">
                                          {t('general.edit')}
                                        </Button>
                                        <Button className='btn-sm' 
                                                onClick={() => history.push("/organization/subscriptions/groups/edit/passes/" + node.id)}
                                                color="secondary">
                                          {t('organization.subscriptions.groups.edit_passes')}
                                        </Button>
                                      </span>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_SUBSCRIPTION_GROUP} key={v4()}>
                                    {(archiveCostcenter, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('general.archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked archived")
                                             let id = node.id
                                             archiveCostcenter({ variables: {
                                               input: {
                                                id,
                                                archived: !archived
                                               }
                                        }, refetchQueries: [
                                            {query: GET_SUBSCRIPTION_GROUPS_QUERY, variables: {"archived": archived }}
                                        ]}).then(({ data }) => {
                                          console.log('got data', data);
                                          toast.success(
                                            (archived) ? t('general.unarchived'): t('general.archived'), {
                                              position: toast.POSITION.BOTTOM_RIGHT
                                            })
                                        }).catch((error) => {
                                          toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                              position: toast.POSITION.BOTTOM_RIGHT
                                            })
                                          console.log('there was an error sending the query', error);
                                        })
                                        }}>
                                          <Icon prefix="fa" name="inbox" />
                                        </button>
                                      </Table.Col>
                                    )}
                                  </Mutation>
                                </Table.Row>
                              ))}
                          </Table.Body>
                        </Table>
                  </ContentCard>
                )}}
             }
            </Query>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="organizationsubscriptiongroup">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/subscriptions/groups/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('organization.subscription_groups.add')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link=''/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
)

export default withTranslation()(withRouter(OrganizationSubscriptionsGroups))