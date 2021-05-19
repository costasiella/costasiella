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
  Badge,
  Button,
  Card,
  Container,
  Table, 
  Text
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import { get_list_query_variables } from "./tools"
import ContentCard from "../../general/ContentCard"
import FinanceMenu from "../FinanceMenu"
import FinanceInvoicesFilter from "./FinanceInvoicesFilter"
import FinanceInvoicesBase from "./FinanceInvoicesBase"
import FinanceInvoicesStatus from "../../ui/FinanceInvoiceStatus"

import { GET_INVOICES_QUERY, DELETE_FINANCE_INVOICE } from "./queries"

import CSLS from "../../../tools/cs_local_storage"
import confirm_delete from "../../../tools/confirm_delete"
import moment from 'moment'


function FinanceInvoices({ t, location, history }) {
  // Set back location for edit invoice
  localStorage.setItem(CSLS.FINANCE_INVOICES_EDIT_RETURN, location.pathname)

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("finance.title")}>
            <div className="page-options d-flex">
              <Link to="/finance/invoices/groups" 
                    className='btn btn-outline-secondary btn-sm'>
                <Icon prefix="fe" name="folder" /> {t('general.groups')}
              </Link>
            </div>
          </Page.Header>
              <Query query={GET_INVOICES_QUERY} variables={get_list_query_variables()} fetchPolicy="network-only">
              {({ loading, error, data: {financeInvoices: invoices}, refetch, fetchMore }) => {
                  // Loading
                  if (loading) return (
                    <FinanceInvoicesBase refetch={refetch}>
                      <ContentCard cardTitle={t('finance.invoices.title')}>
                        <Dimmer active={true}
                                loader={true}>
                        </Dimmer>
                      </ContentCard>
                    </FinanceInvoicesBase>
                  )
                  // Error
                  if (error) return (
                    <FinanceInvoicesBase refetch={refetch}>
                      <ContentCard cardTitle={t('finance.invoices.title')}>
                        <p>{t('finance.invoices.error_loading')}</p>
                      </ContentCard>
                    </FinanceInvoicesBase>
                  )
                  
                  // Empty list
                  if (!invoices.edges.length) { return (
                    <FinanceInvoicesBase refetch={refetch}>
                      <ContentCard cardTitle={t('finance.invoices.title')}>
                        <p>
                          {t('finance.invoices.empty_list')}
                        </p>
                      </ContentCard>
                    </FinanceInvoicesBase>
                  )} else {   
                  // Life's good! :)
                  return (
                    <FinanceInvoicesBase refetch={refetch}>
                      <ContentCard cardTitle={t('finance.invoices.title')}
                                  pageInfo={invoices.pageInfo}
                                  onLoadMore={() => {
                                    fetchMore({
                                      variables: {
                                        after: invoices.pageInfo.endCursor
                                      },
                                      updateQuery: (previousResult, { fetchMoreResult }) => {
                                        const newEdges = fetchMoreResult.financeInvoices.edges
                                        const pageInfo = fetchMoreResult.financeInvoices.pageInfo

                                        return newEdges.length
                                          ? {
                                              // Put the new invoices at the end of the list and update `pageInfo`
                                              // so we have the new `endCursor` and `hasNextPage` values
                                              financeInvoices: {
                                                __typename: previousResult.financeInvoices.__typename,
                                                edges: [ ...previousResult.financeInvoices.edges, ...newEdges ],
                                                pageInfo
                                              }
                                            }
                                          : previousResult
                                      }
                                    })
                                  }} 
                        >
                        <Table>
                          <Table.Header>
                            <Table.Row key={v4()}>
                              <Table.ColHeader>{t('general.status')}</Table.ColHeader>
                              <Table.ColHeader>{t('finance.invoices.invoice_number')}</Table.ColHeader>
                              <Table.ColHeader>{t('finance.invoices.relation')} & {t('finance.invoices.summary')}</Table.ColHeader>
                              <Table.ColHeader>{t('finance.invoices.date')} & {t('finance.invoices.due')}</Table.ColHeader>
                              {/* <Table.ColHeader>{t('finance.invoices.due')}</Table.ColHeader> */}
                              <Table.ColHeader>{t('general.total')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.balance')}</Table.ColHeader>
                              <Table.ColHeader></Table.ColHeader>
                              <Table.ColHeader></Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {invoices.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    <FinanceInvoicesStatus status={node.status} />
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    <Link to={"/finance/invoices/edit/" + node.id}>
                                      {node.invoiceNumber}
                                    </Link>
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
                                    <Link to={"/finance/invoices/edit/" + node.id}>
                                      <Button className='btn-sm' 
                                              color="secondary">
                                        {t('general.edit')}
                                      </Button>
                                    </Link>
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
                                </Mutation>
                                </Table.Row>
                              ))}
                          </Table.Body>
                        </Table>
                      </ContentCard>
                    </FinanceInvoicesBase>
                  )}}
                }
              </Query>
        </Container>
      </div>
    </SiteWrapper>
  )
} 

export default withTranslation()(withRouter(FinanceInvoices))