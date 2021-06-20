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
import RelationsAccountsBase from "./RelationsAccountsBase"
import { GET_ACCOUNTS_QUERY } from "./queries"
import { get_list_query_variables } from "./tools"


const UPDATE_ACCOUNT_ACTIVE = gql`
  mutation UpdateAccountActive($input: UpdateAccountActiveInput!) {
    updateAccountActive(input: $input) {
      account {
        id
        isActive
      }
    }
  }
`


const DELETE_ACCOUNT = gql`
  mutation DeleteAccount($input: DeleteAccountInput!) {
    deleteAccount(input: $input) {
      ok
    }
  }
`


// Set some initial value for isActive, if not found
if (!localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE)) {
  localStorage.setItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE, true) 
} 


const confirm_delete = ({t, msgConfirm, msgDescription, msgSuccess, deleteFunction, functionVariables}) => {
  confirmAlert({
    customUI: ({ onClose }) => {
      return (
        <div className='custom-ui'>
          <h1>{t('general.confirm_delete')}</h1>
          {msgConfirm}
          {msgDescription}
          <button className="btn btn-link pull-right" onClick={onClose}>{t('general.confirm_delete_no')}</button>
          <button
            className="btn btn-danger"
            onClick={() => {
              deleteFunction(functionVariables)
                .then(({ data }) => {
                  console.log('got data', data);
                  toast.success(
                    msgSuccess, {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                }).catch((error) => {
                  toast.error((t('general.toast_server_error')) + ': ' +  error, {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                  console.log('there was an error sending the query', error);
                })
              onClose()
            }}
          >
            <Icon name="trash-2" /> {t('general.confirm_delete_yes')}
          </button>
        </div>
      )
    }
  })
}


const RelationsAccounts = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Query query={GET_ACCOUNTS_QUERY} variables={get_list_query_variables()} notifyOnNetworkStatusChange>
        {({ loading, error, data, refetch, fetchMore, variables}) => {
          // Loading
          if (loading && !data.accounts) return (
            <RelationsAccountsBase>
              <ContentCard cardTitle={t('relations.accounts.title')}>
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
                <ContentCard cardTitle={t('relations.accounts.title')}>
                  <p>{t('relations.accounts.error_loading')}</p>
                </ContentCard>
              </Container>
            </RelationsAccountsBase>
          )
          const headerOptions = <Card.Options>
            <Button color={(localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE) === "true") ? 'primary': 'secondary'}  
                    size="sm"
                    onClick={() => {
                      localStorage.setItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE, true)
                      refetch(get_list_query_variables())
                    }
            }>
              {t('general.active')}
            </Button>
            <Button color={(localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE) === "false") ? 'primary': 'secondary'} 
                    size="sm" 
                    className="ml-2" 
                    onClick={() => {
                      localStorage.setItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE, false)
                      refetch(get_list_query_variables())
                    }
            }>
              {t('general.deleted')}
            </Button>
          </Card.Options>

          let accounts = data.accounts
          
          // Empty list
          if (!accounts.edges.length) { return (
            <RelationsAccountsBase refetch={refetch}>
              <ContentCard cardTitle={t('relations.accounts.title')}
                            headerContent={headerOptions}>
                <p>
                  {(localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE) === "true") ? t('relations.accounts.empty_list') : t("relations.accounts.empty_archive")}
                </p>
              </ContentCard>
            </RelationsAccountsBase>
          )} else {   
          // Life's good! :)
          return (
            <RelationsAccountsBase refetch={refetch}>
              {console.log('query vars:')}
              {console.log(variables)}
              <ContentCard cardTitle={t('relations.accounts.title')}
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
                      <Table.ColHeader>{t('general.info')}</Table.ColHeader>
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
                                    if (localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE) == "true") {
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
                                    (isActive) ? t('relations.accounts.deactivated'): t('relations.accounts.restored'), {
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
                                          msgConfirm: t("relations.accounts.delete_confirm_msg"),
                                          msgDescription: <p>{node.first_name} {node.last_name}</p>,
                                          msgSuccess: t('relations.accounts.deleted'),
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

export default withTranslation()(withRouter(RelationsAccounts))