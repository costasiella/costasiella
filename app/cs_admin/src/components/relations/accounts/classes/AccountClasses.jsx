// @flow

import React, { useContext } from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import moment from 'moment'

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
import BadgeBookingStatus from "../../../ui/BadgeBookingStatus"
import RelationsAccountsBack from "../RelationsAccountsBack"
import confirm_delete from "../../../../tools/confirm_delete"


import ContentCard from "../../../general/ContentCard"
import ProfileMenu from "../ProfileMenu"
import ProfileCardSmall from "../../../ui/ProfileCardSmall"
import AccountClassesBase from "./AccountClassesBase"

import { GET_ACCOUNT_CLASSES_QUERY } from "./queries"

const DELETE_ACCOUNT_CLASS = gql`
  mutation DeleteScheduleItemAttendance($input: DeleteScheduleItemAttendanceInput!) {
    DeleteScheduleItemAttendance(input: $input) {
      ok
    }
  }
`

function AccountClasses({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormat
  const account_id = match.params.account_id
  const { loading, error, data } = useQuery(GET_ACCOUNT_CLASSES_QUERY, {
    variables: {'account': account_id},
  })

  // Loading
  if (loading) return (
    <AccountClassesBase>
      <p>{t('general.loading_with_dots')}</p>
    </AccountClassesBase>
  )
  // Error
  if (error) {
    console.log(error)
    return (
      <AccountClassesBase>
        <p>{t('general.error_sad_smiley')}</p>
      </AccountClassesBase>
    )
  }

  console.log("AccountClasses data:")
  console.log(data)
  const account = data.account
  const scheduleItemAttendances = data.scheduleItemAttendances
  
  // Empty list
  if (!scheduleItemAttendances.edged.length) {
    return (
      <AccountClassesBase>
        <p>{t('relations.account.classes.empty_list')}</p>
      </AccountClassesBase>
    )
  }

  // Return populated list
  return (
    <AccountClassesBase>
      <ContentCard 
        cardTitle={t('relations.account.classes.title')}
        pageInfo={scheduleItemAttendances.pageInfo}
        onLoadMore={() => {
          fetchMore({
            variables: {
              after: scheduleItemAttendances.pageInfo.endCursor
            },
            updateQuery: (previousResult, { fetchMoreResult }) => {
              const newEdges = fetchMoreResult.scheduleItemAttendances.edges
              const pageInfo = fetchMoreResult.scheduleItemAttendances.pageInfo

              return newEdges.length
                ? {
                    // Put the new scheduleItemAttendances at the end of the list and update `pageInfo`
                    // so we have the new `endCursor` and `hasNextPage` values
                    scheduleItemAttendances: {
                      __typename: previousResult.scheduleItemAttendances.__typename,
                      edges: [ ...previousResult.scheduleItemAttendances.edges, ...newEdges ],
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
              <Table.ColHeader>{t('general.date')}</Table.ColHeader>
              <Table.ColHeader>{t('general.time')}</Table.ColHeader>
              <Table.ColHeader>{t('general.class')}</Table.ColHeader>
              <Table.ColHeader>{t('general.location')}</Table.ColHeader>
              <Table.ColHeader>{t('general.booking_status')}</Table.ColHeader>
              <Table.ColHeader></Table.ColHeader>  
            </Table.Row>
          </Table.Header>
          <Table.Body>
              {scheduleItemAttendances.edges.map(({ node }) => (
                <Table.Row key={v4()}>
                  <Table.Col>
                    { moment(node.date).format(dateFormat) }
                  </Table.Col>
                  <Table.Col>
                    { moment(node.scheduleItem.timeStart).format(timeFormat) }
                  </Table.Col>
                  <Table.Col>
                    { node.scheduleItem.organizationClasstype.name }
                  </Table.Col>
                  <Table.Col>
                    { node.scheduleItem.organizationLocationRoom.organnizationLocation.name } <br />
                    <span className="text-muted">
                      { node.scheduleItem.organizationLocationRoom.name }
                    </span> 
                  </Table.Col>
                  {/* <Table.Col className="text-right" key={v4()}>
                    <Link to={"/relations/accounts/" + match.params.account_id + "/classpasses/edit/" + node.id}>
                      <Button className='btn-sm' 
                              color="secondary">
                        {t('general.edit')}
                      </Button>
                    </Link>
                  </Table.Col> */}
                  {/* <Mutation mutation={DELETE_ACCOUNT_CLASSPASS} key={v4()}>
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
                  </Mutation> */}
                </Table.Row>
              ))}
          </Table.Body>
        </Table>
      </ContentCard>
    </AccountClassesBase>
  )
}




// const scheduleItemAttendances = ({ t, history, match, archived=false }) => (
//   <SiteWrapper>
//     <div className="my-3 my-md-5">
//       <Query query={GET_ACCOUNT_CLASSPASSES_QUERY} variables={{ archived: archived, accountId: match.params.account_id }} pollInterval={5000}> 
//         {({ loading, error, data, refetch, fetchMore }) => {
//           // Loading
//           if (loading) return <p>{t('general.loading_with_dots')}</p>
//           // Error
//           if (error) {
//             console.log(error)
//             return <p>{t('general.error_sad_smiley')}</p>
//           }

//           const account = data.account
//           const scheduleItemAttendances = data.scheduleItemAttendances

//           return (
//             <Container>
//               <Page.Header title={account.firstName + " " + account.lastName} >
//                 <RelationsAccountsBack />
//               </Page.Header>
//               <Grid.Row>
//                 <Grid.Col md={9}>

//                 </Grid.Col>
//                 <Grid.Col md={3}>
//                   <ProfileCardSmall user={account}/>
//                   <HasPermissionWrapper permission="add"
//                                         resource="accountclasspass">
//                     <Link to={"/relations/accounts/" + match.params.account_id + "/classpasses/add"}>
//                       <Button color="primary btn-block mb-6">
//                               {/* //  onClick={() => history.push("/organization/classpasses/add")}> */}
//                         <Icon prefix="fe" name="plus-circle" /> {t('relations.account.classpasses.add')}
//                       </Button>
//                     </Link>
//                   </HasPermissionWrapper>
//                   <ProfileMenu 
//                     active_link='classpasses' 
//                     account_id={match.params.account_id}
//                   />
//                 </Grid.Col>
//               </Grid.Row>
//             </Container>
//           )
//         }}
//       </Query>
//     </div>
//   </SiteWrapper>
// )
      
        
export default withTranslation()(withRouter(scheduleItemAttendances))