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
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import BadgeBoolean from "../../../ui/BadgeBoolean"
import ContentCard from "../../../general/ContentCard"
import FinanceMenu from "../../FinanceMenu"

import { GET_INVOICE_GROUPS_QUERY } from "./queries"

const ARCHIVE_INVOICE_GROUP = gql`
  mutation ArchiveFinanceInvoiceGroup($input: ArchiveFinanceInvoiceGroupInput!) {
    archiveFinanceInvoiceGroup(input: $input) {
      financeInvoiceGroup {
        id
        archived
      }
    }
  }
`


const FinanceInvoiceGroups = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("finance.title")}>
          <div className="page-options d-flex">
            <Link to="/finance/invoices" 
                  className='btn btn-outline-secondary btn-sm mr-2'>
                <Icon prefix="fe" name="arrow-left" /> {t('general.back_to')} {t('finance.invoices.title')}
            </Link>
            <Link to="/finance/invoices/groups/defaults" 
                  className='btn btn-outline-secondary btn-sm'>
                <Icon prefix="fe" name="settings" /> {t('finance.invoice_groups_defaults.title')}
            </Link> 
          </div>
        </Page.Header>
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_INVOICE_GROUPS_QUERY} variables={{ archived }}>
             {({ loading, error, data: {financeInvoiceGroups: invoice_groups}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('finance.invoice_groups.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('finance.invoice_groups.title')}>
                    <p>{t('finance.invoice_groups.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  <Button color={(!archived) ? 'primary': 'secondary'}  
                          size="sm"
                          onClick={() => {archived=false; refetch({archived});}}>
                    {t('general.current')}
                  </Button>
                  <Button color={(archived) ? 'primary': 'secondary'} 
                          size="sm" 
                          className="ml-2" 
                          onClick={() => {archived=true; refetch({archived});}}>
                    {t('general.archive')}
                  </Button>
                </Card.Options>
                
                // Empty list
                if (!invoice_groups.edges.length) { return (
                  <ContentCard cardTitle={t('finance.invoice_groups.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('finance.invoice_groups.empty_list') : t("finance.invoice_groups.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('finance.invoice_groups.title')}
                               headerContent={headerOptions}
                               pageInfo={invoice_groups.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: invoice_groups.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.financeInvoiceGroups.edges
                                    const pageInfo = fetchMoreResult.financeInvoiceGroups.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new invoice_groups at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          financeInvoiceGroups: {
                                            __typename: previousResult.financeInvoiceGroups.__typename,
                                            edges: [ ...previousResult.financeInvoiceGroups.edges, ...newEdges ],
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
                          <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                          <Table.ColHeader>{t('finance.invoice_groups.next_id')}</Table.ColHeader>
                          <Table.ColHeader>{t('finance.invoice_groups.due_after_days')}</Table.ColHeader>
                          <Table.ColHeader>{t('general.prefix')}</Table.ColHeader>
                          <Table.ColHeader>{t('general.public')}</Table.ColHeader>
                          <Table.ColHeader>{t('finance.code')}</Table.ColHeader>
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                          {invoice_groups.edges.map(({ node }) => (
                            <Table.Row key={v4()}>
                              <Table.Col key={v4()}>
                                {node.name}
                              </Table.Col>
                              <Table.Col key={v4()}>
                                {node.nextId}
                              </Table.Col>
                              <Table.Col key={v4()}>
                                {node.dueAfterDays}
                              </Table.Col>
                              <Table.Col key={v4()}>
                                {node.prefix} 
                                {(node.prefixYear) ? <span>[{t('general.year')}]<br /></span>: ''}
                                {(node.autoResetPrefixYear) ? <Text.Small color="gray">
                                  {t('finance.invoice_groups.auto_reset_prefix_year')}
                                </Text.Small>: ''}
                              </Table.Col>
                              <Table.Col key={v4()}>
                                <BadgeBoolean value={node.displayPublic} />
                              </Table.Col>
                              <Table.Col key={v4()}>
                                {node.code}
                              </Table.Col>
                              <Table.Col className="text-right" key={v4()}>
                                {(node.archived) ? 
                                  <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                  <Button className='btn-sm' 
                                          onClick={() => history.push("/finance/invoices/groups/edit/" + node.id)}
                                          color="secondary">
                                    {t('general.edit')}
                                  </Button>
                                }
                              </Table.Col>
                              <Mutation mutation={ARCHIVE_INVOICE_GROUP} key={v4()}>
                                {(archiveInvoiceGroup, { data }) => (
                                  <Table.Col className="text-right" key={v4()}>
                                    <button className="icon btn btn-link btn-sm" 
                                        title={t('general.archive')} 
                                        href=""
                                        onClick={() => {
                                          console.log("clicked archived")
                                          let id = node.id
                                          archiveInvoiceGroup({ variables: {
                                            input: {
                                            id,
                                            archived: !archived
                                            }
                                    }, refetchQueries: [
                                        {query: GET_INVOICE_GROUPS_QUERY, variables: {"archived": archived }}
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
                              </Mutation>
                            </Table.Row>
                          ))}
                      </Table.Body>
                    </Table>
                  </ContentCard>
                )}}
             }
            </Query>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="financeinvoicegroup">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/finance/invoices/groups/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('finance.invoice_groups.add')}
              </Button>
            </HasPermissionWrapper>
            <FinanceMenu active_link='invoices'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(FinanceInvoiceGroups))