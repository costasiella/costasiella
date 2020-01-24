// @flow

import React, { useContext } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'

import moment from 'moment'

import {
  Button,
  Card,
  Icon,
  Table
} from "tabler-react";
import SelfCheckinBase from "../SelfCheckinBase"

import AppSettingsContext from '../../context/AppSettingsContext'

import HasPermissionWrapper from "../../HasPermissionWrapper"
import { GET_LOCATION_CLASSES_QUERY } from "./queries"


function LocationClasses({ t, match, history }) {
  const locationId = match.params.location_id
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const today = moment().format('YYYY-MM-DD')

  const { loading, error, data } = useQuery(GET_LOCATION_CLASSES_QUERY, {
    variables: {
      dateFrom: today,
      dateUntil: today,
      organizationLocation: locationId,
    }
  })

  if (loading) return (
    <SelfCheckinBase>
      {t("general.loading_with_dots")}
    </SelfCheckinBase>
  )
  if (error) return (
    <SelfCheckinBase>
      {t("selfcheckin.classes.error_loading")}
    </SelfCheckinBase>
  )

  console.log(data)

  return (
    <SelfCheckinBase title={t("selfcheckin.classes.title")}>
      <Card>
      <Table>
        <Table.Header>
          <Table.Row>
            <Table.ColHeader>
              { t("general.time") }
            </Table.ColHeader>
            <Table.ColHeader>
              { t("general.room") }
            </Table.ColHeader>
            <Table.ColHeader>
              { t("general.class") }
            </Table.ColHeader>
            <Table.ColHeader>
              { t("general.teacher") }
            </Table.ColHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {
            data.scheduleClasses.map(({ date, classes }) => 
              classes.map((
                { scheduleItemId, 
                  frequencyType,
                  date, 
                  status,
                  description,
                  account, 
                  role,
                  account2,
                  role2,
                  organizationLocationRoom, 
                  organizationClasstype, 
                  organizationLevel,
                  timeStart, 
                  timeEnd,
                  displayPublic }) => (
                    // console.log(scheduleItemId)
                    <Table.Row>
                      <Table.Col>
                        {moment(date + ' ' + timeStart).format(timeFormat)} {' - '}
                        {moment(date + ' ' + timeEnd).format(timeFormat)}
                      </Table.Col>
                      <Table.Col>
                        { organizationLocationRoom.name }
                      </Table.Col>
                      <Table.Col>
                        { organizationClasstype.name }
                      </Table.Col>
                      <Table.Col>
                        {/* Teacher(s) */}
                        { (account) ? account.fullName : 
                          <span className="text-red">{t("schedule.classes.no_teacher")}</span>
                        }
                      </Table.Col>
                      <Table.Col>
                        <Link to={"/selfcheckin/location/" + locationId + "/" + scheduleItemId + "/" + date}>
                          <Button color="secondary" className="pull-right">
                            {t("selfcheckin.classes.go_to_checkin")}
                            <Icon name="chevron-right" />
                          </Button>
                        </Link>
                      </Table.Col>
                    </Table.Row>
                  )
                )
            )
          }
        </Table.Body>
      </Table>
      </Card>
    </SelfCheckinBase>
  )
}


export default withTranslation()(withRouter(LocationClasses))