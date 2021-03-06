// @flow

import React, { useContext } from 'react'
import { Query, Mutation, useQuery } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import moment from 'moment'
import AppSettingsContext from '../../../../context/AppSettingsContext'


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
import SiteWrapper from "../../../../SiteWrapper"
import HasPermissionWrapper from "../../../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../../../general/ContentCard"

import { GET_TASK_RESULT_QUERY } from "../../../queries"
import AutomationAccountSubscriptionCreditsBase from './AutomationAccountSubscriptionCreditsBase'
import AutomationTaskResultStatus from "../../../AutomationTaskResultStatus"

// const ARCHIVE_LEVEL = gql`
//   mutation ArchiveOrganizationLevel($input: ArchiveOrganizationLevelInput!) {
//     archiveOrganizationLevel(input: $input) {
//       organizationLevel {
//         id
//         archived
//       }
//     }
//   }
// `

function AutomationAccountSubscriptionCredits({t, history, match}) {
  const appSettings = useContext(AppSettingsContext)
  const dateTimeFormatMoment = appSettings.dateTimeFormatMoment

  const { error, loading, data, fetchMore } = useQuery(GET_TASK_RESULT_QUERY, {
    variables: {
      taskName: "costasiella.tasks.account.subscription.credits.tasks.account_subscription_credits_add_for_month"
    }
  })

  const headerOptions = <Card.Options>
    <Link to={"/automation/account/subscriptions/credits/add"}>
      <Button color="primary" 
              size="sm"
      >
      {t('general.new_task')}
      </Button>
    </Link>
  </Card.Options>


  // Loading
  if (loading) return (
    <AutomationAccountSubscriptionCreditsBase>
      <p>{t('general.loading_with_dots')}</p>
    </AutomationAccountSubscriptionCreditsBase>
  )
  // Error
  if (error) {
    console.log(error)
    return (
      <AutomationAccountSubscriptionCreditsBase>
        <p>{t('general.error_sad_smiley')}</p>
      </AutomationAccountSubscriptionCreditsBase>
    )
  }

  console.log("Automation credits data:")
  console.log(data)
  const taskResults = data.djangoCeleryResultTaskResults
  // const account = data.account
  // const scheduleItemAttendances = data.scheduleItemAttendances
  

  return (
    <AutomationAccountSubscriptionCreditsBase>
      <ContentCard 
        cardTitle={t('automation.account.subscriptions.credits.title_card')}
        pageInfo={taskResults.pageInfo}
        headerContent={headerOptions}
        onLoadMore={() => {
          fetchMore({
            variables: {
              after: taskResults.pageInfo.endCursor
            },
            updateQuery: (previousResult, { fetchMoreResult }) => {
              const newEdges = fetchMoreResult.djangoCeleryResultTaskResults.edges
              const pageInfo = fetchMoreResult.djangoCeleryResultTaskResults.pageInfo

              return newEdges.length
                ? {
                    // Put the new invoices at the end of the list and update `pageInfo`
                    // so we have the new `endCursor` and `hasNextPage` values
                    djangoCeleryResultTaskResults: {
                      __typename: previousResult.djangoCeleryResultTaskResults.__typename,
                      edges: [ ...previousResult.djangoCeleryResultTaskResults.edges, ...newEdges ],
                      pageInfo
                    }
                  }
                : previousResult
              }
            })
          }} 
        >
          { (!taskResults.edges.length) ? 
            // Empty list
            <p>{t('automation.account.subscriptions.credits.empty_list')}</p>
            :
            // Content
            <Table>
              <Table.Header>
                <Table.Row key={v4()}>
                  <Table.ColHeader>{t('automation.general.status.title')}</Table.ColHeader>
                  <Table.ColHeader>{t('automation.general.time_completed')}</Table.ColHeader>
                  <Table.ColHeader>{t('automation.general.task_kwargs')}</Table.ColHeader>
                  <Table.ColHeader>{t('automation.general.task_result')}</Table.ColHeader>
                  <Table.ColHeader></Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {taskResults.edges.map(({ node }) => (
                  <Table.Row key={v4()}>
                    <Table.Col>
                      <AutomationTaskResultStatus status={node.status} />
                    </Table.Col>
                    <Table.Col>
                      {moment(node.dateDone).format(dateTimeFormatMoment)}
                    </Table.Col>
                    <Table.Col>
                      {node.taskKwargs}
                    </Table.Col>
                    <Table.Col>
                      {node.result}
                    </Table.Col>
                    <Table.Col>

                    </Table.Col>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          }
        </ContentCard>
    </AutomationAccountSubscriptionCreditsBase>
  )
}

export default withTranslation()(withRouter(AutomationAccountSubscriptionCredits))