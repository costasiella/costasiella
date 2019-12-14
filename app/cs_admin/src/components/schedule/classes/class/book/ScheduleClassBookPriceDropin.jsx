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
import ScheduleClassBookPriceBtn from "./ScheduleClassBookPriceBtn"

// import ClassEditBase from "../ClassEditBase"

import { GET_BOOKING_OPTIONS_QUERY, CREATE_SCHEDULE_ITEM_ATTENDANCE } from "./queries"
import CSLS from "../../../../../tools/cs_local_storage"


function ScheduleClassBookPriceDropin({ t, match, history, priceDropin, onClickCheckin=f=>f }) {
  console.log('priceDropin')
  console.log(priceDropin)

  return (
    <Grid.Col md={3}>
      <Card 
        statusColor="blue"
        title={t("general.dropin")} >
      <Card.Body>
        <b>{priceDropin.priceDisplay}</b><br />
        {t("schedule.classes.class.book.dropin_pay_and_book")} <br />

        
          {/* {t('general.valid_until')}: {moment(classpass.accountClasspass.dateEnd).format('LL')} <br /> */}
      </Card.Body>
      <Card.Footer>
        <ScheduleClassBookPriceBtn priceDropin={priceDropin} />
        {/* {(!classpass.allowed) ? t('schedule.classes.class.book.classpass_not_allowed') :
          <ClasspassCheckinButton classpass={classpass} />
        } */}
      </Card.Footer>
      </Card>
    </Grid.Col>
  )
}


export default withTranslation()(withRouter(ScheduleClassBookPriceDropin))

