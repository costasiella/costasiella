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
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../general/ContentCard"
import FinanceMenu from "../FinanceMenu"

import { GET_GLACCOUNTS_QUERY } from "./queries"

const ARCHIVE_GLACCOUNT = gql`
  mutation ArchiveFinanceGLAccount($input: ArchiveFinanceGLAccountInput!) {
    archiveFinanceGlaccount(input: $input) {
      financeGlaccount {
        id
        archived
      }
    }
  }
`


const FinanceGLAccounts = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("finance.title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_GLACCOUNTS_QUERY} variables={{ archived }}>
             {({ loading, error, data: {financeGlaccounts: glaccounts}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('finance.glaccounts.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('finance.glaccounts.title')}>
                    <p>{t('finance.glaccounts.error_loading')}</p>
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
                if (!glaccounts.edges.length) { return (
                  <ContentCard cardTitle={t('finance.glaccounts.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('finance.glaccounts.empty_list') : t("finance.glaccounts.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('finance.glaccounts.title')}
                               headerContent={headerOptions}
                               pageInfo={glaccounts.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: glaccounts.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.financeGlaccounts.edges
                                    const pageInfo = fetchMoreResult.financeGlaccounts.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new glaccounts at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          financeGlaccounts: {
                                            __typename: previousResult.financeGlaccounts.__typename,
                                            edges: [ ...previousResult.financeGlaccounts.edges, ...newEdges ],
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
                              <Table.ColHeader>{t('finance.code')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {glaccounts.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {node.name}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {node.code}
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(node.archived) ? 
                                      <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/finance/glaccounts/edit/" + node.id)}
                                              color="secondary">
                                        {t('general.edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_GLACCOUNT} key={v4()}>
                                    {(archiveGlaccount, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('general.archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked archived")
                                             let id = node.id
                                             archiveGlaccount({ variables: {
                                               input: {
                                                id,
                                                archived: !archived
                                               }
                                        }, refetchQueries: [
                                            {query: GET_GLACCOUNTS_QUERY, variables: {"archived": archived }}
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
                                  resource="financeglaccount">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/finance/glaccounts/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('finance.glaccounts.add')}
              </Button>
            </HasPermissionWrapper>
            <FinanceMenu active_link='glaccounts'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(FinanceGLAccounts))