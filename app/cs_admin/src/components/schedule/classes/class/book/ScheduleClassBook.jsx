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
import confirm_delete from "../../../../../tools/confirm_delete"

import { class_subtitle, get_accounts_query_variables } from "../tools"

import ContentCard from "../../../../general/ContentCard"
import ScheduleClassBookBack from "./ScheduleClassBookBack"
// import ClassEditBase from "../ClassEditBase"

import { GET_BOOKING_OPTIONS_QUERY } from "./queries"
import CSLS from "../../../../../tools/cs_local_storage"

const DELETE_SCHEDULE_CLASS_TEACHER = gql`
  mutation DeleteScheduleClassTeacher($input: DeleteScheduleItemTeacherInput!) {
    deleteScheduleItemTeacher(input: $input) {
      ok
    }
  }
`


function ScheduleClassBook({ t, match, history }) {
  const [showSearch, setShowSearch] = useState(false)
  const return_url = "/schedule/classes/"
  const account_id = match.params.account_id
  const schedule_item_id = match.params.class_id
  const class_date = match.params.date
  const { loading: queryLoading, error: queryError, data: queryData } = useQuery(
    GET_BOOKING_OPTIONS_QUERY, {
      variables: {
        account: account_id,
        scheduleItem: schedule_item_id,
        date: class_date,
        listType: "attend"
      }
    }
  )

  // Query
  // Loading
  if (queryLoading) return <p>{t('general.loading_with_dots')}</p>
  // Error
  if (queryError) {
    console.log(queryError)
    return <p>{t('general.error_sad_smiley')}</p>
  }
  
  console.log(queryData)
  const scheduleItem = queryData.scheduleClassBookingOptions.scheduleItem
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
              <ScheduleClassBookBack classId={schedule_item_id} date={class_date} />
            </div>
          </Page.Header>
          <Grid.Row>
              <Grid.Col md={9}>
                <Card>
                  <Card.Header>
                    <Card.Title>{t('general.booking_options')}</Card.Title>
                  </Card.Header>
                  <Card.Body>
                    attendance list here
                  </Card.Body>
                </Card>
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




export default withTranslation()(withRouter(ScheduleClassBook))

