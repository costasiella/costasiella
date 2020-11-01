// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'

import { GET_SCHEDULE_EVENTS_QUERY, GET_SCHEDULE_EVENT_QUERY } from '../queries'
// import { LEVEL_SCHEMA } from '../yupSchema'


import {
  Dimmer,
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import ScheduleEventEditBase from "./ScheduleEventEditBase"


const UPDATE_SCHEDULE_EVENT = gql`
  mutation UpdateScheduleEvent($input: UpdateScheduleEventInput!) {
    updateScheduleEvent(input: $input) {
      scheduleEvent {
        id
        name
      }
    }
  }
`

function ScheduleEventEdit({t, match, history}) {
  const id = match.params.id
  const returnUrl = "/schedule/events"
  const activeTab = "general"

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_QUERY, {
    variables: { id: id }
  })
  const [ updateScheduleEvent ] = useMutation(UPDATE_SCHEDULE_EVENT)


  if (loading) {
    return (
      <ScheduleEventEditBase activeTab={activeTab}>
        <Card.Body>
          <Dimmer loading={true} active={true} />
        </Card.Body>
      </ScheduleEventEditBase>
    )
  }

  if (error) {
    return (
      <ScheduleEventEditBase activeTab={activeTab}>
        <Card.Body>
          {t("schedule.events.error_loading")}
        </Card.Body>
      </ScheduleEventEditBase>
    )
  }

  const event = data.scheduleEvent

  return (
    <ScheduleEventEditBase activeTab={activeTab}>
      <Card.Body>
        hello world
      </Card.Body>
    </ScheduleEventEditBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventEdit))