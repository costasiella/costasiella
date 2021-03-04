// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Badge,
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
import { confirmAlert } from 'react-confirm-alert'
import { toast } from 'react-toastify'

import CSLS from "../../../tools/cs_local_storage"

import ContentCard from "../../general/ContentCard"
import RelationsAccountsBase from "./RelationsB2BBase"
import { GET_ACCOUNTS_QUERY } from "./queries"
import { get_list_query_variables } from "./tools"
import confirm_archive from "../../../tools/confirm_archive"
import confirm_unarchive from "../../../tools/confirm_unarchive"
import confirm_delete from "../../../tools/confirm_delete"


const UPDATE_BUSINESS_ARCHIVE = gql`
  mutation UpdateBusinessArchived($input: UpdateBusinessInput!) {
    updateBusiness(input: $input) {
      business {
        id
        archived
      }
    }
  }
`


const DELETE_BUSINESS = gql`
  mutation DeleteBusiness($input: DeleteBusinessInput!) {
    deleteBusiness(input: $input) {
      ok
    }
  }
`


// Set some initial value for isActive, if not found
if (!localStorage.getItem(CSLS.RELATIONS_BUSINESSES_SHOW_ARCHIVE)) {
  localStorage.setItem(CSLS.RELATIONS_BUSINESSES_SHOW_ARCHIVE, true) 
} 


