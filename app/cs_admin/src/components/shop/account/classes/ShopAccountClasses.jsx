// @flow

import React, { useContext } from 'react'
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import { Link } from 'react-router-dom'
import moment from 'moment'

import AppSettingsContext from '../../../context/AppSettingsContext'
import BadgeBookingStatus from '../../../ui/BadgeBookingStatus'

import {
  Button,
  Card,
  Grid,
  Icon,
  Table
} from "tabler-react"
import { GET_ACCOUNT_CLASSES_QUERY } from "./queries"
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"

import ShopAccountClassesBase from "./ShopAccountClassesBase"
import ContentCard from "../../../general/ContentCard"


function ShopAccountClasses({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const dateTimeFormat = dateFormat + ' ' + timeFormat

  // Chain queries. First query user data and then query class attendance for that user once we have the account Id.
  const { loading: loadingUser, error: errorUser, data: dataUser } = useQuery(GET_USER_PROFILE)
  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_CLASSES_QUERY, {
    skip: loadingUser || errorUser || !dataUser,
    variables: {
      account: dataUser && dataUser.user ? dataUser.user.accountId : null
    }
  })
  // TODO: add cancel class button & query
  // const [ updateOrder ] = useMutation(UPDATE_ORDER)

  if (loading || loadingUser || !data) return (
    <ShopAccountClassesBase>
      {t("general.loading_with_dots")}
    </ShopAccountClassesBase>
  )
  if (error || errorUser) return (
    <ShopAccountClassesBase>
      {t("shop.account.classes.error_loading_data")}
    </ShopAccountClassesBase>
  )

  console.log("User data: ###")
  console.log(data)
  console.log(dataUser)
  const user = dataUser.user
  const scheduleItemAttendances = data.scheduleItemAttendances

  // Empty list
  if (!scheduleItemAttendances.edges.length) {
    return (
      <ShopAccountClassesBase accountName={user.fullName}>
        <Grid.Row>
          <Grid.Col md={12}>
            <Card cardTitle={t('shop.account.classes.title')} >
              <Card.Body>
                {t('shop.account.classes.empty_list')}
              </Card.Body>
            </Card>
          </Grid.Col>
        </Grid.Row>
      </ShopAccountClassesBase>
    )  
  }



  // Populated list
  return (
    <ShopAccountClassesBase accountName={user.fullName}>
      <Grid.Row>
        <Grid.Col md={12}>
          <ContentCard cardTitle={t('shop.account.classes.title')}
            // headerContent={headerOptions}
            pageInfo={scheduleItemAttendances.pageInfo}
            onLoadMore={() => {
              fetchMore({
                variables: {
                  after: scheduleItemAttendances.pageInfo.endCursor
                },
                updateQuery: (previousResult, { fetchMoreResult }) => {
                  const newEdges = fetchMoreResult.schduleItemAttendances.edges
                  const pageInfo = fetchMoreResult.schduleItemAttendances.pageInfo

                  return newEdges.length
                    ? {
                        // Put the new subscriptions at the end of the list and update `pageInfo`
                        // so we have the new `endCursor` and `hasNextPage` values
                        schduleItemAttendances: {
                          __typename: previousResult.schduleItemAttendances.__typename,
                          edges: [ ...previousResult.schduleItemAttendances.edges, ...newEdges ],
                          pageInfo
                        }
                      }
                    : previousResult
                }
              })
            }} >
            <Table>
              <Table.Header>
                <Table.Row key={v4()}>
                  <Table.ColHeader>{t('general.time')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.class')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.location')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.booking_status')}</Table.ColHeader>
                  <Table.ColHeader></Table.ColHeader>  
                </Table.Row>
              </Table.Header>
              <Table.Body>
                { scheduleItemAttendances.edges.map(({ node }) => (
                  <Table.Row key={v4()}>
                    <Table.Col>
                      { moment(node.date).format(dateFormat) } <br />
                      <span className="text-muted">
                        {moment(node.date + ' ' + node.scheduleItem.timeStart).format(timeFormat)}
                      </span>
                    </Table.Col>
                    <Table.Col>
                      { node.scheduleItem.organizationClasstype.name }
                    </Table.Col>
                    <Table.Col>
                      { node.scheduleItem.organizationLocationRoom.organizationLocation.name } <br />
                      <span className="text-muted">
                        { node.scheduleItem.organizationLocationRoom.name }
                      </span> 
                    </Table.Col>
                    <Table.Col>
                      <BadgeBookingStatus status={node.bookingStatus} />
                    </Table.Col>
                    <Table.Col>
                      {/* TODO: improve this by adding a "Can be cancelled field to GQL schema" */}
                      {((node.bookingStatus != "CANCELLED") && node.cancellationPossible) ?  
                        <div>
                          <Link to={`/shop/account/class_cancel/${node.scheduleItem.id}/${node.date}/${node.id}`}>
                            <Button 
                              className="pull-right mr-r"
                              color="warning"
                              >
                              {t("general.cancel")}
                            </Button>
                          </Link>
                          <Link to={`/shop/account/class_info/${node.scheduleItem.id}/${node.date}`}>
                            <Button
                              className="pull-right"
                              color="secondary"
                              icon="info"
                            >
                              {t("general.info")}
                            </Button>
                          </Link>
                        </div> : ""
                      }
                    </Table.Col>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </ContentCard>
        </Grid.Col>
      </Grid.Row>
    </ShopAccountClassesBase>
  )
}


export default withTranslation()(withRouter(ShopAccountClasses))