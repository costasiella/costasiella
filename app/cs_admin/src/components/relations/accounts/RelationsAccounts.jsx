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
import RelationsMenu from "../RelationsMenu"

import { GET_ACCOUNTS_QUERY } from "./queries"

const TRASH_ACCOUNT = gql`
  mutation ArchiveOrganizationDiscovery($input: ArchiveOrganizationDiscoveryInput!) {
    archiveOrganizationDiscovery(input: $input) {
      organizationDiscovery {
        id
        trashed
      }
    }
  }
`


const RelationsAccounts = ({ t, history, trashed=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("relations.title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_ACCOUNTS_QUERY} variables={{ trashed }}>
             {({ loading, error, data: {accounts: accounts}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('relations.accounts.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('relations.accounts.title')}>
                    <p>{t('relations.accounts.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  <Button color={(!trashed) ? 'primary': 'secondary'}  
                          size="sm"
                          onClick={() => {trashed=false; refetch({trashed});}}>
                    {t('general.current')}
                  </Button>
                  <Button color={(trashed) ? 'primary': 'secondary'} 
                          size="sm" 
                          className="ml-2" 
                          onClick={() => {trashed=true; refetch({trashed});}}>
                    {t('general.archive')}
                  </Button>
                </Card.Options>
                
                // Empty list
                if (!accounts.edges.length) { return (
                  <ContentCard cardTitle={t('relations.accounts.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!trashed) ? t('relations.accounts.empty_list') : t("relations.accounts.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('relations.accounts.title')}
                               headerContent={headerOptions}
                               pageInfo={accounts.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: accounts.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.accounts.edges
                                    const pageInfo = fetchMoreResult.accounts.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new accounts at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          accounts: {
                                            __typename: previousResult.accounts.__typename,
                                            edges: [ ...previousResult.accounts.edges, ...newEdges ],
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
                              <Table.ColHeader>{t('general.email')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {accounts.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {node.firstName} {node.lastName}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {node.email}
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(node.trashed) ? 
                                      <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/organization/accounts/edit/" + node.id)}
                                              color="secondary">
                                        {t('general.edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={TRASH_ACCOUNT} key={v4()}>
                                    {(archiveCostcenter, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('general.archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked trashed")
                                             let id = node.id
                                             archiveCostcenter({ variables: {
                                               input: {
                                                id,
                                                trashed: !trashed
                                               }
                                        }, refetchQueries: [
                                            {query: GET_ACCOUNTS_QUERY, variables: {"trashed": trashed }}
                                        ]}).then(({ data }) => {
                                          console.log('got data', data);
                                          toast.success(
                                            (trashed) ? t('general.untrashed'): t('general.trashed'), {
                                              position: toast.POSITION.BOTTOM_RIGHT
                                            })
                                        }).catch((error) => {
                                          toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                              position: toast.POSITION.BOTTOM_RIGHT
                                            })
                                          console.log('there was an error sending the query', error);
                                        })
                                        }}>
                                          <Icon prefix="fe" name="trash-2" />
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
                                  resource="account">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/accounts/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('relations.accounts.add')}
              </Button>
            </HasPermissionWrapper>
            <RelationsMenu active_link='accounts'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(RelationsAccounts))