// @flow

import React, { useContext} from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import moment from 'moment'

import AppSettingsContext from '../../../context/AppSettingsContext'

import {
  Card,
  Grid,
  Table
} from "tabler-react";
import { QUERY_ACCOUNT_SUBSCRIPTIONS } from "./queries"
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"

import ShopAccountSubscriptionsBase from "./ShopAccountSubscriptionsBase"
import ContentCard from "../../../general/ContentCard"


function ShopAccountSubscriptions({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat

  // Chain queries. First query user data and then query invoices for that user once we have the account Id.
  const { loading: loadingUser, error: errorUser, data: dataUser } = useQuery(GET_USER_PROFILE)
  const { loading, error, data, fetchMore } = useQuery(QUERY_ACCOUNT_SUBSCRIPTIONS, {
    skip: loadingUser || errorUser || !dataUser,
    variables: {
      account: dataUser && dataUser.user ? dataUser.user.accountId : null
    }
  })
  

  if (loading || loadingUser || !data) return (
    <ShopAccountSubscriptionsBase>
      {t("general.loading_with_dots")}
    </ShopAccountSubscriptionsBase>
  )
  if (error || errorUser) return (
    <ShopAccountSubscriptionsBase>
      {t("shop.account.subscriptions.error_loading_data")}
    </ShopAccountSubscriptionsBase>
  )

  console.log("User data: ###")
  console.log(data)
  const user = data.user
  const subscriptions = data.accountSubscriptions

  // Empty list
  if (!subscriptions.edges.length) {
    return (
      <ShopAccountSubscriptionsBase accountName={user.fullName}>
        <Grid.Row>
          <Grid.Col md={12}>
            <Card cardTitle={t('shop.account.subscriptions.title')} >
              <Card.Body>
                {t('shop.account.subscriptions.empty_list')}
              </Card.Body>
            </Card>
          </Grid.Col>
        </Grid.Row>
      </ShopAccountSubscriptionsBase>
    )  
  }

  // Populated list
  return (
    <ShopAccountSubscriptionsBase accountName={user.fullName}>
      <Grid.Row>
        <Grid.Col md={12}>
          <ContentCard cardTitle={t('shop.account.subscriptions.title')}
            // headerContent={headerOptions}
            pageInfo={subscriptions.pageInfo}
            onLoadMore={() => {
              fetchMore({
                variables: {
                  after: subscriptions.pageInfo.endCursor
                },
                updateQuery: (previousResult, { fetchMoreResult }) => {
                  const newEdges = fetchMoreResult.accountSubscriptions.edges
                  const pageInfo = fetchMoreResult.accountSubscriptions.pageInfo

                  return newEdges.length
                    ? {
                        // Put the new subscriptions at the end of the list and update `pageInfo`
                        // so we have the new `endCursor` and `hasNextPage` values
                        accountSubscriptions: {
                          __typename: previousResult.accountSubscriptions.__typename,
                          edges: [ ...previousResult.accountSubscriptions.edges, ...newEdges ],
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
                  <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {subscriptions.edges.map(({ node }) => (
                  <Table.Row key={v4()}>
                    <Table.Col>
                      {node.organizationSubscription.name}
                    </Table.Col>
                    <Table.Col>
                      {moment(node.dateStart).format(dateFormat)}
                    </Table.Col>
                    <Table.Col>
                      { (node.dateEnd) ? moment(node.dateEnd).format(dateFormat) : "" }
                    </Table.Col>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </ContentCard>
        </Grid.Col>
      </Grid.Row>
    </ShopAccountSubscriptionsBase>
  )
}


export default withTranslation()(withRouter(ShopAccountSubscriptions))