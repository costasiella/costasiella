// @flow

import React, { useContext } from 'react'
import { useQuery, useMutation } from "react-apollo"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'

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

import AppSettingsContext from '../../context/AppSettingsContext'

import { get_list_query_variables } from "./tools"

// import FinancePaymentBatchCategory from "../../ui/FinancePaymentBatchCategory"
import BadgeFinancePaymentBatchStatus from "../../ui/BadgeFinancePaymentBatchStatus"
import ContentCard from "../../general/ContentCard"
import FinanceMenu from "../FinanceMenu"
import FinancePaymentBatchesBase from "./FinancePaymentBatchesBase"
import CSLS from "../../../tools/cs_local_storage"
import confirm_delete from "../../../tools/confirm_delete"

import { GET_PAYMENT_BATCHES_QUERY, DELETE_PAYMENT_BATCH } from "./queries"
import moment from 'moment'

function FinancePaymentBatches({t, history, match }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const batchType = match.params.batch_type

  const { loading, error, data, fetchMore, refetch } = useQuery(GET_PAYMENT_BATCHES_QUERY, {
    variables: get_list_query_variables(batchType),
  })
  const [deletePaymentBatch] = useMutation(DELETE_PAYMENT_BATCH)

  let cardTitle
  let msgEmptyList
  if (batchType == "collection") {
    cardTitle = t('finance.payment_batch_collections.title')
    msgEmptyList = t('finance.payment_batch_collections.empty_list')
  } else {
    cardTitle = t('finance.payment_batch_payments.title')
    msgEmptyList = t('finance.payment_batch_payments.empty_list')
  }

  // Loading
  if (loading) return (
    <FinancePaymentBatchesBase showAdd={true}>
      <ContentCard cardTitle={cardTitle}>
        <Dimmer active={true}
                loader={true}>
        </Dimmer>
      </ContentCard>
    </FinancePaymentBatchesBase>
  )
  // Error
  if (error) return (
    <FinancePaymentBatchesBase showAdd={true}>
      <ContentCard cardTitle={cardTitle}>
        <p>{t('finance.payment_batches.error_loading')}</p>
      </ContentCard>
      </FinancePaymentBatchesBase>
  )

  let financePaymentBatches = data.financePaymentBatches
  // Empty list
  if (!financePaymentBatches.edges.length) { return (
    <FinancePaymentBatchesBase showAdd={true}>
      <ContentCard cardTitle={cardTitle} >
        <p>{msgEmptyList}</p>
      </ContentCard>
    </FinancePaymentBatchesBase>
  )}

  return (
    <FinancePaymentBatchesBase showAdd={true}>
      <ContentCard cardTitle={cardTitle}
        pageInfo={financePaymentBatches.pageInfo}
        onLoadMore={() => {
        fetchMore({
          variables: {
            after: financePaymentBatches.pageInfo.endCursor
          },
          updateQuery: (previousResult, { fetchMoreResult }) => {
            const newEdges = fetchMoreResult.financePaymentBatches.edges
            const pageInfo = fetchMoreResult.financePaymentBatches.pageInfo

            return newEdges.length
              ? {
                  // Put the new payment_methods at the end of the list and update `pageInfo`
                  // so we have the new `endCursor` and `hasNextPage` values
                  financePaymentBatches: {
                    __typename: previousResult.financePaymentBatches.__typename,
                    edges: [ ...previousResult.financePaymentBatches.edges, ...newEdges ],
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
              <Table.ColHeader>{t('general.status')}</Table.ColHeader>
              <Table.ColHeader>{t('general.name')}</Table.ColHeader>
              <Table.ColHeader>{t('finance.payment_batches.execution_date')}</Table.ColHeader>
              <Table.ColHeader>{t('finance.payment_batches.batch_category')}</Table.ColHeader>             
              <Table.ColHeader></Table.ColHeader>
              <Table.ColHeader></Table.ColHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {financePaymentBatches.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col key={v4()}>
                  <BadgeFinancePaymentBatchStatus status={node.status} />
                </Table.Col>
                <Table.Col key={v4()}>
                  {node.name}
                </Table.Col>
                <Table.Col>
                  {moment(node.executionDate).format(dateFormat)}
                </Table.Col>
                <Table.Col>
                  {(node.financePaymentBatchCategory) ? node.financePaymentBatchCategory.name : t("general.invoices")}
                  {(node.year) ? <div><small className="text-muted">{node.year} - {node.month}</small></div> : ""}
                </Table.Col>
                <Table.Col>
                  <Link to={`/finance/paymentbatches/${batchType}/view/${node.id}`}>
                    <Button className='btn-sm' 
                            color="secondary">
                      {t('general.view')}
                    </Button>
                  </Link>
                </Table.Col>
                <Table.Col className="text-right" key={v4()}>
                  <button className="icon btn btn-link btn-sm" 
                    title={t('general.delete')} 
                    href=""
                    onClick={() => {
                      confirm_delete({
                        t: t,
                        msgConfirm: t("finance.payment_batches.delete_confirm_msg"),
                        msgDescription: <p>{node.name}</p>,
                        msgSuccess: t('finance.payment_batches.deleted'),
                        deleteFunction: deletePaymentBatch,
                        functionVariables: { variables: {
                          input: {
                            id: node.id
                          }
                        }, refetchQueries: [
                          {query: GET_PAYMENT_BATCHES_QUERY, variables: get_list_query_variables(batchType) } 
                        ]}
                      })
                  }}>
                    <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
                  </button>
                </Table.Col>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </ContentCard>
    </FinancePaymentBatchesBase>
  )
}

export default withTranslation()(withRouter(FinancePaymentBatches))