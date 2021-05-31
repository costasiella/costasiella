// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Button,
  Icon,
  Table
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import confirm_delete from "../../../../tools/confirm_delete"

import ContentCard from "../../../general/ContentCard"
import AccountFinancePaymentBatchCategoryItemsBase from "./AccountFinancePaymentBatchCategoryItemsBase"

import { 
  GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEMS_QUERY,
  DELETE_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM
} from "./queries"



function AccountFinancePaymentBatchCategoryItems({ t, history, match }) {
  const accountId = match.params.account_id

  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEMS_QUERY, {
    variables: { account: accountId }
  })
  const [deleteAccountFinancePaymentBatchCategoryItem] = useMutation(DELETE_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM)

  if (loading) return (
    <AccountFinancePaymentBatchCategoryItemsBase>
      <p>{t('general.loading_with_dots')}</p>
    </AccountFinancePaymentBatchCategoryItemsBase>
  )
  // Error
  if (error) {
    console.log(error)
    return (
      <AccountFinancePaymentBatchCategoryItemsBase>
        <p>{t('general.error_sad_smiley')}</p>
      </AccountFinancePaymentBatchCategoryItemsBase>
    )
  }

  let batchCategoryItems = data.accountFinancePaymentBatchCategoryItems

  return (
    <AccountFinancePaymentBatchCategoryItemsBase>
      <ContentCard 
        cardTitle={t('relations.account.finance_payment_batch_category_items.title')}
        hasCardBody={false}
        pageInfo={batchCategoryItems.pageInfo}
        onLoadMore={() => {
          fetchMore({
            variables: {
              after: batchCategoryItems.pageInfo.endCursor
            },
            updateQuery: (previousResult, { fetchMoreResult }) => {
              const newEdges = fetchMoreResult.accountFinancePaymentBatchCategoryItems.edges
              const pageInfo = fetchMoreResult.accountFinancePaymentBatchCategoryItems.pageInfo

              return newEdges.length
                ? {
                    // Put the new accountClasspasses at the end of the list and update `pageInfo`
                    // so we have the new `endCursor` and `hasNextPage` values
                    batchCategoryItems: {
                      __typename: previousResult.accountFinancePaymentBatchCategoryItems.__typename,
                      edges: [ ...previousResult.accountFinancePaymentBatchCategoryItems.edges, ...newEdges ],
                      pageInfo
                    }
                  }
                : previousResult
            }
          })
        }} 
      >
        <Table cards>
          <Table.Header>
            <Table.Row key={v4()}>
              <Table.ColHeader>{t('general.year')}</Table.ColHeader>
              <Table.ColHeader>{t('general.month')}</Table.ColHeader>
              <Table.ColHeader>{t('general.amount')}</Table.ColHeader>
              <Table.ColHeader>{t('general.category')}</Table.ColHeader>
              <Table.ColHeader>{t('general.description')}</Table.ColHeader>
              <Table.ColHeader></Table.ColHeader> 
              <Table.ColHeader></Table.ColHeader> 
            </Table.Row>
          </Table.Header>
          <Table.Body>
              {batchCategoryItems.edges.map(({ node }) => (
                <Table.Row key={v4()}>
                  <Table.Col key={v4()}>
                    {node.year}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.month}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.amountDisplay}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.financePaymentBatchCategory.name}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.description.replace(/(.{28})..+/, "$1...")}
                  </Table.Col>
                  <Table.Col className="text-right" key={v4()}>
                    <Link to={`/relations/accounts/${match.params.account_id}/finance_payment_batch_category_items/edit/${node.id}`}>
                      <Button className='btn-sm' 
                              color="secondary">
                        {t('general.edit')}
                      </Button>
                    </Link>
                  </Table.Col>
                  <Table.Col>
                    <button 
                      className="icon btn btn-link btn-sm" 
                      title={t('general.delete')} 
                      href=""
                      onClick={() => {
                        confirm_delete({
                          t: t,
                          msgConfirm: t("relations.account.finance_payment_batch_category_items.delete_confirm_msg"),
                          msgDescription: <p><br />{node.financePaymentBatchCategory.name} {node.amountDisplay} <br/>{node.description}</p>,
                          msgSuccess: t('relations.account.finance_payment_batch_category_items.deleted'),
                          deleteFunction: deleteAccountFinancePaymentBatchCategoryItem,
                          functionVariables: { variables: {
                            input: {
                              id: node.id
                            }
                          }, refetchQueries: [
                            {query: GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEMS_QUERY, variables: { 
                              account: accountId
                            }} 
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
    </AccountFinancePaymentBatchCategoryItemsBase>
  )
}
      
        
export default withTranslation()(withRouter(AccountFinancePaymentBatchCategoryItems))
