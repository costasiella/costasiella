// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
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

import { get_list_query_variables } from "./tools"

import FinancePaymentBatchCategory from "../../ui/FinancePaymentBatchCategory"
import ContentCard from "../../general/ContentCard"
import FinanceMenu from "../FinanceMenu"
import FinancePaymentBatchesBase from "./FinancePaymentBatchesBase"
import CSLS from "../../../tools/cs_local_storage"

import { GET_PAYMENT_BATCHES_QUERY, DELETE_PAYMENT_BATCH_CATEGORY } from "./queries"

function FinancePaymentBatches({t, history, match }) {
  const batchType = match.params.batch_type

  const { loading, error, data, fetchMore, refetch } = useQuery(GET_PAYMENT_BATCHES_QUERY, {
    variables: get_list_query_variables(batchType),
  })
  const [deletePaymentBatchCategory] = useMutation(DELETE_PAYMENT_BATCH_CATEGORY)

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
    <FinancePaymentBatchesBase>
      <ContentCard cardTitle={cardTitle}>
        <Dimmer active={true}
                loader={true}>
        </Dimmer>
      </ContentCard>
    </FinancePaymentBatchesBase>
  )
  // Error
  if (error) return (
    <FinancePaymentBatchesBase>
      <ContentCard cardTitle={cardTitle}>
        <p>{t('finance.payment_batches.error_loading')}</p>
      </ContentCard>
      </FinancePaymentBatchesBase>
  )

  let financePaymentBatches = data.financePaymentBatches
  // Empty list
  if (!financePaymentBatches.edges.length) { return (
    <FinancePaymentBatchesBase>
      <ContentCard cardTitle={cardTitle} >
        <p>{msgEmptyList}</p>
      </ContentCard>
    </FinancePaymentBatchesBase>
  )}

  return (
    <FinancePaymentBatchesBase>
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
              <Table.ColHeader>{t('general.name')}</Table.ColHeader>
              {/* <Table.ColHeader>{t('finance.payment_batch_categories.batch_category_type')}</Table.ColHeader> */}
              {/* <Table.ColHeader></Table.ColHeader>
              <Table.ColHeader></Table.ColHeader> */}
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {financePaymentBatches.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col key={v4()}>
                  {node.name}
                </Table.Col>
                {/* <Table.Col key={v4()}> */}
                  {/* <FinancePaymentBatchCategory categoryType={node.batchCategoryType} />
                </Table.Col>
                <Table.Col className="text-right">
                  <Link to={`/finance/paymentbatchcategories/edit/${node.id}`}>
                    <Button className='btn-sm' 
                            color="secondary">
                      {t('general.edit')}
                    </Button>
                  </Link>
                </Table.Col>
                <Table.Col className="text-right" key={v4()}>
                  <button className="icon btn btn-link btn-sm" 
                      title={t('general.archive')} 
                      onClick={() => {
                        console.log("clicked archived")
                        let id = node.id
                        archivePaymentBatchCategory({ variables: {
                          input: {
                          id,
                          archived: !node.archived
                        }
                      }, refetchQueries: [
                          {query: GET_PAYMENT_BATCH_CATEGORIES_QUERY, variables: get_list_query_variables()}
                      ]}).then(({ data }) => {
                        console.log('got data', data);
                        toast.success(
                          (node.archived) ? t('general.unarchived'): t('general.archived'), {
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
                </Table.Col> */}
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </ContentCard>
    </FinancePaymentBatchesBase>
  )
}

export default withTranslation()(withRouter(FinancePaymentBatches))