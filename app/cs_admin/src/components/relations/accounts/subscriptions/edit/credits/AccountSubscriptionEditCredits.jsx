// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'

import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_CREDITS_QUERY } from './queries'

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


function AccountSubscriptionEditCredits({t, match, history}) {
  const id = match.params.subscription_id
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions`
  const activeTab = "credits"

  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_SUBSCRIPTION_CREDITS_QUERY, {
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

  const accountSubscriptionCredits = data.accountSubscriptionCredits
  const pageInfo = data.accountSubscriptionCredits.pageInfo
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
        after: accountSubscriptionCredits.pageInfo.endCursor
      },
      updateQuery: (previousResult, { fetchMoreResult }) => {
        const newEdges = fetchMoreResult.accountSubscriptionCredits.edges
        const pageInfo = fetchMoreResult.accountSubscriptionCredits.pageInfo

        return newEdges.length
          ? {
              // Put the new invoices at the end of the list and update `pageInfo`
              // so we have the new `endCursor` and `hasNextPage` values
              accountSubscriptionCredits: {
                __typename: previousResult.accountSubscriptionCredits.__typename,
                edges: [ ...previousResult.accountSubscriptionCredits.edges, ...newEdges ],
                pageInfo
              }
            }
          : previousResult
      }
    })
  }

  return (
    <AccountSubscriptionEditListBase active_tab={activeTab} pageInfo={pageInfo} onLoadMore={onLoadMore}>
      <h5>{t('relations.account.subscriptions.credits.title_list')}</h5>
      <Table>
        <Table.Header>
          <Table.Row key={v4()}>
            {/* <Table.ColHeader>{t('general.status')}</Table.ColHeader>
            <Table.ColHeader>{t('finance.invoices.invoice_number')}</Table.ColHeader>
            <Table.ColHeader>{t('finance.invoices.relation')} & {t('finance.invoices.summary')}</Table.ColHeader>
            <Table.ColHeader>{t('finance.invoices.date')} & {t('finance.invoices.due')}</Table.ColHeader>
            <Table.ColHeader>{t('general.total')}</Table.ColHeader>
            <Table.ColHeader>{t('general.balance')}</Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
            <Table.ColHeader></Table.ColHeader> */}
          </Table.Row>
        </Table.Header>
        <Table.Body>
            {accountSubscriptionCredits.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col>
                  {node.id}
                </Table.Col>
                {/* <Table.Col key={v4()}>
                  <FinanceInvoicesStatus status={node.status} />
                </Table.Col>
                <Table.Col key={v4()}>
                  {node.invoiceNumber}
                </Table.Col>
                <Table.Col key={v4()}>
                  {(node.account) ? 
                    <Link to={"/relations/accounts/" + node.account.id + "/profile"}>
                      {(node.relationCompany) ? node.relationCompany: node.relationContactName}
                    </Link> :
                    (node.relationCompany) ? node.relationCompany: node.relationContactName
                  }
                    <br />
                  <Text.Small color="gray">{node.summary.trunc(20)}</Text.Small>
                </Table.Col>
                <Table.Col key={v4()}>
                  {moment(node.dateSent).format('LL')} <br />
                  {moment(node.dateDue).format('LL')}
                </Table.Col>
                <Table.Col key={v4()}>
                  {node.totalDisplay}
                </Table.Col>
                <Table.Col key={v4()}>
                  {node.balanceDisplay}
                </Table.Col>
                <Table.Col className="text-right" key={v4()}>
                  <Button className='btn-sm' 
                          onClick={() => history.push("/finance/invoices/edit/" + node.id)}
                          color="secondary">
                    {t('general.edit')}
                  </Button>
                </Table.Col>
                <Mutation mutation={DELETE_FINANCE_INVOICE} key={v4()}>
                  {(deleteFinanceInvoice, { data }) => (
                    <Table.Col className="text-right" key={v4()}>
                      <button className="icon btn btn-link btn-sm" 
                        title={t('general.delete')} 
                        href=""
                        onClick={() => {
                          confirm_delete({
                            t: t,
                            msgConfirm: t("finance.invoices.delete_confirm_msg"),
                            msgDescription: <p>{node.invoiceNumber}</p>,
                            msgSuccess: t('finance.invoices.deleted'),
                            deleteFunction: deleteFinanceInvoice,
                            functionVariables: { 
                              variables: {
                                input: {
                                  id: node.id
                                }
                              }, 
                              refetchQueries: [
                                {query: GET_INVOICES_QUERY, variables: get_list_query_variables() } 
                              ]
                            }
                          })
                      }}>
                        <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
                      </button>
                    </Table.Col>
                  )}
                </Mutation> */}
              </Table.Row>
            ))}
        </Table.Body>
      </Table>
    </AccountSubscriptionEditListBase>
  )
}

export default withTranslation()(withRouter(AccountSubscriptionEditCredits))
