// @flow

import React, { useContext } from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import moment from 'moment'

import AppSettingsContext from '../../../context/AppSettingsContext'


import {
  BlogCard,
  Button,
  Badge,
  Card,
  Grid,
  Icon,
  Table
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import confirm_delete from "../../../../tools/confirm_delete"

import ContentCard from "../../../general/ContentCard"
import LoadMoreOnBottomScroll from "../../../general/LoadMoreOnBottomScroll"
import AccountNotesBase from "./AccountNotesBase"

import { 
  GET_ACCOUNT_NOTES_QUERY,
  DELETE_ACCOUNT_NOTE
} from "./queries"



function AccountNotes({ t, history, match }) {
  const appSettings = useContext(AppSettingsContext)
  const dateTimeFormatMoment = appSettings.dateTimeFormatMoment

  const accountId = match.params.account_id

  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_NOTES_QUERY, {
    variables: { account: accountId, noteType: "BACKOFFICE" }
  })
  const [deleteAccountFinancePaymentBatchCategoryItem] = useMutation(DELETE_ACCOUNT_NOTE)

  if (loading) return (
    <AccountNotesBase>
      <p>{t('general.loading_with_dots')}</p>
    </AccountNotesBase>
  )
  // Error
  if (error) {
    console.log(error)
    return (
      <AccountNotesBase>
        <p>{t('general.error_sad_smiley')}</p>
      </AccountNotesBase>
    )
  }

  let notes = data.accountNotes

  return (
    <AccountNotesBase>
        <LoadMoreOnBottomScroll 
          pageInfo={notes.pageInfo}
          onLoadMore={() => {
            fetchMore({
              variables: {
                after: notes.pageInfo.endCursor
              },
              updateQuery: (previousResult, { fetchMoreResult }) => {
                const newEdges = fetchMoreResult.accountNotes.edges
                const pageInfo = fetchMoreResult.accountNotes.pageInfo

                return newEdges.length
                  ? {
                      // Put the new accountClasspasses at the end of the list and update `pageInfo`
                      // so we have the new `endCursor` and `hasNextPage` values
                      accountNotes: {
                        __typename: previousResult.accountNotes.__typename,
                        edges: [ ...previousResult.accountNotes.edges, ...newEdges ],
                        pageInfo
                      }
                    }
                  : previousResult
              }
            })
          }} 
        >
          {notes.edges.map(({ node }) => (
              <Card>
                <Card.Body>
                  {(node.injury) ? <Badge color="danger" className="float-right">{t("general.injury")}</Badge> : ""}
                  {node.note}
                </Card.Body>
                <Card.Footer>
                  <small className="float-right">delete</small>
                  <small className="float-right mr-4">edit</small>
                  
                  <small className="text-muted float-right mr-4">{moment(node.createdAt).format(dateTimeFormatMoment)}</small>
                  {node.noteBy.fullName} <br />
                </Card.Footer>
              </Card>
          ))}
        </LoadMoreOnBottomScroll>
    </AccountNotesBase>
  )
}
      
        
export default withTranslation()(withRouter(AccountNotes))
