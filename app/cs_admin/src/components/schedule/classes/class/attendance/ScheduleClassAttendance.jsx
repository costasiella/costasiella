// @flow

import React, { Component, useState } from 'react'
import { useQuery, useMutation, useLazyQuery } from '@apollo/react-hooks'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import moment from 'moment'

import {
  Alert,
  Dropdown,
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
import { TimeStringToJSDateOBJ } from '../../../../../tools/date_tools'
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'
import { class_edit_all_subtitle, represent_teacher_role } from "../../tools"
import { get_attendance_list_query_variables } from "./tools"
import confirm_delete from "../../../../../tools/confirm_delete"

import { get_accounts_query_variables } from "./tools"
import { class_subtitle } from "../tools"

import ScheduleClassBack from "../ScheduleClassBack"
import ContentCard from "../../../../general/ContentCard"
import InputSearch from "../../../../general/InputSearch"
import BadgeBookingStatus from "../../../../ui/BadgeBookingStatus"
import ScheduleClassAttendanceDelete from "./ScheduleClassAttendanceDelete"
// import ClassEditBase from "../ClassEditBase"

import { GET_ACCOUNTS_QUERY, GET_SCHEDULE_CLASS_ATTENDANCE_QUERY, UPDATE_SCHEDULE_ITEM_ATTENDANCE } from "./queries"
import CSLS from "../../../../../tools/cs_local_storage"


function setAttendanceStatus({t, updateAttendance, node, status}) {
  updateAttendance({
    variables: { 
      input: {
        id: node.id, 
        bookingStatus: status
      }
    }
  }).then(({ data }) => {
    console.log('got data', data);
    toast.success(
      t('schedule.classes.class.attendance.status_saved'), {
        position: toast.POSITION.BOTTOM_RIGHT
      })
  }).catch((error) => {
    toast.error((t('general.toast_server_error')) + ': ' +  error, {
        position: toast.POSITION.BOTTOM_RIGHT
      })
    console.log('there was an error sending the query', error);
  })
}


function ScheduleClassAttendance({ t, match, history }) {
  const [showSearch, setShowSearch] = useState(false)
  const return_url = "/schedule/classes/"
  const schedule_item_id = match.params.class_id
  const class_date = match.params.date
  const { refetch: refetchAttendance, loading: queryAttendanceLoading, error: queryAttendanceError, data: queryAttendanceData } = useQuery(
    GET_SCHEDULE_CLASS_ATTENDANCE_QUERY, {
      variables: get_attendance_list_query_variables(schedule_item_id, class_date)
    }
  )
  const [ updateAttendance, 
    { loading: mutationAttendanceLoading, error: mutationAttendanceError },
  ] = useMutation(UPDATE_SCHEDULE_ITEM_ATTENDANCE)

  const [ getAccounts, 
         { refetch: refetchAccounts, 
           fetchMore: fetchMoreAccounts,
           loading: queryAccountsLoading, 
           error: queryAccountsError, 
           data: queryAccountsData 
         }] = useLazyQuery( GET_ACCOUNTS_QUERY )

  console.log('queryAccountsData')
  console.log(queryAccountsData)

  // const [createInvoice, { data }] = useMutation(CREATE_ACCOUNT_INVOICE, {
  //   // onCompleted = () => history.push('/finance/invoices/edit/')
  // }) 

  // Query
  // Loading
  if (queryAttendanceLoading) return <p>{t('general.loading_with_dots')}</p>
  // Error
  if (queryAttendanceError) {
    console.log(queryAttendanceError)
    return <p>{t('general.error_sad_smiley')}</p>
  }
  
  console.log(queryAttendanceData)
  const scheduleItem = queryAttendanceData.scheduleItem
  const subtitle = class_subtitle({
    t: t,
    location: scheduleItem.organizationLocationRoom.organizationLocation.name, 
    locationRoom: scheduleItem.organizationLocationRoom.name,
    classtype: scheduleItem.organizationClasstype.name, 
    timeStart: TimeStringToJSDateOBJ(scheduleItem.timeStart), 
    date: class_date
  })
  
  
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('schedule.title')} subTitle={subtitle}>
            <div className="page-options d-flex">       
              <ScheduleClassBack />
              <InputSearch 
                initialValueKey={CSLS.SCHEDULE_CLASSES_CLASS_ATTENDANCE_SEARCH}
                placeholder="Search..."
                onChange={(value) => {
                  console.log(value)
                  localStorage.setItem(CSLS.SCHEDULE_CLASSES_CLASS_ATTENDANCE_SEARCH, value)
                  if (value) {
                    // {console.log('showSearch')}
                    // {console.log(showSearch)}
                    setShowSearch(true)
                    getAccounts({ variables: get_accounts_query_variables()})
                  } else {
                    setShowSearch(false)
                  }
                }}
              />
            </div>
          </Page.Header>
          <Grid.Row>
              <Grid.Col md={9}>
                {/* Search results */}
                {(showSearch && (queryAccountsData) && (!queryAccountsLoading) && (!queryAccountsError)) ?
                  <ContentCard cardTitle={t('general.search_results')}
                            pageInfo={queryAccountsData.accounts.pageInfo}
                            onLoadMore={() => {
                                fetchMoreAccounts({
                                variables: {
                                  after: queryAccountsData.accounts.pageInfo.endCursor
                                },
                                updateQuery: (previousResult, { fetchMoreResult }) => {
                                  const newEdges = fetchMoreResult.accounts.edges
                                  const pageInfo = fetchMoreResult.accounts.pageInfo 

                                  return newEdges.length
                                    ? {
                                        // Put the new accounts at the end of the list and update `pageInfo`
                                        // so we have the new `endCursor` and `hasNextPage` values
                                        queryAccountsData: {
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
                          <Table.ColHeader></Table.ColHeader>
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                        {queryAccountsData.accounts.edges.map(({ node }) => (
                          <Table.Row key={v4()}>
                            <Table.Col key={v4()}>
                              {node.firstName} {node.lastName}
                            </Table.Col>
                            <Table.Col key={v4()}>
                              {node.email}
                            </Table.Col>
                            <Table.Col key={v4()}>
                              <Link to={"/schedule/classes/class/book/" + schedule_item_id + "/" + class_date + "/" + node.id}>
                                <Button color="secondary pull-right">
                                  {t('general.checkin')} <Icon name="chevron-right" />
                                </Button>
                              </Link>       
                            </Table.Col>
                          </Table.Row>
                        ))}
                      </Table.Body>
                    </Table>
                  </ContentCard> : ""
                }
                {/* Attendance */}
                <ContentCard cardTitle={t('general.attendance')}
                            pageInfo={queryAttendanceData.scheduleItemAttendances.pageInfo}
                            onLoadMore={() => {
                                fetchMoreAccounts({
                                variables: {
                                  after: queryAttendanceData.scheduleItemAttendances.pageInfo.endCursor
                                },
                                updateQuery: (previousResult, { fetchMoreResult }) => {
                                  const newEdges = fetchMoreResult.scheduleItemAttendances.edges
                                  const pageInfo = fetchMoreResult.scheduleItemAttendances.pageInfo 

                                  return newEdges.length
                                    ? {
                                        // Put the new scheduleItemAttendances at the end of the list and update `pageInfo`
                                        // so we have the new `endCursor` and `hasNextPage` values
                                        queryAttendanceData: {
                                          scheduleItemAttendances: {
                                            __typename: previousResult.scheduleItemAttendances.__typename,
                                            edges: [ ...previousResult.scheduleItemAttendances.edges, ...newEdges ],
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
                        <Table.ColHeader>{t('general.booking_status')}</Table.ColHeader>
                        <Table.ColHeader></Table.ColHeader>
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                      {queryAttendanceData.scheduleItemAttendances.edges.map(({ node }) => (
                          <Table.Row key={v4()}>
                            <Table.Col>
                              {node.account.fullName}
                            </Table.Col>
                            <Table.Col>
                              <BadgeBookingStatus status={node.bookingStatus} />
                            </Table.Col>
                            <Table.Col>
                              <Dropdown
                                key={v4()}
                                className="pull-right"
                                type="button"
                                toggle
                                color="secondary btn-sm"
                                triggerContent={t("general.status")}
                                items={[
                                  <HasPermissionWrapper key={v4()} permission="change" resource="scheduleitemattendance">
                                    <Dropdown.Item
                                      key={v4()}
                                      icon="check"
                                      onClick={() => {
                                        setAttendanceStatus({
                                          t: t, 
                                          updateAttendance: updateAttendance,
                                          node: node,
                                          status: 'ATTENDING'
                                        })
                                        refetchAttendance()
                                      }}>
                                        {t('schedule.classes.class.attendance.booking_status.ATTENDING')}
                                    </Dropdown.Item>
                                  </HasPermissionWrapper>,
                                  <HasPermissionWrapper key={v4()} permission="change" resource="scheduleitemattendance">
                                    <Dropdown.Item
                                      key={v4()}
                                      icon="calendar"
                                      onClick={() => {
                                        setAttendanceStatus({
                                          t: t, 
                                          updateAttendance: updateAttendance,
                                          node: node,
                                          status: 'BOOKED'
                                        })
                                        refetchAttendance()
                                      }}>
                                        {t('schedule.classes.class.attendance.booking_status.BOOKED')}
                                    </Dropdown.Item>
                                  </HasPermissionWrapper>,
                                  <HasPermissionWrapper key={v4()} permission="change" resource="scheduleitemattendance">
                                    <Dropdown.Item
                                      key={v4()}
                                      icon="x"
                                      onClick={() => {
                                        setAttendanceStatus({
                                          t: t, 
                                          updateAttendance: updateAttendance,
                                          node: node,
                                          status: 'CANCELLED'
                                        })
                                        refetchAttendance()
                                      }}>
                                        {t('schedule.classes.class.attendance.booking_status.CANCELLED')}
                                    </Dropdown.Item>
                                  </HasPermissionWrapper>,
                                  // <HasPermissionWrapper key={v4()} permission="change" resource="scheduleitemattendance">
                                  //   <Dropdown.ItemDivider key={v4()} />
                                  //   <Dropdown.Item
                                  //     key={v4()}
                                  //     badge={t('schedule.classes.all_classes_in_series')}
                                  //     badgeType="secondary"
                                  //     icon="edit-2"
                                  //     onClick={() => history.push('/schedule/classes/all/edit/' + scheduleItemId)}>
                                  //       {t("general.edit")}
                                  //   </Dropdown.Item>
                                  // </HasPermissionWrapper>,
                                  // <HasPermissionWrapper key={v4()} permission="delete" resource="scheduleclass">
                                  //   <Dropdown.ItemDivider key={v4()} />
                                  //   <Mutation mutation={DELETE_SCHEDULE_CLASS} key={v4()}>
                                  //     {(deleteScheduleClass, { data }) => (
                                  //         <Dropdown.Item
                                  //           key={v4()}
                                  //           badge={t('schedule.classes.all_classes_in_series')}
                                  //           badgeType="danger"
                                  //           icon="trash-2"
                                  //           onClick={() => {
                                  //             confirm_delete({
                                  //               t: t,
                                  //               msgConfirm: t("schedule.classes.delete_confirm_msg"),
                                  //               msgDescription: <p key={v4()}>
                                  //                 {moment(date + ' ' + timeStart).format('LT')} {' - '}
                                  //                 {moment(date + ' ' + timeEnd).format('LT')} {' '} @ {' '}
                                  //                 {organizationLocationRoom.organizationLocation.name} {' '}
                                  //                 {organizationLocationRoom.name}
                                  //                 {organizationClasstype.Name}
                                  //                 </p>,
                                  //               msgSuccess: t('schedule.classes.deleted'),
                                  //               deleteFunction: deleteScheduleClass,
                                  //               functionVariables: { variables: {
                                  //                 input: {
                                  //                   id: scheduleItemId
                                  //                 }
                                  //               }, refetchQueries: [
                                  //                 { query: GET_CLASSES_QUERY, variables: get_list_query_variables() }
                                  //               ]}
                                  //             })
                                  //         }}>
                                  //         {t("general.delete")}
                                  //         </Dropdown.Item>
                                  //     )}
                                  //   </Mutation>
                                  // </HasPermissionWrapper>
                                ]}
                              />
                              <ScheduleClassAttendanceDelete node={node} />
                              {/* <Link to={"/schedule/classes/class/book/" + schedule_item_id + "/" + class_date + "/" + node.id}>
                                <Button color="secondary pull-right">
                                  {t('general.checkin')} <Icon name="chevron-right" />
                                </Button>
                              </Link>        */}
                            </Table.Col>
                          </Table.Row>
                        ))}
                    </Table.Body>
                  </Table>
                </ContentCard>
                {/* <Card>
                  <Card.Header>
                    <Card.Title>{t('general.attendance')}</Card.Title>
                  </Card.Header>
                  <Card.Body>
                    attendance list here
                  </Card.Body>
                </Card> */}
              </Grid.Col>
              <Grid.Col md={3}>
                sidebar here
                {/* <HasPermissionWrapper permission="add"
                                      resource="accountsubscription">
                  <Link to={return_url}>
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
                <ProfileMenu 
                  active_link='subscriptions'
                  account_id={match.params.account_id}
                /> */}
              </Grid.Col>
            </Grid.Row>
          </Container>
      </div>
    </SiteWrapper>
  )
}




export default withTranslation()(withRouter(ScheduleClassAttendance))



// class ScheduleClassTeachers extends Component {
//   constructor(props) {
//     super(props)
//     console.log("Schedule classs teachers props:")
//     console.log(props)
//   }

//   render() {
//     const t = this.props.t
//     const match = this.props.match
//     const history = this.props.history
//     const classId = match.params.class_id

//     // const ButtonAdd = <HasPermissionWrapper permission="add" resource="scheduleitemteacher">
//     //   <Link to={"/schedule/classes/all/teachers/" + classId + "/add" } >
//     //     <Button color="primary btn-block mb-6">
//     //     <Icon prefix="fe" name="plus-circle" /> {t('schedule.classes.teachers.add')}
//     //     </Button>
//     //   </Link>
//     // </HasPermissionWrapper>

//     return (
//       <SiteWrapper>
//       <div className="my-3 my-md-5">
//         {console.log('ID here:')}
//         {console.log(classId)}
//         <Query query={GET_SCHEDULE_CLASS_TEACHERS_QUERY} variables={{ scheduleItem: classId }}>
//           {({ loading, error, data, refetch, fetchMore }) => {
  
//             // Loading
//             if (loading) return (
//               <ClassEditBase menu_active_link="teachers" card_title={t('schedule.classes.teachers.title')} sidebar_button={ButtonAdd}>
//                 <Dimmer active={true} loader={true} />
//               </ClassEditBase>
//             )
//             // Error
//             if (error) return (
//               <ClassEditBase menu_active_link="teachers" card_title={t('schedule.classes.teachers.title')} sidebar_button={ButtonAdd}>
//                 <p>{t('schedule.classes.teachers.error_loading')}</p>
//               </ClassEditBase>
//             )
//             // const headerOptions = <Card.Options>
//             //   <Button color={(!archived) ? 'primary': 'secondary'}  
//             //           size="sm"
//             //           onClick={() => {archived=false; refetch({archived});}}>
//             //     {t('general.current')}
//             //   </Button>
//             //   <Button color={(archived) ? 'primary': 'secondary'} 
//             //           size="sm" 
//             //           className="ml-2" 
//             //           onClick={() => {archived=true; refetch({archived});}}>
//             //     {t('general.archive')}
//             //   </Button>
//             // </Card.Options>
  
//             const initialTimeStart = TimeStringToJSDateOBJ(data.scheduleItem.timeStart)
//             const subtitle = class_edit_all_subtitle({
//               t: t,
//               location: data.scheduleItem.organizationLocationRoom.organizationLocation.name,
//               locationRoom: data.scheduleItem.organizationLocationRoom.name,
//               classtype: data.scheduleItem.organizationClasstype.name,
//               starttime: initialTimeStart
//             })
  
//             // Empty list
//             if (!data.scheduleItemTeachers.edges.length) { return (
//               <ClassEditBase menu_active_link="teachers" card_title={t('schedule.classes.teachers.title')} sidebar_button={ButtonAdd}>
//                 <p>{t('schedule.classes.teachers.empty_list')}</p>
//               </ClassEditBase>
//             )} else {   
//             // Life's good! :)
//               return (
//                 <ClassEditBase 
//                   menu_active_link="teachers" 
//                   default_card={false} 
//                   subtitle={subtitle}
//                   sidebar_button={ButtonAdd}
//                 >
//                 <ContentCard 
//                   cardTitle={t('schedule.classes.title_edit')}
//                   // headerContent={headerOptions}
//                   pageInfo={data.scheduleItemTeachers.pageInfo}
//                   onLoadMore={() => {
//                   fetchMore({
//                     variables: {
//                       after: data.scheduleItemTeachers.pageInfo.endCursor
//                     },
//                     updateQuery: (previousResult, { fetchMoreResult }) => {
//                       const newEdges = fetchMoreResult.scheduleItemTeachers.edges
//                       const pageInfo = fetchMoreResult.scheduleItemTeachers.pageInfo
  
//                       return newEdges.length
//                         ? {
//                             // Put the new locations at the end of the list and update `pageInfo`
//                             // so we have the new `endCursor` and `hasNextPage` values
//                             data: { 
//                               scheduleItemTeachers: {
//                                 __typename: previousResult.scheduleItemTeachers.__typename,
//                                 edges: [ ...previousResult.scheduleItemTeachers.edges, ...newEdges ],
//                                 pageInfo
//                               }
//                             }
//                           }
//                         : previousResult
//                       }
//                     })
//                   }} >
//                   <div>
//                     <Table>
//                       <Table.Header>
//                         <Table.Row>
//                           <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
//                           <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
//                           <Table.ColHeader>{t('general.teacher')}</Table.ColHeader>
//                           <Table.ColHeader>{t('general.teacher_2')}</Table.ColHeader>
//                           <Table.ColHeader></Table.ColHeader>
//                           <Table.ColHeader></Table.ColHeader>
//                         </Table.Row>
//                       </Table.Header>
//                       <Table.Body>
//                         {data.scheduleItemTeachers.edges.map(({ node }) => (
//                           <Table.Row key={v4()}>
//                             {console.log(node)}
//                             <Table.Col key={v4()}> 
//                               {moment(node.dateStart).format('LL')}
//                             </Table.Col>
//                             <Table.Col key={v4()}> 
//                               {(node.dateEnd) ? moment(node.dateEnd).format('LL') : ""}
//                             </Table.Col>
//                             <Table.Col>
//                               {node.account.fullName} <br />
//                               <span className="text-muted">
//                                 {represent_teacher_role(t, node.role)}
//                               </span>
//                             </Table.Col>
//                             <Table.Col>
//                               {node.account2 ?
//                                 <span>
//                                   {node.account2.fullName} <br />
//                                   <span className="text-muted">
//                                     {represent_teacher_role(t, node.role2)}
//                                   </span>
//                                 </span> : ""
//                               }
//                             </Table.Col>
//                             <Table.Col className="text-right" key={v4()}>
//                               <Button className='btn-sm' 
//                                       onClick={() => history.push("/schedule/classes/all/teachers/" + match.params.class_id + '/edit/' + node.id)}
//                                       color="secondary">
//                                 {t('general.edit')}
//                               </Button>
//                             </Table.Col>
//                             <Mutation mutation={DELETE_SCHEDULE_CLASS_TEACHER} key={v4()}>
//                               {(deleteScheduleItemTeacher, { data }) => (
//                                 <Table.Col className="text-right" key={v4()}>
//                                   <button className="icon btn btn-link btn-sm" 
//                                       title={t('general.delete')} 
//                                       href=""
//                                       onClick={() => {
//                                         confirm_delete({
//                                           t: t,
//                                           msgConfirm: t('schedule.classes.teachers.delete_confirm_msg'),
//                                           msgDescription: <p>{t('schedule.classes.teachers.delete_confirm_description')}</p>,
//                                           msgSuccess: t('schedule.classes.teachers.deleted'),
//                                           deleteFunction: deleteScheduleItemTeacher,
//                                           functionVariables: { variables: {
//                                             input: {
//                                               id: node.id
//                                             }
//                                           }, refetchQueries: [
//                                             {query: GET_SCHEDULE_CLASS_TEACHERS_QUERY, variables: { scheduleItem: match.params.class_id }}
//                                           ]}
//                                       })}}
//                                   >
//                                     <span className="text-red">
//                                       <Icon prefix="fe" name="trash-2" />
//                                     </span>
//                                   </button>
//                                 </Table.Col>
//                               )}
//                             </Mutation>
//                           </Table.Row>
//                         ))}
//                       </Table.Body>
//                     </Table>
//                     </div>
//                   </ContentCard>
//                 </ClassEditBase>
//             )}}
//           }
//         </Query>
//       </div>
//     </SiteWrapper>
//     )
//   }

// };

// export default withTranslation()(withRouter(ScheduleClassTeachers))