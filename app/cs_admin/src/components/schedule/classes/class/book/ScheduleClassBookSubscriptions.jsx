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
import SubscriptionCheckinButton from "./ScheduleClassBookSubscriptionBtn"

import { GET_BOOKING_OPTIONS_QUERY } from "./queries"
import CSLS from "../../../../../tools/cs_local_storage"



function ScheduleClassBookSubscriptions({ 
  t, 
  match, 
  history, 
  subscriptions, 
  locationId,
  returnTo="schedule_classes"
}) {

  return (
    subscriptions.map((subscription) =>(
      <Grid.Col md={3}>
        <Card 
          statusColor="blue"
          title={t("general.subscription")} >
        <Card.Body>
          <b>{subscription.accountSubscription.organizationSubscription.name}</b><br />
          <span className="text-muted">
            {t("general.credits_remaining")}: {subscription.accountSubscription.creditTotal}
          </span>
        </Card.Body>
        <Card.Footer>
          {(!subscription.allowed) ? t('schedule.classes.class.book.subscription_not_allowed') :
            <SubscriptionCheckinButton subscription={subscription} returnTo={returnTo} locationId={locationId} />
          }
        </Card.Footer>
        </Card>
      </Grid.Col>
    ))
  )
}


export default withTranslation()(withRouter(ScheduleClassBookSubscriptions))

