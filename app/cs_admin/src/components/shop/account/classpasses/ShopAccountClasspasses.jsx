// @flow

import React, { useContext} from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import moment from 'moment'

import AppSettingsContext from '../../../context/AppSettingsContext'
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"

import {
  Card,
  Grid,
  Table
} from "tabler-react";
import { QUERY_ACCOUNT_CLASSPASSES } from "./queries"

import ShopAccountClasspassesBase from "./ShopAccountClasspassesBase"
import ContentCard from "../../../general/ContentCard"


function ShopAccountClasspasses({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const { loading: loadingUser, error: errorUser, data: dataUser } = useQuery(GET_USER_PROFILE)
  const { loading, error, data, fetchMore } = useQuery(QUERY_ACCOUNT_CLASSPASSES, {
    skip: loadingUser || errorUser || !dataUser,
    variables: {
      account: dataUser && dataUser.user ? dataUser.user.accountId : null
    }
  })
  

  if (loading || loadingUser || !data) return (
    <ShopAccountClasspassesBase>
      {t("general.loading_with_dots")}
    </ShopAccountClasspassesBase>
  )
  if (error || errorUser) return (
    <ShopAccountClasspassesBase>
      {t("shop.account.classpasses.error_loading_data")}
    </ShopAccountClasspassesBase>
  )

  console.log("User data: ###")
  console.log(data)
  const user = data.user
  const classpasses = data.accountClasspasses

  // Empty list
  if (!classpasses.edges.length) {
    return (
      <ShopAccountClasspassesBase accountName={user.fullName}>
        <Grid.Row>
          <Grid.Col md={12}>
            <Card cardTitle={t('shop.account.classpasses.title')} >
              <Card.Body>
                {t('shop.account.classpasses.empty_list')}
              </Card.Body>
            </Card>
          </Grid.Col>
        </Grid.Row>
      </ShopAccountClasspassesBase>
    )  
  }

  // Populated list
  return (
    <ShopAccountClasspassesBase accountName={user.fullName}>
      <Grid.Row>
        <Grid.Col md={12}>
          <ContentCard cardTitle={t('shop.account.classpasses.title')}
            // headerContent={headerOptions}
            pageInfo={classpasses.pageInfo}
            onLoadMore={() => {
              fetchMore({
                variables: {
                  after: classpasses.pageInfo.endCursor
                },
                updateQuery: (previousResult, { fetchMoreResult }) => {
                  const newEdges = fetchMoreResult.accountClasspasses.edges
                  const pageInfo = fetchMoreResult.accountClasspasses.pageInfo

                  return newEdges.length
                    ? {
                        // Put the new subscriptions at the end of the list and update `pageInfo`
                        // so we have the new `endCursor` and `hasNextPage` values
                        accountClasspasses: {
                          __typename: previousResult.accountClasspasses.__typename,
                          edges: [ ...previousResult.accountClasspasses.edges, ...newEdges ],
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
                  <Table.ColHeader>{t('general.classes_remaining')}</Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {classpasses.edges.map(({ node }) => (
                  <Table.Row key={v4()}>
                    <Table.Col>
                      {node.organizationClasspass.name}
                    </Table.Col>
                    <Table.Col>
                      {moment(node.dateStart).format(dateFormat)}
                    </Table.Col>
                    <Table.Col>
                      {moment(node.dateEnd).format(dateFormat)}
                    </Table.Col>
                    <Table.Col>
                      {node.classesRemainingDisplay}
                    </Table.Col>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </ContentCard>
        </Grid.Col>
      </Grid.Row>
    </ShopAccountClasspassesBase>
  )
}


export default withTranslation()(withRouter(ShopAccountClasspasses))