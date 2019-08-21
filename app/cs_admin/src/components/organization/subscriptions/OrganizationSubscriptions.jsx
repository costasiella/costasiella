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
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import BadgeBoolean from "../../ui/BadgeBoolean"

import ContentCard from "../../general/ContentCard"
import OrganizationMenu from "../OrganizationMenu"

import { GET_SUBSCRIPTIONS_QUERY } from "./queries"

const ARCHIVE_SUBSCRIPTION = gql`
  mutation ArchiveOrganizationSubscription($input: ArchiveOrganizationSubscriptionInput!) {
    archiveOrganizationSubscription(input: $input) {
      organizationSubscription {
        id
        archived
      }
    }
  }
`


const OrganizationSubscriptions = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("organization.title")}>
          <div className="page-options d-flex">
            <Link to="/organization/subscriptions/groups" 
                  className='btn btn-outline-secondary btn-sm'>
                <Icon prefix="fe" name="folder" /> {t('general.groups')}
            </Link>
          </div>
        </Page.Header>
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_SUBSCRIPTIONS_QUERY} variables={{ archived }}>
             {({ loading, error, data: {organizationSubscriptions: subscriptions}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('organization.subscriptions.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('organization.subscriptions.title')}>
                    <p>{t('organization.subscriptions.error_loading')}</p>
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
                if (!subscriptions.edges.length) { return (
                  <ContentCard cardTitle={t('organization.subscriptions.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('organization.subscriptions.empty_list') : t("organization.subscriptions.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('organization.subscriptions.title')}
                               headerContent={headerOptions}
                               pageInfo={subscriptions.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: subscriptions.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.organizationSubscriptions.edges
                                    const pageInfo = fetchMoreResult.organizationSubscriptions.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new subscriptions at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          organizationSubscriptions: {
                                            __typename: previousResult.organizationSubscriptions.__typename,
                                            edges: [ ...previousResult.organizationSubscriptions.edges, ...newEdges ],
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
                              <Table.ColHeader>{t('general.public')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.shop')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.classes')}</Table.ColHeader>
                              <Table.ColHeader><span className="pull-right">{t('general.price')}</span></Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {subscriptions.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {node.name}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    <BadgeBoolean value={node.displayPublic} />
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    <BadgeBoolean value={node.displayShop} />
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {
                                      (node.unlimited) ? t("general.unlimited"):
                                      <div>
                                        {node.classes} <br />
                                        <span className="text-muted"> {t("general.a")} {node.subscriptionUnitDisplay}</span>
                                      </div>
                                    }
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {node.priceTodayDisplay} <br />
                                    <Link to={"/organization/subscriptions/prices/" + node.id}
                                          className='btn btn-link btn-sm'>
                                        {/* <Icon prefix="fe" name="dollar-sign" />  */}
                                        {t('general.edit_price')}
                                    </Link>
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(node.archived) ? 
                                      <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/organization/subscriptions/edit/" + node.id)}
                                              color="secondary">
                                        {t('general.edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_SUBSCRIPTION} key={v4()}>
                                    {(archiveSubscription, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('general.archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked archived")
                                             let id = node.id
                                             archiveSubscription({ variables: {
                                               input: {
                                                id,
                                                archived: !archived
                                               }
                                        }, refetchQueries: [
                                            {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": archived }}
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
                                  resource="organizationsubscription">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/subscriptions/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('organization.subscriptions.add')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='subscriptions'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationSubscriptions))