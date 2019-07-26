// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


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

import { GET_INVOICES_QUERY } from "./queries"

import moment from 'moment'

const ARCHIVE_INVOICE = gql`
  mutation ArchiveFinanceCostCenter($input: ArchiveFinanceCostCenterInput!) {
    archiveFinanceCostcenter(input: $input) {
      financeCostcenter {
        id
        archived
      }
    }
  }
`


const FinanceInvoices = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("finance.title")} />
            <Query query={GET_INVOICES_QUERY} variables={get_list_query_variables()}>
             {({ loading, error, data: {financeInvoices: invoices}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('finance.invoices.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('finance.invoices.title')}>
                    <p>{t('finance.invoices.error_loading')}</p>
                  </ContentCard>
                )
                
                // Empty list
                if (!invoices.edges.length) { return (
                  <ContentCard cardTitle={t('finance.invoices.title')}>
                    <p>
                      {t('finance.invoices.empty_list')}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <Grid.Row>
                    <Grid.Col md={9}>
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
                                    {node.status}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {node.invoiceNumber}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {(node.relationCompany) ? node.relationCompany: node.relationContactName} <br />
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
                                  {/* <Mutation mutation={ARCHIVE_INVOICE} key={v4()}>
                                    {(archiveCostcenter, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                            title={t('general.archive')} 
                                            href=""
                                            onClick={() => {
                                              console.log("clicked archived")
                                              let id = node.id
                                              archiveCostcenter({ variables: {
                                                input: {
                                                id,
                                                archived: !archived
                                                }
                                        }, refetchQueries: [
                                            {query: GET_INVOICES_QUERY, variables: {"archived": archived }}
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
                                  </Mutation> */}
                                </Table.Row>
                              ))}
                          </Table.Body>
                        </Table>
                      </ContentCard>
                     </Grid.Col>
                    <Grid.Col md={3}>
                      <h5 className="mt-2 pt-1">{t("general.filter")}</h5>
                      <FinanceInvoicesFilter refetch={refetch}/>
                      <h5>{t("general.menu")}</h5>
                      <FinanceMenu active_link='invoices'/>
                    </Grid.Col>
                  </Grid.Row>
                )}}
               }
            </Query>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(FinanceInvoices))