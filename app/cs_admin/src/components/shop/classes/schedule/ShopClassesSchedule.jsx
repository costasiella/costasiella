// @flow

import React, { useContext } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'
import moment from 'moment'

import CSLS from "../../../../tools/cs_local_storage"
import AppSettingsContext from '../../../context/AppSettingsContext'

import {
  Button,
  Card, 
  Grid,
  Icon,
  List,
  Media,
  Table,
} from "tabler-react";
import ShopClassesScheduleBase from "./ShopClassesScheduleBase"
import CSDatePicker from "../../../ui/CSDatePicker"

import { GET_CLASSES_QUERY } from "../../../schedule/classes/queries"

import { get_list_query_variables } from './tools'



// Set some initial values for dates, if not found
if (!localStorage.getItem(CSLS.SHOP_CLASSES_DATE_FROM)) {
  console.log('date from not found... defaulting to today...')
  localStorage.setItem(CSLS.SHOP_CLASSES_DATE_FROM, moment().format('YYYY-MM-DD')) 
  localStorage.setItem(CSLS.SHOP_CLASSES_DATE_UNTIL, moment().add(6, 'days').format('YYYY-MM-DD')) 
} 



function ShopClassesSchedule({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const title = t("shop.home.title")
  const { loading, error, data, refetch } = useQuery(GET_CLASSES_QUERY, {
    variables: get_list_query_variables()
  })

  if (loading) return (
    <ShopClassesScheduleBase title={title} >
      {t("general.loading_with_dots")}
    </ShopClassesScheduleBase>
  )
  if (error) return (
    <ShopClassesScheduleBase title={title}>
      {t("shop.classpasses.error_loading")}
    </ShopClassesScheduleBase>
  )

  console.log(data)
  console.log(data.scheduleClasses)

  return (
    <ShopClassesScheduleBase 
      title={title}
      pageHeaderOptions={
        <Button.List className="schedule-list-page-options-btn-list">
          <Button 
            icon="chevron-left"
            color="secondary"
            onClick={ () => {
              let nextWeekFrom = moment(localStorage.getItem(CSLS.SHOP_CLASSES_DATE_FROM)).subtract(7, 'days')
              let nextWeekUntil = moment(nextWeekFrom).add(6, 'days')
              
              localStorage.setItem(CSLS.SHOP_CLASSES_DATE_FROM, nextWeekFrom.format('YYYY-MM-DD')) 
              localStorage.setItem(CSLS.SHOP_CLASSES_DATE_UNTIL, nextWeekUntil.format('YYYY-MM-DD')) 

              refetch(get_list_query_variables())
          }} />
          <Button 
            color="secondary"
            onClick={ () => {
              let currentWeekFrom = moment()
              let currentWeekUntil = moment(currentWeekFrom).add(6, 'days')

              localStorage.setItem(CSLS.SHOP_CLASSES_DATE_FROM, currentWeekFrom.format('YYYY-MM-DD')) 
              localStorage.setItem(CSLS.SHOP_CLASSES_DATE_UNTIL, currentWeekUntil.format('YYYY-MM-DD')) 
              
              refetch(get_list_query_variables())
          }} > 
            {t("general.today")}
          </Button>
          <Button 
            icon="chevron-right"
            color="secondary"
            onClick={ () => {
              let nextWeekFrom = moment(localStorage.getItem(CSLS.SHOP_CLASSES_DATE_FROM)).add(7, 'days')
              let nextWeekUntil = moment(nextWeekFrom).add(6, 'days')
              
              localStorage.setItem(CSLS.SHOP_CLASSES_DATE_FROM, nextWeekFrom.format('YYYY-MM-DD')) 
              localStorage.setItem(CSLS.SHOP_CLASSES_DATE_UNTIL, nextWeekUntil.format('YYYY-MM-DD')) 

              refetch(get_list_query_variables())
          }} />
        </Button.List> 
      }
    >
        
      {data.scheduleClasses.map(({ date, classes }) =>
        <Grid.Row key={v4()}>
          <Grid.Col md={12}>
              <Card>
                <Card.Header>
                  <Card.Title>
                    <b>{moment(date).format("dddd")}</b> {' '}
                    <span className="text-muted">
                      {moment(date).format("LL")} 
                    </span>
                  </Card.Title>
                </Card.Header>                
                {!(classes.length) ? 
                  <Card.Body>
                    <p>{t('schedule.classes.empty_list')}</p>
                  </Card.Body> :
                  <Table cards>
                    <Table.Body>
                      {classes.map(({ 
                        scheduleItemId, 
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
                          <Table.Row>
                            <Table.Col>
                            <h4>
                              {moment(date + ' ' + timeStart).format(timeFormat)} {' - '}
                              {moment(date + ' ' + timeEnd).format(timeFormat)} { ' ' }
                            </h4> 
                            { organizationClasstype.name } { (account) ? ' ' + t("general.with") + ' ' + account.fullName : "" } <br />
                            <span className="text-muted">{ organizationLocationRoom.organizationLocation.name }</span>
                            </Table.Col>
                            <Table.Col>
                              <Button className="pull-right" color="primary" outline>
                                Book <Icon name="chevron-right" />
                              </Button>
                            </Table.Col>
                          </Table.Row>
                        )
                      )}
                    </Table.Body>
                  </Table>
                }
              </Card>
          </Grid.Col>
        </Grid.Row>
      )}

    </ShopClassesScheduleBase>
  )
}


export default withTranslation()(withRouter(ShopClassesSchedule))
