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

import { GET_ACCOUNT_CLASSPASSES_QUERY } from "./queries"

const DELETE_ACCOUNT_CLASSPASS = gql`
  mutation DeleteAccountClasspass($input: DeleteAccountClasspassInput!) {
    deleteAccountClasspass(input: $input) {
      ok
    }
  }
`


const AccountClasspasses = ({ t, history, match, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Query query={GET_ACCOUNT_CLASSPASSES_QUERY} variables={{ archived: archived, accountId: match.params.account_id }} 
        fetchPolicy="network-only"> 
        {({ loading, error, data, refetch, fetchMore }) => {
          // Loading
          if (loading) return <p>{t('general.loading_with_dots')}</p>
          // Error
          if (error) {
            console.log(error)
            return <p>{t('general.error_sad_smiley')}</p>
          }

          const account = data.account
          const accountClasspasses = data.accountClasspasses

          return (
            <Container>
              <Page.Header title={account.firstName + " " + account.lastName} >
                <RelationsAccountsBack />
              </Page.Header>
              <Grid.Row>
                <Grid.Col md={9}>
                  <ContentCard 
                    cardTitle={t('relations.account.classpasses.title')}
                    pageInfo={accountClasspasses.pageInfo}
                    onLoadMore={() => {
                      fetchMore({
                        variables: {
                          after: accountClasspasses.pageInfo.endCursor
                        },
                        updateQuery: (previousResult, { fetchMoreResult }) => {
                          const newEdges = fetchMoreResult.accountClasspasses.edges
                          const pageInfo = fetchMoreResult.accountClasspasses.pageInfo

                          return newEdges.length
                            ? {
                                // Put the new accountClasspasses at the end of the list and update `pageInfo`
                                // so we have the new `endCursor` and `hasNextPage` values
                                accountClasspasses: {
                                  __typename: previousResult.accountClasspasses.__typename,
                                  edges: [ ...previousResult.accountClasspasses.edges, ...newEdges ],
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
                          <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
                          <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
                          <Table.ColHeader>{t('general.classes_remaining')}</Table.ColHeader>
                          <Table.ColHeader></Table.ColHeader> 
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                          {accountClasspasses.edges.map(({ node }) => (
                            <Table.Row key={v4()}>
                              <Table.Col key={v4()}>
                                {node.organizationClasspass.name}
                              </Table.Col>
                              <Table.Col key={v4()}>
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
                              </Mutation>
                            </Table.Row>
                          ))}
                      </Table.Body>
                    </Table>
                  </ContentCard>
                </Grid.Col>
                <Grid.Col md={3}>
                  <ProfileCardSmall user={account}/>
                  <HasPermissionWrapper permission="add"
                                        resource="accountclasspass">
                    <Link to={"/relations/accounts/" + match.params.account_id + "/classpasses/add"}>
                      <Button color="primary btn-block mb-6">
                              {/* //  onClick={() => history.push("/organization/classpasses/add")}> */}
                        <Icon prefix="fe" name="plus-circle" /> {t('relations.account.classpasses.add')}
                      </Button>
                    </Link>
                  </HasPermissionWrapper>
                  <ProfileMenu 
                    active_link='classpasses' 
                    account_id={match.params.account_id}
                  />
                </Grid.Col>
              </Grid.Row>
            </Container>
          )
        }}
      </Query>
    </div>
  </SiteWrapper>
)
      
        
export default withTranslation()(withRouter(AccountClasspasses))