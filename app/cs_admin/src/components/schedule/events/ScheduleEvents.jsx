// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


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
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../general/ContentCard"
import ScheduleEventsBase from "./ScheduleEventsBase"

import { GET_SCHEDULE_EVENTS_QUERY } from "./queries"
import { get_list_query_variables } from "./tools"

// const ARCHIVE_EVENT = gql`
//   mutation ArchiveOrganizationLevel($input: ArchiveOrganizationLevelInput!) {
//     archiveOrganizationLevel(input: $input) {
//       organizationLevel {
//         id
//         archived
//       }
//     }
//   }
// `

function ScheduleEvents({t, history, archived=false}) {
  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_EVENTS_QUERY, {
    variables: get_list_query_variables()
  })

  const sidebarContent = <HasPermissionWrapper permission="add" resource="scheduleevent">
    <Button color="primary btn-block mb-1"
            onClick={() => history.push("/schedule/events/add")}>
      <Icon prefix="fe" name="plus-circle" /> {t('schedule.events.add')}
    </Button>
  </HasPermissionWrapper>

  if (loading) {
    return (
      <ScheduleEventsBase sidebarContent={sidebarContent}>
        <ContentCard cardTitle={t('schedule.events.title')}>
          <Dimmer active={true}
                  loader={true}>
          </Dimmer>
        </ContentCard>
      </ScheduleEventsBase>
    )
  }

  if (error) {
    return (
      <ScheduleEventsBase sidebarContent={sidebarContent}>
        <ContentCard cardTitle={t('schedule.events.title')}>
          {t("schedle.events.error_loading_data")}
        </ContentCard>
      </ScheduleEventsBase>
    )
  }

  return (
    <ScheduleEventsBase sidebarContent={sidebarContent}>
      <ContentCard cardTitle={t('schedule.events.title')}>
        hello world
      </ContentCard>
    </ScheduleEventsBase>
  )
}

export default withTranslation()(withRouter(ScheduleEvents))


// const ScheduleEvents = ({ t, history, archived=false }) => (
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

