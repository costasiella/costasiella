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


// const OrganizationLevels = ({ t, history, archived=false }) => (
//   <SiteWrapper>
//     <div className="my-3 my-md-5">
//       <Container>
//         <Page.Header title={t("organization.title")} />
//         <Grid.Row>
//           <Grid.Col md={9}>
//             <Query query={GET_LEVELS_QUERY} variables={{ archived }}>
//              {({ loading, error, data: {organizationLevels: levels}, refetch, fetchMore }) => {
//                 // Loading
//                 if (loading) return (
//                   <ContentCard cardTitle={t('organization.levels.title')}>
//                     <Dimmer active={true}
//                             loader={true}>
//                     </Dimmer>
//                   </ContentCard>
//                 )
//                 // Error
//                 if (error) return (
//                   <ContentCard cardTitle={t('organization.levels.title')}>
//                     <p>{t('organization.levels.error_loading')}</p>
//                   </ContentCard>
//                 )
//                 const headerOptions = <Card.Options>
//                   <Button color={(!archived) ? 'primary': 'secondary'}  
//                           size="sm"
//                           onClick={() => {archived=false; refetch({archived});}}>
//                     {t('general.current')}
//                   </Button>
//                   <Button color={(archived) ? 'primary': 'secondary'} 
//                           size="sm" 
//                           className="ml-2" 
//                           onClick={() => {archived=true; refetch({archived});}}>
//                     {t('general.archive')}
//                   </Button>
//                 </Card.Options>
                
//                 // Empty list
//                 if (!levels.edges.length) { return (
//                   <ContentCard cardTitle={t('organization.levels.title')}
//                                headerContent={headerOptions}>
//                     <p>
//                     {(!archived) ? t('organization.levels.empty_list') : t("organization.levels.empty_archive")}
//                     </p>
                   
//                   </ContentCard>
//                 )} else {   
//                 // Life's good! :)
//                 return (
//                   <ContentCard cardTitle={t('organization.levels.title')}
//                                headerContent={headerOptions}
//                                pageInfo={levels.pageInfo}
//                                onLoadMore={() => {
//                                 fetchMore({
//                                   variables: {
//                                     after: levels.pageInfo.endCursor
//                                   },
//                                   updateQuery: (previousResult, { fetchMoreResult }) => {
//                                     const newEdges = fetchMoreResult.organizationLevels.edges
//                                     const pageInfo = fetchMoreResult.organizationLevels.pageInfo

//                                     return newEdges.length
//                                       ? {
//                                           // Put the new levels at the end of the list and update `pageInfo`
//                                           // so we have the new `endCursor` and `hasNextPage` values
//                                           organizationLevels: {
//                                             __typename: previousResult.organizationLevels.__typename,
//                                             edges: [ ...previousResult.organizationLevels.edges, ...newEdges ],
//                                             pageInfo
//                                           }
//                                         }
//                                       : previousResult
//                                   }
//                                 })
//                               }} >
//                     <Table>
//                           <Table.Header>
//                             <Table.Row key={v4()}>
//                               <Table.ColHeader>{t('general.name')}</Table.ColHeader>
//                             </Table.Row>
//                           </Table.Header>
//                           <Table.Body>
//                               {levels.edges.map(({ node }) => (
//                                 <Table.Row key={v4()}>
//                                   <Table.Col key={v4()}>
//                                     {node.name}
//                                   </Table.Col>
//                                   <Table.Col className="text-right" key={v4()}>
//                                     {(node.archived) ? 
//                                       <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
//                                       <Button className='btn-sm' 
//                                               onClick={() => history.push("/organization/levels/edit/" + node.id)}
//                                               color="secondary">
//                                         {t('general.edit')}
//                                       </Button>
//                                     }
//                                   </Table.Col>
//                                   <Mutation mutation={ARCHIVE_LEVEL} key={v4()}>
//                                     {(archiveCostcenter, { data }) => (
//                                       <Table.Col className="text-right" key={v4()}>
//                                         <button className="icon btn btn-link btn-sm" 
//                                            title={t('general.archive')} 
//                                            href=""
//                                            onClick={() => {
//                                              console.log("clicked archived")
//                                              let id = node.id
//                                              archiveCostcenter({ variables: {
//                                                input: {
//                                                 id,
//                                                 archived: !archived
//                                                }
//                                         }, refetchQueries: [
//                                             {query: GET_LEVELS_QUERY, variables: {"archived": archived }}
//                                         ]}).then(({ data }) => {
//                                           console.log('got data', data);
//                                           toast.success(
//                                             (archived) ? t('general.unarchived'): t('general.archived'), {
//                                               position: toast.POSITION.BOTTOM_RIGHT
//                                             })
//                                         }).catch((error) => {
//                                           toast.error((t('general.toast_server_error')) + ': ' +  error, {
//                                               position: toast.POSITION.BOTTOM_RIGHT
//                                             })
//                                           console.log('there was an error sending the query', error);
//                                         })
//                                         }}>
//                                           <Icon prefix="fa" name="inbox" />
//                                         </button>
//                                       </Table.Col>
//                                     )}
//                                   </Mutation>
//                                 </Table.Row>
//                               ))}
//                           </Table.Body>
//                         </Table>
//                   </ContentCard>
//                 )}}
//              }
//             </Query>
//           </Grid.Col>
//           <Grid.Col md={3}>
//             <HasPermissionWrapper permission="add"
//                                   resource="organizationlevel">
//               <Button color="primary btn-block mb-6"
//                       onClick={() => history.push("/organization/levels/add")}>
//                 <Icon prefix="fe" name="plus-circle" /> {t('organization.levels.add')}
//               </Button>
//             </HasPermissionWrapper>
//             <OrganizationMenu active_link='levels'/>
//           </Grid.Col>
//         </Grid.Row>
//       </Container>
//     </div>
//   </SiteWrapper>
// );

export default withTranslation()(withRouter(AutomationAccountSubscriptionCredits))