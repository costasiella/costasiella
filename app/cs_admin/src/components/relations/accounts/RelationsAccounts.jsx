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

import ContentCard from "../../general/ContentCard"
import InputSearch from "../../general/InputSearch"
import RelationsMenu from "../RelationsMenu"
import CSLS from "../../../tools/cs_local_storage"

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
      <Query query={GET_ACCOUNTS_QUERY} variables={get_list_query_variables()}>
        {({ loading, error, data, refetch, fetchMore }) => {
          // Loading
          if (loading) return (
            <ContentCard cardTitle={t('relations.accounts.title')}>
              <Dimmer active={true}
                      loader={true}>
              </Dimmer>
            </ContentCard>
          )
          // Error
          if (error) return (
            <Container>
              <ContentCard cardTitle={t('relations.accounts.title')}>
                <p>{t('relations.accounts.error_loading')}</p>
              </ContentCard>
            </Container>
          )
          const headerOptions = <Card.Options>
            <Button color={(localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE)) ? 'primary': 'secondary'}  
                    size="sm"
                    onClick={() => {
                      localStorage.setItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE, true)
                      refetch(get_list_query_variables())
                    }
            }>
              {t('general.active')}
            </Button>
            <Button color={(localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE)) ? 'secondary': 'primary'} 
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
          
          // Empty list
          if (!data.accounts.edges.length) { return (
            <ContentCard cardTitle={t('relations.accounts.title')}
                          headerContent={headerOptions}>
              <p>
              {(!localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE)) ? t('relations.accounts.empty_list') : t("relations.accounts.empty_archive")}
              </p>
              
            </ContentCard>
          )} else {   
          // Life's good! :)
          return (
            <Container>
              <Page.Header title={t("relations.title")}>
                <div className="page-options d-flex">
                  <InputSearch 
                    initialValueKey={CSLS.RELATIONS_ACCOUNTS_SEARCH}
                    placeholder="Search..."
                    onChange={(value) => {
                      console.log(value)
                      localStorage.setItem(CSLS.RELATIONS_ACCOUNTS_SEARCH, value)
                      refetch(get_list_query_variables())
                    }}
                  />
                </div>
              </Page.Header>
              <Grid.Row>
                <Grid.Col md={9}>
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
                                    {console.log(node)}
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
                                            updateAccountActive({ variables: {
                                              input: {
                                                id,
                                                isActive: !localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE)
                                              }
                                        }, refetchQueries: [
                                            {query: GET_ACCOUNTS_QUERY, variables: get_list_query_variables()}
                                        ]}).then(({ data }) => {
                                          console.log('got data', data);
                                          toast.success(
                                            (localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE)) ? t('relations.accounts.deactivated'): t('relations.accounts.restored'), {
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
                </Grid.Col>
                <Grid.Col md={3}>
                  <HasPermissionWrapper permission="add"
                                        resource="account">
                    <Button color="primary btn-block mb-6"
                            onClick={() => history.push("/relations/accounts/add")}>
                      <Icon prefix="fe" name="plus-circle" /> {t('relations.accounts.add')}
                    </Button>
                  </HasPermissionWrapper>
                  <RelationsMenu active_link='accounts'/>
                </Grid.Col>
              </Grid.Row>
            </Container>
          )}}
        }
      </Query>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(RelationsAccounts))