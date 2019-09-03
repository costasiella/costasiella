// @flow

import React, { useContext } from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import AppSettingsContext from '../../../context/AppSettingsContext'

import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Button,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'
import { confirmAlert } from 'react-confirm-alert'

import ContentCard from "../../../general/ContentCard"
import OrganizationMenu from "../../OrganizationMenu"
import AlertInfo from "../../../ui/AlertInfo"

import { GET_SUBSCRIPTION_PRICES_QUERY } from "./queries"
import { GET_SUBSCRIPTIONS_QUERY } from "../queries"

import moment from 'moment'


const DELETE_SUBSCRIPTION_PRICE = gql`
  mutation DeleteOrganizationSubscriptionPrice($input: DeleteOrganizationSubscriptionPriceInput!) {
    deleteOrganizationSubscriptionPrice(input: $input) {
      ok
    }
  }
`


const confirmDelete = (t, match, deleteSubscriptionPrice, node) => {
  console.log("clicked delete")
  let id = node.id

  confirmAlert({
    customUI: ({ onClose }) => {
      return (
        <div className='custom-ui'>
          <h1>{t('general.confirm_delete')}</h1>
          <p>{t('organization.subscription_prices.delete_confirm_msg')}</p>
          <p>
            {node.priceDisplay} {node.financeTaxRate.name} <br />
            <span className="text-muted">
              {node.dateStart} {(node.dateEnd) ? ' - ' + node.dateEnd : ""}
            </span>
          </p>
          <button className="btn btn-link pull-right" onClick={onClose}>{t('general.confirm_delete_no')}</button>
          <button
            className="btn btn-danger"
            onClick={() => {
            deleteSubscriptionPrice({ variables: {
                input: {
                id
                }
              }, refetchQueries: [
                  {query: GET_SUBSCRIPTION_PRICES_QUERY, variables: { organizationSubscription: match.params.subscription_id }},
                  {query: GET_SUBSCRIPTIONS_QUERY, variables: {archived: false}},
              ]}).then(({ data }) => {
                console.log('got data', data);
                toast.success(
                  t('organization.subscription_prices.deleted'), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
              }).catch((error) => {
                toast.error((t('general.toast_server_error')) + ': ' +  error, {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                console.log('there was an error sending the query', error);
              })
              onClose()
            }}
          >
            <Icon name="trash-2" /> {t('general.confirm_delete_yes')}
          </button>
          
        </div>
      );
    }
  })
}


function OrganizationSubscriptionsPrices ({ t, history, match, archived=false }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat

  return (
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
              <Query query={GET_SUBSCRIPTION_PRICES_QUERY} variables={{ organizationSubscription: match.params.subscription_id }}>
              {({ loading, error, data: {organizationSubscriptionPrices: subscription_prices, organizationSubscription: subscription}, refetch, fetchMore }) => {
                  // Loading
                  if (loading) return (
                    <ContentCard cardTitle={t('organization.subscription_prices.title')}>
                      <Dimmer active={true}
                              loader={true}>
                      </Dimmer>
                    </ContentCard>
                  )
                  // Error
                  if (error) return (
                    <ContentCard cardTitle={t('organization.subscription_prices.title')}>
                      <p>{t('organization.subscription_prices.error_loading')}</p>
                    </ContentCard>
                  )
                  const headerOptions = null

                  // Empty list
                  if (!subscription_prices.edges.length) { return (
                    <ContentCard cardTitle={t('organization.subscription_prices.title')}
                                headerContent={headerOptions}>
                      <AlertInfo title={t('general.subscription')} message={subscription.name} />
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
                        <AlertInfo title={t('general.subscription')} message={subscription.name} />

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
                                    {moment(node.dateStart).format(dateFormat)}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {(node.dateEnd) ? moment(node.dateEnd).format(dateFormat) : ""}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {node.priceDisplay} <br />
                                    <span className="text-muted">{node.financeTaxRate.name}</span>
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
                                  <Mutation mutation={DELETE_SUBSCRIPTION_PRICE} key={v4()}>
                                      {(deleteSubscriptionPrice, { data }) => (
                                        <Table.Col className="text-right" key={v4()}>
                                          <button className="icon btn btn-link btn-sm" 
                                            title={t('general.delete')} 
                                            href=""
                                            onClick={() => {confirmDelete(t, match, deleteSubscriptionPrice, node)}}
                                          >
                                            <span className="text-red">
                                              <Icon prefix="fe" name="trash-2" />
                                            </span>
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
  )
}

export default withTranslation()(withRouter(OrganizationSubscriptionsPrices))