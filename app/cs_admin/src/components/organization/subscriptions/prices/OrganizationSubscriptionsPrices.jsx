// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Alert,
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
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import ContentCard from "../../../general/ContentCard"
import OrganizationMenu from "../../OrganizationMenu"
import AlertInfo from "../../../ui/AlertInfo"

import { GET_SUBSCRIPTION_PRICES_QUERY } from "./queries"

const ARCHIVE_SUBSCRIPTION_PRICE = gql`
  mutation ArchiveOrganizationSubscriptionPrice($input: ArchiveOrganizationSubscriptionPriceInput!) {
    archiveOrganizationSubscriptionPrice(input: $input) {
      organizationSubscriptionPrice {
        id
        archived
      }
    }
  }
`

const OrganizationSubscriptionsPrices = ({ t, history, match, archived=false }) => (
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
            <Query query={GET_SUBSCRIPTION_PRICES_QUERY} variables={{ archived, organizationSubscription: match.params.subscription_id }}>
             {({ loading, error, data: {organizationSubscriptionPrices: subscription_prices, organizationSubscription: subscription}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('organization.subscription_prices.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('organization.subscription_prices.title')}>
                    <p>{t('organization.subscription_prices.error_loading')}</p>
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
                if (!subscription_prices.edges.length) { return (
                  <ContentCard cardTitle={t('organization.subscription_prices.title')}
                               headerContent={headerOptions}>
                    <AlertInfo title='general.subscription' message={subscription.name} />
                    <p>
                    {(!archived) ? t('organization.subscription_prices.empty_list') : t("organization.subscription_prices.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('organization.subscription_prices.title')}
                               headerContent={headerOptions}
                               pageInfo={subscription_prices.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: subscription_prices.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.organizationSubscriptionsPrices.edges
                                    const pageInfo = fetchMoreResult.organizationSubscriptionsPrices.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new subscriptions at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          organizationSubscriptionsPrices: {
                                            __typename: previousResult.organizationSubscriptionsPrices.__typename,
                                            edges: [ ...previousResult.organizationSubscriptionsPrices.edges, ...newEdges ],
                                            pageInfo
                                          }
                                        }
                                      : previousResult
                                  }
                                })
                              }} >
                    <div>
                      <AlertInfo title='general.subscription' message={subscription.name} />

                      <Table>
                        <Table.Header>
                          <Table.Row key={v4()}>
                            <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
                            <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
                            <Table.ColHeader>{t('general.price')}</Table.ColHeader>
                            <Table.ColHeader></Table.ColHeader>
                          </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {subscription_prices.edges.map(({ node }) => (
                              <Table.Row key={v4()}>
                                <Table.Col key={v4()}>
                                  {node.dateStart}
                                </Table.Col>
                                <Table.Col key={v4()}>
                                  {node.dateEnd}
                                </Table.Col>
                                <Table.Col key={v4()}>
                                  {node.priceDisplay}
                                </Table.Col>
                                <Table.Col className="text-right" key={v4()}>
                                  {(node.archived) ? 
                                    <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                    <Button className='btn-sm' 
                                            onClick={() => history.push("/organization/subscriptions/prices/edit/" + match.params.subscription_id + '/' + node.id)}
                                            color="secondary">
                                      {t('general.edit')}
                                    </Button>
                                  }
                                </Table.Col>
                                <Mutation mutation={ARCHIVE_SUBSCRIPTION_PRICE} key={v4()}>
                                  {(archiveSubscriptionsPrice, { data }) => (
                                    <Table.Col className="text-right" key={v4()}>
                                      <button className="icon btn btn-link btn-sm" 
                                          title={t('general.archive')} 
                                          href=""
                                          onClick={() => {
                                            console.log("clicked archived")
                                            let id = node.id
                                            archiveSubscriptionsPrice({ variables: {
                                              input: {
                                              id,
                                              archived: !archived
                                              }
                                      }, refetchQueries: [
                                          { 
                                            query: GET_SUBSCRIPTION_PRICES_QUERY, 
                                            variables: {"archived": archived, organizationSubscription: match.params.subscription_id }
                                          }
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
                      </div>
                  </ContentCard>
                )}}
             }
            </Query>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="organizationsubscriptionprice">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/subscriptions/prices/add/" + match.params.subscription_id)}>
                <Icon prefix="fe" name="plus-circle" /> {t('organization.subscription_prices.add')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='subscriptions'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationSubscriptionsPrices))