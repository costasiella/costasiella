// @flow

import React, { useContext } from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import { Link } from 'react-router-dom'
import moment from 'moment'

import AppSettingsContext from '../../../context/AppSettingsContext'
import FinanceInvoicesStatus from "../../../ui/FinanceInvoiceStatus"

import {
  Button,
  Card,
  Grid,
  Icon,
  Table
} from "tabler-react"
import { QUERY_ACCOUNT_INVOICES } from "./queries"
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"

import ShopAccountInvoicesBase from "./ShopAccountInvoicesBase"


function ShopAccountInvoices({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const dateTimeFormat = dateFormat + ' ' + timeFormat

  // Chain queries. First query user data and then query invoices for that user once we have the account Id.
  const { loading: loadingUser, error: errorUser, data: dataUser } = useQuery(GET_USER_PROFILE)
  const { loading, error, data, fetchMore } = useQuery(QUERY_ACCOUNT_INVOICES, {
    skip: loadingUser || errorUser || !dataUser,
    variables: {
      account: dataUser && dataUser.user ? dataUser.user.accountId : null
    }
  })

  if (loading || loadingUser || !data) return (
    <ShopAccountInvoicesBase>
      {t("general.loading_with_dots")}
    </ShopAccountInvoicesBase>
  )
  if (error || errorUser) return (
    <ShopAccountInvoicesBase>
      {t("shop.account.classpasses.error_loading_data")}
    </ShopAccountInvoicesBase>
  )

  console.log("User data: ###")
  console.log(data)
  const user = dataUser.user
  const invoices = data.financeInvoices

  // Empty list
  if (!invoices.edges.length) {
    return (
      <ShopAccountInvoicesBase accountName={user.fullName}>
        <Grid.Row>
          <Grid.Col md={12}>
            <Card cardTitle={t('shop.account.invoices.title')} >
              <Card.Body>
                {t('shop.account.invoices.empty_list')}
              </Card.Body>
            </Card>
          </Grid.Col>
        </Grid.Row>
      </ShopAccountInvoicesBase>
    )  
  }

  // Populated list
  return (
    <ShopAccountInvoicesBase accountName={user.fullName}>
      <Grid.Row>
        <Grid.Col md={12}>
          <ContentCard cardTitle={t('shop.account.classes.title')}
            // headerContent={headerOptions}
            pageInfo={invoices.pageInfo}
            onLoadMore={() => {
              fetchMore({
                variables: {
                  after: invoices.pageInfo.endCursor
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
                {/* { invoices.edges.map(({ node }) => (
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
                  </Table.Row>
                ))} */}
              </Table.Body>
            </Table>
          </ContentCard>
        </Grid.Col>
      </Grid.Row>
    </ShopAccountInvoicesBase>
  )
}


export default withTranslation()(withRouter(ShopAccountInvoices))