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
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import BooleanBadge from "../../ui/BooleanBadge"
import ContentCard from "../../general/ContentCard"
import ScheduleMenu from "../ScheduleMenu"

import { GET_CLASSES_QUERY } from "./queries"


import moment from 'moment'

let dateFrom = new Date()
let dateUntil = new Date()
dateUntil.setDate(dateUntil.getDate() + 6)
console.log(dateFrom)
console.log(dateUntil)


const ScheduleClasses = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("schedule.title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_CLASSES_QUERY} variables={
              { dateFrom: moment(dateFrom).format('YYYY-MM-DD'), 
                dateUntil: moment(dateUntil).format('YYYY-MM-DD')}
            }>
             {({ loading, error, data: {scheduleClasses: schedule_classes}, refetch }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('schedule.classes.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('schedule.classes.title')}>
                    <p>{t('schedule.classes.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  {/* <Button color={(!archived) ? 'primary': 'secondary'}  
                          size="sm"
                          onClick={() => {archived=false; refetch({archived});}}>
                    {t('general.current')}
                  </Button>
                  <Button color={(archived) ? 'primary': 'secondary'} 
                          size="sm" 
                          className="ml-2" 
                          onClick={() => {archived=true; refetch({archived});}}>
                    {t('general.archive')}
                  </Button> */}
                </Card.Options>
                
                // Empty list
                if (!schedule_classes.length) { return (
                  <ContentCard cardTitle={t('schedule.classes.title')}
                               headerContent={headerOptions}>
                    <p>
                      {t('schedule.classes.empty_list')}
                    </p>
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  schedule_classes.map(({ date, classes }) => (
                  <div key={v4()}>
                    <Card>
                      <Card.Header>
                        <Card.Title>
                          <b>{moment(date).format("dddd")}</b> {' '}
                          <span className="text-muted">
                            {moment(date).format("LL")} 
                          </span>
                        </Card.Title>
                      </Card.Header>
                      <Card.Body>
                        {!(classes.length) ? t('schedule.classes.empty_list') :
                          <Table>
                            <Table.Header>
                              <Table.Row key={v4()}>
                                <Table.ColHeader>{t('general.time')}</Table.ColHeader>
                                <Table.ColHeader>{t('general.location')}</Table.ColHeader>
                                <Table.ColHeader>{t('general.class')}</Table.ColHeader>
                                <Table.ColHeader>{t('general.public')}</Table.ColHeader>
                              </Table.Row>
                            </Table.Header>
                            <Table.Body>
                              {classes.map((
                                { scheduleItemID, 
                                  date, 
                                  organizationLocationRoom, 
                                  organizationClasstype, 
                                  organizationLevel,
                                  timeStart, 
                                  timeEnd,
                                  displayPublic }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col>
                                    {/* Start & end time */}
                                    {moment(date + ' ' + timeStart).format('LT')} {' - '}
                                    {moment(date + ' ' + timeEnd).format('LT')}
                                  </Table.Col>
                                  <Table.Col>
                                    {/* Location */}
                                    {organizationLocationRoom.organizationLocation.name} {' '}
                                    <span className="text-muted"> &bull; {organizationLocationRoom.name}</span>
                                  </Table.Col>
                                  <Table.Col>
                                    {/* Type and level */}
                                    {organizationClasstype.name} <br />
                                    <span className="text-muted">
                                      {organizationLevel.name}
                                    </span>
                                  </Table.Col>
                                  <Table.Col>
                                    {/* Public */}
                                    <BooleanBadge value={displayPublic} />
                                  </Table.Col>
                                </Table.Row>
                              ))}
                            </Table.Body>
                          </Table>
                        }
                      </Card.Body>
                    </Card>
                  </div>
                  ))

                  


                  // <ContentCard cardTitle={t('schedule.classes.title')}
                  //              headerContent={headerOptions} >
                  //   <Table>
                  //         <Table.Header>
                  //           <Table.Row key={v4()}>
                  //             <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                  //           </Table.Row>
                  //         </Table.Header>
                  //         <Table.Body>
                  //             {schedule_classes.map(({ date, classes }) => (
                  //               <Table.Row key={v4()}>
                  //                 <Table.Col key={v4()}>
                  //                   {node.name}
                  //                 </Table.Col>
                  //                 <Table.Col className="text-right" key={v4()}>
                  //                   {(node.archived) ? 
                  //                     <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                  //                     <Button className='btn-sm' 
                  //                             onClick={() => history.push("/organization/classes/edit/" + node.id)}
                  //                             color="secondary">
                  //                       {t('general.edit')}
                  //                     </Button>
                  //                   }
                  //                 </Table.Col>
                  //                 {/* <Mutation mutation={ARCHIVE_LEVEL} key={v4()}>
                  //                   {(archiveCostcenter, { data }) => (
                  //                     <Table.Col className="text-right" key={v4()}>
                  //                       <button className="icon btn btn-link btn-sm" 
                  //                          title={t('general.archive')} 
                  //                          href=""
                  //                          onClick={() => {
                  //                            console.log("clicked archived")
                  //                            let id = node.id
                  //                            archiveCostcenter({ variables: {
                  //                              input: {
                  //                               id,
                  //                               archived: !archived
                  //                              }
                  //                       }, refetchQueries: [
                  //                           {query: GET_CLASSES_QUERY, variables: {"archived": archived }}
                  //                       ]}).then(({ data }) => {
                  //                         console.log('got data', data);
                  //                         toast.success(
                  //                           (archived) ? t('general.unarchived'): t('general.archived'), {
                  //                             position: toast.POSITION.BOTTOM_RIGHT
                  //                           })
                  //                       }).catch((error) => {
                  //                         toast.error((t('general.toast_server_error')) + ': ' +  error, {
                  //                             position: toast.POSITION.BOTTOM_RIGHT
                  //                           })
                  //                         console.log('there was an error sending the query', error);
                  //                       })
                  //                       }}>
                  //                         <Icon prefix="fa" name="inbox" />
                  //                       </button>
                  //                     </Table.Col>
                  //                   )}
                  //                 </Mutation> */}
                  //               </Table.Row>
                  //             ))}
                  //         </Table.Body>
                  //       </Table>
                  // </ContentCard>
                )}}
             }
            </Query>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="scheduleclass">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/schedule/classes/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('schedule.classes.add')}
              </Button>
            </HasPermissionWrapper>
            <ScheduleMenu active_link='classes'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(ScheduleClasses))