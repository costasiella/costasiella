// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
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
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import BadgeBoolean from "../../../ui/BadgeBoolean"
import RelationsAccountsBack from "../RelationsAccountsBack"
import confirm_delete from "../../../../tools/confirm_delete"

import ContentCard from "../../../general/ContentCard"
import ProfileMenu from "../ProfileMenu"
import ProfileCardSmall from "../../../ui/ProfileCardSmall"
import AccountFinancePaymentBatchCategoryItemsBase from "./AccountFinancePaymentBatchCategoryItemsBase"

import { GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEMS_QUERY } from "./queries"

const DELETE_ACCOUNT_CLASSPASS = gql`
  mutation DeleteAccountClasspass($input: DeleteAccountClasspassInput!) {
    deleteAccountClasspass(input: $input) {
      ok
    }
  }
`

function AccountFinancePaymentBatchCategoryItems({ t, history, match }) {
  const accountId = match.params.account_id

  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEMS_QUERY, {
    variables: { account: accountId }
  })

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
              <Table.ColHeader>{t('general.category')}</Table.ColHeader>
              <Table.ColHeader></Table.ColHeader> 
            </Table.Row>
          </Table.Header>
          <Table.Body>
              {batchCategoryItems.edges.map(({ node }) => (
                <Table.Row key={v4()}>
                  <Table.Col key={v4()}>
                    {node.financePaymentBatchCategory.name}
                  </Table.Col>
                  {/* <Table.Col key={v4()}>
                    {node.dateStart}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.dateEnd}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.classesRemainingDisplay}
                  </Table.Col>
                  <Table.Col className="text-right" key={v4()}>
                    <Link to={"/relations/accounts/" + match.params.account_id + "/classpasses/edit/" + node.id}>
                      <Button className='btn-sm' 
                              color="secondary">
                        {t('general.edit')}
                      </Button>
                    </Link>
                  </Table.Col>
                  <Mutation mutation={DELETE_ACCOUNT_CLASSPASS} key={v4()}>
                    {(deleteAccountClasspass, { data }) => (
                      <Table.Col className="text-right" key={v4()}>
                        <button className="icon btn btn-link btn-sm" 
                          title={t('general.delete')} 
                          href=""
                          onClick={() => {
                            confirm_delete({
                              t: t,
                              msgConfirm: t("relations.account.classpasses.delete_confirm_msg"),
                              msgDescription: <p>{node.organizationClasspass.name} {node.dateStart}</p>,
                              msgSuccess: t('relations.account.classpasses.deleted'),
                              deleteFunction: deleteAccountClasspass,
                              functionVariables: { variables: {
                                input: {
                                  id: node.id
                                }
                              }, refetchQueries: [
                                {query: GET_ACCOUNT_CLASSPASSES_QUERY, variables: { archived: archived, accountId: match.params.account_id }} 
                              ]}
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
      </ContentCard>
    </AccountFinancePaymentBatchCategoryItemsBase>
  )
}
      
        
export default withTranslation()(withRouter(AccountFinancePaymentBatchCategoryItems))
