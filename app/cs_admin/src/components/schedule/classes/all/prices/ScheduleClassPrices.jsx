// @flow

import React, { useContext } from 'react'
import { Query, Mutation, useQuery } from "react-apollo"
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
import { TimeStringToJSDateOBJ } from '../../../../../tools/date_tools'
import AppSettingsContext from '../../../../context/AppSettingsContext'
import ButtonAdd from "./ButtonAdd"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'
import { class_edit_all_subtitle } from "../tools"
import confirm_delete from "../../../../../tools/confirm_delete"

import ContentCard from "../../../../general/ContentCard"
import ClassEditBase from "../ClassEditBase"
import ScheduleClassPriceDelete from './ScheduleClassPriceDelete'

import { GET_SCHEDULE_ITEM_PRICES_QUERY } from "./queries"


function ScheduleClassPrices({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const classId = match.params.class_id

  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_ITEM_PRICES_QUERY, {
    variables: { scheduleItem: classId }
  })

  if (loading) return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <ClassEditBase menu_active_link="prices" card_title={t('schedule.classes.prices.title')} sidebar_button={<ButtonAdd classId={classId}/>}>
          <Dimmer active={true} loader={true} />
        </ClassEditBase>
      </div>
    </SiteWrapper>
  )
  // Error
  if (error) return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <ClassEditBase menu_active_link="prices" card_title={t('schedule.classes.prices.title')} sidebar_button={<ButtonAdd classId={classId}/>}>
          <p>{t('schedule.classes.prices.error_loading')}</p>
        </ClassEditBase>
      </div>
    </SiteWrapper>
  )


  const initialTimeStart = TimeStringToJSDateOBJ(data.scheduleItem.timeStart)
  const subtitle = class_edit_all_subtitle({
    t: t,
    location: data.scheduleItem.organizationLocationRoom.organizationLocation.name,
    locationRoom: data.scheduleItem.organizationLocationRoom.name,
    classtype: data.scheduleItem.organizationClasstype.name,
    starttime: initialTimeStart
  })

  // Empty list
  if (!data.scheduleItemPrices.edges.length) { return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <ClassEditBase menu_active_link="prices" card_title={t('schedule.classes.prices.title')} sidebar_button={<ButtonAdd classId={classId}/>}>
          <p>{t('schedule.classes.prices.empty_list')}</p>
        </ClassEditBase>
      </div>
    </SiteWrapper>
  )}

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        {console.log('ID here:')}
        {console.log(classId)}

        <ClassEditBase 
          menu_active_link="prices" 
          default_card={false} 
          subtitle={subtitle}
          sidebar_button={<ButtonAdd classId={classId}/>}
        >
        <ContentCard 
          cardTitle={t('schedule.classes.title_edit')}
          // headerContent={headerOptions}
          pageInfo={data.scheduleItemPrices.pageInfo}
          onLoadMore={() => {
          fetchMore({
            variables: {
              after: data.scheduleItemPrices.pageInfo.endCursor
            },
            updateQuery: (previousResult, { fetchMoreResult }) => {
              const newEdges = fetchMoreResult.scheduleItemPrices.edges
              const pageInfo = fetchMoreResult.scheduleItemPrices.pageInfo

              return newEdges.length
                ? {
                    // Put the new locations at the end of the list and update `pageInfo`
                    // so we have the new `endCursor` and `hasNextPage` values
                    data: { 
                      scheduleItemPrices: {
                        __typename: previousResult.scheduleItemPrices.__typename,
                        edges: [ ...previousResult.scheduleItemPrices.edges, ...newEdges ],
                        pageInfo
                      }
                    }
                  }
                : previousResult
              }
            })
          }} >
          <div>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.dropin')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.trial')}</Table.ColHeader>
                  <Table.ColHeader></Table.ColHeader>
                  <Table.ColHeader></Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {data.scheduleItemPrices.edges.map(({ node }) => (
                  <Table.Row key={v4()}>
                    {console.log(node)}
                    <Table.Col key={v4()}> 
                      {moment(node.dateStart).format('LL')}
                    </Table.Col>
                    <Table.Col key={v4()}> 
                      {(node.dateEnd) ? moment(node.dateEnd).format('LL') : ""}
                    </Table.Col>
                    <Table.Col>
                      {node.organizationClasspassDropin.name}
                    </Table.Col>
                    <Table.Col>
                      {(node.organizationClasspassTrial) ? node.organizationClasspassTrial.name : ""}
                    </Table.Col>
                    <Table.Col className="text-right" key={v4()}>
                      <Button className='btn-sm' 
                              onClick={() => history.push("/schedule/classes/all/prices/" + match.params.class_id + '/edit/' + node.id)}
                              color="secondary">
                        {t('general.edit')}
                      </Button>
                    </Table.Col>
                    <Table.Col>
                      <ScheduleClassPriceDelete id={node.id} />
                    </Table.Col>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
            </div>
          </ContentCard>
        </ClassEditBase>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(ScheduleClassPrices))