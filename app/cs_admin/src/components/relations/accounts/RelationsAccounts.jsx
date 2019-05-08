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
import { confirmAlert } from 'react-confirm-alert'
import { toast } from 'react-toastify'

import ContentCard from "../../general/ContentCard"
import RelationsMenu from "../RelationsMenu"

import { GET_ACCOUNTS_QUERY } from "./queries"


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


const confirm = ({t, msgConfirm, msgDescription, msgSuccess, deleteFunction, functionVariables}) => {
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


const RelationsAccounts = ({ t, history, isActive=true }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("relations.title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_ACCOUNTS_QUERY} variables={{ isActive }}>
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
                  <Button color={(isActive) ? 'primary': 'secondary'}  
                          size="sm"
                          onClick={() => {isActive=true; refetch({isActive});}}>
                    {t('general.active')}
                  </Button>
                  <Button color={(!isActive) ? 'primary': 'secondary'} 
                          size="sm" 
                          className="ml-2" 
                          onClick={() => {isActive=false; refetch({isActive});}}>
                    {t('general.deleted')}
                  </Button>
                </Card.Options>
                
                // Empty list
                if (!accounts.edges.length) { return (
                  <ContentCard cardTitle={t('relations.accounts.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!isActive) ? t('relations.accounts.empty_list') : t("relations.accounts.empty_archive")}
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
                                    {(!node.isActive) ? 
                                      <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/organization/accounts/edit/" + node.id)}
                                              color="secondary">
                                        {t('general.edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={UPDATE_ACCOUNT_ACTIVE} key={v4()}>
                                    {(updateAccountActive, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('general.archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked isActive")
                                             let id = node.id
                                             updateAccountActive({ variables: {
                                               input: {
                                                id,
                                                isActive: !isActive
                                               }
                                        }, refetchQueries: [
                                            {query: GET_ACCOUNTS_QUERY, variables: {"isActive": isActive }}
                                        ]}).then(({ data }) => {
                                          console.log('got data', data);
                                          toast.success(
                                            (isActive) ? t('general.unisActive'): t('general.isActive'), {
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
                                                let msgDescription = <p>
                                                  {node.first_name} {node.last_name}
                                                </p>

                                                confirm({
                                                  t:t,
                                                  msgConfirm: t("relations.accounts.delete_confirm_msg"),
                                                  msgDescription: msgDescription,
                                                  msgSuccess: t('relations.accounts.deleted'),
                                                  deleteFunction: deleteAccount,
                                                  functionVariables: { variables: {
                                                    input: {
                                                      id: node.id
                                                    }
                                                  }, refetchQueries: [
                                                    {query: GET_ACCOUNTS_QUERY, variables: {"isActive": false }}
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
                )}}
             }
            </Query>
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
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(RelationsAccounts))