const RelationsB2B = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Query query={GET_ACCOUNTS_QUERY} variables={get_list_query_variables()} notifyOnNetworkStatusChange>
        {({ loading, error, data, refetch, fetchMore, variables}) => {
          // Loading
          if (loading) return (
            <RelationsAccountsBase refetch={refetch}>
              <ContentCard cardTitle={t('relations.b2b.title')}>
                <Dimmer active={true}
                        loader={true}>
                </Dimmer>
              </ContentCard>
            </RelationsAccountsBase>
          )
          // Error
          if (error) return (
            <RelationsAccountsBase>
              <Container>
                <ContentCard cardTitle={t('relations.b2b.title')}>
                  <p>{t('relations.b2b.error_loading')}</p>
                </ContentCard>
              </Container>
            </RelationsAccountsBase>
          )
          const headerOptions = <Card.Options>
            <Button color={(localStorage.getItem(CSLS.RELATIONS_BUSINESSES_SHOW_ARCHIVE) === "true") ? 'primary': 'secondary'}  
                    size="sm"
                    onClick={() => {
                      localStorage.setItem(CSLS.RELATIONS_BUSINESSES_SHOW_ARCHIVE, true)
                      refetch(get_list_query_variables())
                    }
            }>
              {t('general.active')}
            </Button>
            <Button color={(localStorage.getItem(CSLS.RELATIONS_BUSINESSES_SHOW_ARCHIVE) === "false") ? 'primary': 'secondary'} 
                    size="sm" 
                    className="ml-2" 
                    onClick={() => {
                      localStorage.setItem(CSLS.RELATIONS_BUSINESSES_SHOW_ARCHIVE, false)
                      refetch(get_list_query_variables())
                    }
            }>
              {t('general.deleted')}
            </Button>
          </Card.Options>
          
          // Empty list
          if (!data.accounts.edges.length) { return (
            <RelationsAccountsBase refetch={refetch}>
              <ContentCard cardTitle={t('relations.b2b.title')}
                            headerContent={headerOptions}>
                <p>
                  {(localStorage.getItem(CSLS.RELATIONS_BUSINESSES_SHOW_ARCHIVE) === "true") ? t('relations.b2b.empty_list') : t("relations.b2b.empty_archive")}
                </p>
              </ContentCard>
            </RelationsAccountsBase>
          )} else {   
          // Life's good! :)
          return (
            <RelationsAccountsBase refetch={refetch}>
              {console.log('query vars:')}
              {console.log(variables)}
              <ContentCard cardTitle={t('relations.b2b.title')}
                           headerContent={headerOptions}
                           pageInfo={data.accounts.pageInfo}
                           onLoadMore={() => {
                             fetchMore({
                               variables: {
                                 after: data.accounts.pageInfo.endCursor
                               },
                               updateQuery: (previousResult, { fetchMoreResult }) => {
                                 const newEdges = fetchMoreResult.accounts.edges
                                 const pageInfo = fetchMoreResult.accounts.pageInfo 

                                 return newEdges.length
                                   ? {
                                       // Put the new accounts at the end of the list and update `pageInfo`
                                       // so we have the new `endCursor` and `hasNextPage` values
                                      data: {
                                        accounts: {
                                          __typename: previousResult.accounts.__typename,
                                          edges: [ ...previousResult.accounts.edges, ...newEdges ],
                                          pageInfo
                                        }
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
                      <Table.ColHeader>{t('general.info')}</Table.ColHeader>
                    </Table.Row>
                  </Table.Header>
                  <Table.Body>
                      {data.accounts.edges.map(({ node }) => (
                        <Table.Row key={v4()}>
                          <Table.Col key={v4()}>
                            {node.firstName} {node.lastName}
                          </Table.Col>
                          <Table.Col key={v4()}>
                            {node.email}
                          </Table.Col>
                          <Table.Col key={v4()}>
                            {/* {console.log(node)} */}
                            {(node.customer) ? <span>
                                <Badge color="primary" className="mb-1">{t("general.customer")}</Badge> <br />
                              </span> : null}
                            {(node.teacher) ? <span>
                                <Badge color="info" className="mb-1">{t("general.teacher")}</Badge> <br />
                              </span> : null}
                            {(node.employee) ? <span>
                                <Badge color="secondary" className="mb-1">{t("general.employee")}</Badge> <br />
                              </span> : null}
                          </Table.Col>
                          <Table.Col className="text-right" key={v4()}>
                            {(!node.isActive) ? 
                              <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                              <Button className='btn-sm' 
                                      onClick={() => history.push("/relations/accounts/" + node.id + "/profile")}
                                      color="secondary">
                                {t('general.edit')}
                              </Button>
                            }
                          </Table.Col>
                          <Mutation mutation={UPDATE_ACCOUNT_ACTIVE} key={v4()}>
                            {(updateAccountActive, { data }) => (
                              <Table.Col className="text-right" key={v4()}>
                                <button className="icon btn btn-link btn-sm" 
                                  title={t('general.deactivate')} 
                                  href=""
                                  onClick={() => {
                                    console.log("clicked isActive")
                                    let id = node.id
                                    let isActive 
                                    if (localStorage.getItem(CSLS.RELATIONS_BUSINESSES_SHOW_ARCHIVE) == "true") {
                                      isActive = true
                                    } else {
                                      isActive = false
                                    }

                                    updateAccountActive({ variables: {
                                      input: {
                                        id,
                                        isActive: !isActive // invert, as we need the opposite from the list currently displayed
                                      }
                                }, refetchQueries: [
                                    {query: GET_ACCOUNTS_QUERY, variables: get_list_query_variables()}
                                ]}).then(({ data }) => {
                                  console.log('got data', data);
                                  toast.success(
                                    (isActive) ? t('relations.b2b.deactivated'): t('relations.b2b.restored'), {
                                      position: toast.POSITION.BOTTOM_RIGHT
                                    })
                                }).catch((error) => {
                                  toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                      position: toast.POSITION.BOTTOM_RIGHT
                                    })
                                  console.log('there was an error sending the query', error);
                                })
                                }}>
                                  {
                                    (node.isActive) ?
                                      <Icon prefix="fe" name="trash-2" /> :
                                      t("general.restore")
                                  }
                                </button>
                              </Table.Col>
                            )}
                          </Mutation>
                          {
                            (node.isActive) ? '' :
                              <Mutation mutation={DELETE_ACCOUNT} key={v4()}>
                                {(deleteAccount, { data }) => (
                                  <Table.Col className="text-right" key={v4()}>
                                    <button className="icon btn btn-link btn-sm" 
                                      title={t('general.delete')} 
                                      href=""
                                      onClick={() => {
                                        confirm_delete({
                                          t: t,
                                          msgConfirm: t("relations.b2b.delete_confirm_msg"),
                                          msgDescription: <p>{node.first_name} {node.last_name}</p>,
                                          msgSuccess: t('relations.b2b.deleted'),
                                          deleteFunction: deleteAccount,
                                          functionVariables: { variables: {
                                            input: {
                                              id: node.id
                                            }
                                          }, refetchQueries: [
                                            {query: GET_ACCOUNTS_QUERY, variables: get_list_query_variables()}
                                          ]}
                                        })
                                    }}>
                                      <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
                                    </button>
                                  </Table.Col>
                                )}
                              </Mutation>
                          }
                        </Table.Row>
                      ))}
                  </Table.Body>
                </Table>
              </ContentCard>
            </RelationsAccountsBase>
          )}}
        }
      </Query>
    </div>
  </SiteWrapper>
)

export default withTranslation()(withRouter(RelationsB2B))