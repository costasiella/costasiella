// @flow

import React, { useContext } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'

import { Formik } from 'formik'
import { toast } from 'react-toastify'
import FinanceInvoicesStatus from "../../../../../ui/FinanceInvoiceStatus"
import ButtonAddSecondaryMenu from '../../../../../ui/ButtonAddSecondaryMenu'

import AppSettingsContext from '../../../../../context/AppSettingsContext'

import { GET_FINANCE_INVOICE_ITEM_QUERY } from './queries'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Table,
  Text
} from "tabler-react";
// import HasPermissionWrapper from "../../../../HasPermissionWrapper"

import CSLS from "../../../../../../tools/cs_local_storage"
import AccountSubscriptionEditInvoiceDelete from "./AccountSubscriptionEditInvoiceDelete"
import AccountSubscriptionEditListBase from "../AccountSubscriptionEditListBase"
// import AccountSubscriptionEditCreditDelete from "./AccountSubscriptionEditCreditDelete"
import moment from 'moment';


function AccountSubscriptionEditInvoices({t, location, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const dateTimeFormatMoment = appSettings.dateTimeFormatMoment
  console.log(appSettings)
  
  const id = match.params.subscription_id
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions`
  const activeTab = "invoices"

  const buttonAdd = <ButtonAddSecondaryMenu 
                     linkTo={`/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/invoices/add`} />

  const { loading, error, data, fetchMore } = useQuery(GET_FINANCE_INVOICE_ITEM_QUERY, {
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
  // Set back location for edit invoice
  localStorage.setItem(CSLS.FINANCE_INVOICES_EDIT_RETURN, location.pathname)

  const financeInvoiceItems = data.financeInvoiceItems
  const pageInfo = data.financeInvoiceItems.pageInfo
  // const inputData = data
  // const account = data.account
  // const initialdata = data.accountSubscription

  // let initialPaymentMethod = ""
  // if (initialdata.financePaymentMethod) {
  //   initialPaymentMethod = initialdata.financePaymentMethod.id
  // }

  const onLoadMore = () => {
    fetchMore({
      variables: {
        after: financeInvoiceItems.pageInfo.endCursor
      },
      updateQuery: (previousResult, { fetchMoreResult }) => {
        const newEdges = fetchMoreResult.financeInvoiceItems.edges
        const pageInfo = fetchMoreResult.financeInvoiceItems.pageInfo

        return newEdges.length
          ? {
              // Put the new invoices at the end of the list and update `pageInfo`
              // so we have the new `endCursor` and `hasNextPage` values
              financeInvoiceItems: {
                __typename: previousResult.financeInvoiceItems.__typename,
                edges: [ ...previousResult.financeInvoiceItems.edges, ...newEdges ],
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
      <h5>{t('relations.account.subscriptions.invoices.title_list')}</h5>
      <Table>
        <Table.Header>
          <Table.Row key={v4()}>
            <Table.ColHeader>{t('general.status')}</Table.ColHeader>
            <Table.ColHeader>{t('finance.invoices.invoice_number')} & {t('finance.invoices.summary')}</Table.ColHeader>
            <Table.ColHeader>{t('finance.invoices.date')} & {t('finance.invoices.due')}</Table.ColHeader>
            {/* <Table.ColHeader>{t('finance.invoices.due')}</Table.ColHeader> */}
            <Table.ColHeader>{t('general.total')}</Table.ColHeader>
            <Table.ColHeader>{t('general.balance')}</Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
            {financeInvoiceItems.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col key={v4()}>
                  <FinanceInvoicesStatus status={node.financeInvoice.status} />
                </Table.Col>
                <Table.Col key={v4()}>
                  {node.financeInvoice.invoiceNumber} <br />
                  <Text.Small color="gray">{node.financeInvoice.summary.trunc(30)}</Text.Small>
                </Table.Col>

                <Table.Col key={v4()}>
                  {moment(node.financeInvoice.dateSent).format('LL')} <br />
                  {moment(node.financeInvoice.dateDue).format('LL')}
                </Table.Col>
                <Table.Col key={v4()}>
                  {node.financeInvoice.totalDisplay}
                </Table.Col>
                <Table.Col key={v4()}>
                  {node.financeInvoice.balanceDisplay}
                </Table.Col>
                <Table.Col className="text-right" key={v4()}>
                  <Button className='btn-sm' 
                          onClick={() => history.push("/finance/invoices/edit/" + node.financeInvoice.id)}
                          color="secondary">
                    {t('general.edit')}
                  </Button>
                </Table.Col>
                <Table.Col>
                  <AccountSubscriptionEditInvoiceDelete id={node.financeInvoice.id} />
                </Table.Col>
                {/* <Table.Col>
                  {moment(node.createdAt).format(dateTimeFormatMoment)}
                </Table.Col>
                <Table.Col>
                  <div dangerouslySetInnerHTML={{__html: node.description}} />
                </Table.Col>
                <Table.Col>
                  {node.mutationAmount}
                </Table.Col>
                <Table.Col>
                  <SubscriptionCreditsMutationType mutationType={node.mutationType} />
                </Table.Col>
                <Table.Col className="text-right">
                  <Link to={`/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/credits/edit/${node.id}`}>
                    <Button className='btn-sm' 
                            color="secondary">
                      {t('general.edit')}
                    </Button>
                  </Link>
                </Table.Col>
                <Table.Col className="text-right">
                  <AccountSubscriptionEditCreditDelete id={node.id} />
                </Table.Col> */}
              </Table.Row>
            ))}
        </Table.Body>
      </Table>
    </AccountSubscriptionEditListBase>
  )
}

export default withTranslation()(withRouter(AccountSubscriptionEditInvoices))
