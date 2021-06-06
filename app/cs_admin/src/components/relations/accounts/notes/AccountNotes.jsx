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
import CSLS from "../../../../tools/cs_local_storage"


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

import { get_list_query_variables } from "./tools"



function AccountNotes({ t, history, match }) {
  // Set some initial value for noteType, if not found
  if (!localStorage.getItem(CSLS.RELATIONS_ACCOUNT_NOTES_NOTE_TYPE)) {
    localStorage.setItem(CSLS.RELATIONS_ACCOUNT_NOTES_NOTE_TYPE, "BACKOFFICE") 
  }

  const appSettings = useContext(AppSettingsContext)
  const dateTimeFormatMoment = appSettings.dateTimeFormatMoment

  const accountId = match.params.account_id

  const { loading, error, data, fetchMore, refetch } = useQuery(GET_ACCOUNT_NOTES_QUERY, {
    variables: get_list_query_variables(accountId)
  })
  const [deleteAccountNote] = useMutation(DELETE_ACCOUNT_NOTE)

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
      <Grid.Row>
        <Grid.Col>
          <div className="float-right mb-4">
            <Button.List>
              <Button color={(localStorage.getItem(CSLS.RELATIONS_ACCOUNT_NOTES_NOTE_TYPE) === "BACKOFFICE") ? 'primary': 'secondary'}  
                      size=""
                      onClick={() => {
                        localStorage.setItem(CSLS.RELATIONS_ACCOUNT_NOTES_NOTE_TYPE, "BACKOFFICE")
                        refetch(get_list_query_variables(accountId))
                      }
              }>
                {t('relations.account.notes.backoffice')}
              </Button>
              <Button color={(localStorage.getItem(CSLS.RELATIONS_ACCOUNT_NOTES_NOTE_TYPE) === "TEACHERS") ? 'primary': 'secondary'} 
                      size="" 
                      className="ml-2" 
                      onClick={() => {
                        localStorage.setItem(CSLS.RELATIONS_ACCOUNT_NOTES_NOTE_TYPE, "TEACHERS")
                        refetch(get_list_query_variables(accountId))
                      }
              }>
                {t('relations.account.notes.teachers')}
              </Button>
            </Button.List>
          </div>
        </Grid.Col>
      </Grid.Row>
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
              <div dangerouslySetInnerHTML={{__html: node.note}} />
            </Card.Body>
            <Card.Footer>
              <Button 
                color="danger"
                size="sm"
                className="float-right"
                outline
                onClick={() => {
                  confirm_delete({
                    t: t,
                    msgConfirm: t("relations.account.notes.delete_confirm_msg"),
                    msgDescription: <p><div dangerouslySetInnerHTML={{__html: node.note}} /></p>,
                    msgSuccess: t('relations.account.notes.deleted'),
                    deleteFunction: deleteAccountNote,
                    functionVariables: { 
                      variables: {
                        input: {
                          id: node.id
                        }
                      }, 
                      refetchQueries: [
                        {query: GET_ACCOUNT_NOTES_QUERY, variables: get_list_query_variables(accountId) },
                      ]
                    }
                  })
                }}
              >
                <Icon name="trash-2" />
              </Button>
              <Link to={`/relations/accounts/${match.params.account_id}/notes/edit/${node.id}`}>
                <Button
                  color="secondary"
                  size="sm"
                  className="float-right mr-4"
                  outline
                >
                  {t("general.edit")}
                </Button>
              </Link>              
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
