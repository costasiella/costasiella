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
  Table,
  StampCard
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



function ScheduleClassBookClasspasses({ t, match, history, classpasses, onClickCheckin=f=>f }) {
  console.log('classpasses')
  console.log(classpasses)

  return (
    classpasses.map((classpass) =>(
      <Grid.Col md={4}>
        <Card 
          statusColor="blue"
          title={t("general.classpass")} >
        <Card.Body>
          <b>{classpass.accountClasspass.organizationClasspass.name}</b><br />
          details here
        </Card.Body>
        <Card.Footer>
          {(!classpass.allowed) ? t('schedule.classes.class.book.classpass_not_allowed') :
            <Button 
              block 
              outline 
              color="success" 
              icon="check"
            >
              {t("general.checkin")}
            </Button>
          }
        </Card.Footer>
        </Card>
      </Grid.Col>
    ))
  )
}


export default withTranslation()(withRouter(ScheduleClassBookClasspasses))

