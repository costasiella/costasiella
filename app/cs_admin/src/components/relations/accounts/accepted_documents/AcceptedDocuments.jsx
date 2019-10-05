// @flow

import React, { useContext } from 'react'
import { useQuery } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import AppSettingsContext from '../../../context/AppSettingsContext'



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

import { GET_ACCOUNT_ACCEPTED_DOCUMENTS_QUERY } from "./queries"

import moment from 'moment'


function AccountAcceptedDocuments({ t, history, match }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat

  const accountId = match.params.account_id
  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_ACCEPTED_DOCUMENTS_QUERY, {
    variables: {
      account: accountId
    }
  })

  // Loading
  if (loading) return <p>{t('general.loading_with_dots')}</p>
  // Error
  if (error) {
    console.log(error)
    return <p>{t('general.error_sad_smiley')}</p>
  }
  
  const account = data.account
  const acceptedDocuments = data.accountAcceptedDocuments

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={account.firstName + " " + account.lastName} >
            <RelationsAccountsBack />
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              <ContentCard 
                cardTitle={t('relations.account.accepted_documents.title')}
                pageInfo={acceptedDocuments.pageInfo}
                onLoadMore={() => {
                  fetchMore({
                    variables: {
                      after: acceptedDocuments.pageInfo.endCursor
                    },
                    updateQuery: (previousResult, { fetchMoreResult }) => {
                      const newEdges = fetchMoreResult.acceptedDocuments.edges
                      const pageInfo = fetchMoreResult.acceptedDocuments.pageInfo

                      return newEdges.length
                        ? {
                            // Put the new acceptedDocuments at the end of the list and update `pageInfo`
                            // so we have the new `endCursor` and `hasNextPage` values
                            acceptedDocuments: {
                              __typename: previousResult.acceptedDocuments.__typename,
                              edges: [ ...previousResult.acceptedDocuments.edges, ...newEdges ],
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
                      <Table.ColHeader>{t('general.document_type')}</Table.ColHeader>
                      <Table.ColHeader>{t('general.date_accepted')}</Table.ColHeader>
                      <Table.ColHeader>{t('general.document')}</Table.ColHeader>
                    </Table.Row>
                  </Table.Header>
                  <Table.Body>
                      {acceptedDocuments.edges.map(({ node }) => (
                        <Table.Row key={v4()}>
                          <Table.Col key={v4()}>
                            {node.documentType}
                          </Table.Col>
                          <Table.Col key={v4()}>
                          {moment(node.dateAccepted).format(dateFormat)}
                          </Table.Col>
                          <Table.Col key={v4()}>
                            {node.documentUrl}
                          </Table.Col>
                          <Table.Col className="text-right" key={v4()}>
                            <Link to={"/relations/accounts/" + match.params.account_id + "/classpasses/edit/" + node.id}>
                              <Button className='btn-sm' 
                                      color="secondary">
                                {t('general.edit')}
                              </Button>
                            </Link>
                          </Table.Col>
                        </Table.Row>
                      ))}
                  </Table.Body>
                </Table>
              </ContentCard>
            </Grid.Col>
            <Grid.Col md={3}>
              <ProfileCardSmall user={account}/>
              <ProfileMenu 
                active_link='accepted_documents' 
                account_id={match.params.account_id}
              />
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

      
        
export default withTranslation()(withRouter(AccountAcceptedDocuments))