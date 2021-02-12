// @flow

import React, { useContext } from 'react'
import { useQuery } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'

import AppSettingsContext from '../../../../../context/AppSettingsContext'
import ButtonAddSecondaryMenu from '../../../../../ui/ButtonAddSecondaryMenu'

import { GET_ACCOUNT_SUBSCRIPTION_ALT_PRICES_QUERY } from './queries'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Table,
} from "tabler-react";
// import HasPermissionWrapper from "../../../../HasPermissionWrapper"
import AccountSubscriptionEditListBase from "../AccountSubscriptionEditListBase"
import AccountSubscriptionEditAltPriceDelete from "./AccountSubscriptionEditAltPriceDelete"
import moment from 'moment';


function AccountSubscriptionEditAltPrices({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  console.log(appSettings)
  
  const id = match.params.subscription_id
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions`
  const activeTab = "alt_prices"

  const buttonAdd = <ButtonAddSecondaryMenu 
                      linkTo={`/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/alt_prices/add`} />

  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_SUBSCRIPTION_ALT_PRICES_QUERY, {
    variables: {
      accountSubscription: subscriptionId
    }
  })
  
  if (loading) return (
    <AccountSubscriptionEditListBase active_tab={activeTab}>
      {t("general.loading_with_dots")}
    </AccountSubscriptionEditListBase>
  )
  if (error) return (
    <AccountSubscriptionEditListBase active_tab={activeTab}>
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </AccountSubscriptionEditListBase>
  )

  console.log('query data')
  console.log(data)

  const accountSubscriptionAltPrices = data.accountSubscriptionAltPrices
  const pageInfo = data.accountSubscriptionAltPrices.pageInfo

    // Empty list
    if (!accountSubscriptionAltPrices.edges.length) { return (
      <AccountSubscriptionEditListBase active_tab={activeTab}>
        <div className="pull-right">{buttonAdd}</div>
        <h5>{t('relations.account.subscriptions.alt_prices.title_list')}</h5>
        <p>{t('relations.account.subscriptions.alt_prices.empty_list')}</p>
      </AccountSubscriptionEditListBase>
    )}

  const onLoadMore = () => {
    fetchMore({
      variables: {
        after: accountSubscriptionAltPrices.pageInfo.endCursor
      },
      updateQuery: (previousResult, { fetchMoreResult }) => {
        const newEdges = fetchMoreResult.accountSubscriptionAltPrices.edges
        const pageInfo = fetchMoreResult.accountSubscriptionAltPrices.pageInfo

        return newEdges.length
          ? {
              // Put the new invoices at the end of the list and update `pageInfo`
              // so we have the new `endCursor` and `hasNextPage` values
              accountSubscriptionAltPrices: {
                __typename: previousResult.accountSubscriptionAltPrices.__typename,
                edges: [ ...previousResult.accountSubscriptionAltPrices.edges, ...newEdges ],
                pageInfo
              }
            }
          : previousResult
      }
    })
  }

  return (
    <AccountSubscriptionEditListBase active_tab={activeTab} pageInfo={pageInfo} onLoadMore={onLoadMore}>
      <div className="pull-right">{buttonAdd}</div>
      <h5>{t('relations.account.subscriptions.alt_prices.title_list')}</h5>
      <Table>
        <Table.Header>
          <Table.Row key={v4()}>
            <Table.ColHeader>{t('general.subscription_year')}</Table.ColHeader>
            <Table.ColHeader>{t('general.subscription_month')}</Table.ColHeader>
            <Table.ColHeader>{t('general.amount')}</Table.ColHeader>
            <Table.ColHeader>{t('general.description')}</Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
            {accountSubscriptionAltPrices.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col>
                  {node.subscriptionYear}
                </Table.Col>
                <Table.Col>
                  {node.subscriptionMonth}
                </Table.Col>
                <Table.Col>
                  {node.amountDisplay}
                </Table.Col>
                <Table.Col>
                <div dangerouslySetInnerHTML={{__html: node.description}} />
                </Table.Col>
                <Table.Col className="text-right">
                  <Link to={`/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/alt_prices/edit/${node.id}`}>
                    <Button className='btn-sm' 
                            color="secondary">
                      {t('general.edit')}
                    </Button>
                  </Link>
                </Table.Col>
                <Table.Col className="text-right">
                  <AccountSubscriptionEditAltPriceDelete id={node.id} />
                </Table.Col>
              </Table.Row>
            ))}
        </Table.Body>
      </Table>
    </AccountSubscriptionEditListBase>
  )
}

export default withTranslation()(withRouter(AccountSubscriptionEditAltPrices))
