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
  List,
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
import ClasspassCheckinButton from "./ScheduleClassBookClasspassBtn"

// import ClassEditBase from "../ClassEditBase"

import { GET_BOOKING_OPTIONS_QUERY, CREATE_SCHEDULE_ITEM_ATTENDANCE } from "./queries"
import CSLS from "../../../../../tools/cs_local_storage"


function ScheduleClassBookClasspasses({ t, match, history, classpasses, onClickCheckin=f=>f }) {
  console.log('classpasses')
  console.log(classpasses)

  return (
    classpasses.map((classpass) =>(
      <Grid.Col md={3}>
        <Card 
          statusColor="blue"
          title={t("general.classpass")} >
        <Card.Body>
          <b>{classpass.accountClasspass.organizationClasspass.name}</b><br />
          <span className="text-muted">
            {t('general.classes_remaining')}: {classpass.accountClasspass.classesRemainingDisplay} <br />
            {t('general.valid_until')}: {moment(classpass.accountClasspass.dateEnd).format('LL')} <br />
          </span>
        </Card.Body>
        <Card.Footer>
          {(!classpass.allowed) ? t('schedule.classes.class.book.classpass_not_allowed') :
            <ClasspassCheckinButton classpass={classpass} />
            // <Button 
            //   block 
            //   outline 
            //   color="success" 
            //   icon="check"
            //   onClick={() => onClickCheckin({classpass: classpass})}
            // >
            //   {t("general.checkin")}
            // </Button>
          }
        </Card.Footer>
        </Card>
      </Grid.Col>
    ))
  )
}


export default withTranslation()(withRouter(ScheduleClassBookClasspasses))

