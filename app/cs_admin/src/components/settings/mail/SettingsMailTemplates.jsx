// @flow

import React from 'react'
import { useQuery } from "react-apollo"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import ContentCard from "../../general/ContentCard"
import SettingsMailTemplatesBase from "./SettingsMailTemplatesBase"

import { GET_SYSTEM_MAIL_TEMPLATES_QUERY } from "./queries"


function SystemMailTemplates({ t, match, params }) {
  const title = t("settings.mail.templates.title")
  const { loading, error, data, fetchMore } = useQuery(GET_SYSTEM_MAIL_TEMPLATES_QUERY)

  if (loading) return (
    <SettingsMailTemplatesBase title={title} >
      {t("general.loading_with_dots")}
    </SettingsMailTemplatesBase>
  )
  if (error) return (
    <SettingsMailTemplatesBase title={title}>
      {t("settings.mail.templates.error_loading")}
    </SettingsMailTemplatesBase>
  )

  console.log(data)
  const mailTemplates = data.systemMailTemplates

  // TODO: add empty list message and request import



  return (
    <SettingsMailTemplatesBase title={title} >
      <ContentCard 
        cardTitle={t('settings.mail.templates.title')}
        // headerContent={headerOptions}
        pageInfo={mailTemplates.pageInfo}
        onLoadMore={() => {
          fetchMore({
            variables: {
              after: mailTemplates.pageInfo.endCursor
            },
            updateQuery: (previousResult, { fetchMoreResult }) => {
              const newEdges = fetchMoreResult.systemMailTemplates.edges
              const pageInfo = fetchMoreResult.systemMailTemplates.pageInfo

              return newEdges.length
                ? {
                    // Put the new subscriptions at the end of the list and update `pageInfo`
                    // so we have the new `endCursor` and `hasNextPage` values
                    systemMailTemplates: {
                      __typename: previousResult.systemMailTemplates.__typename,
                      edges: [ ...previousResult.systemMailTemplates.edges, ...newEdges ],
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
              <Table.ColHeader>{t('settings.mail.templates.name')}</Table.ColHeader>
              <Table.ColHeader></Table.ColHeader>
            </Table.Row>
          </Table.Header>
              <Table.Body>
                  {mailTemplates.edges.map(({ node }) => (
                    <Table.Row key={v4()}>
                      <Table.Col>
                        {node.name}
                      </Table.Col>
                      <Table.Col>
                        <Link to={"/settings/mail/templates/edit/" + node.id}>
                          <Button className='btn-sm pull-right' 
                                  color="secondary">
                            {t('general.edit')}
                          </Button>
                        </Link>
                      </Table.Col>
                    </Table.Row>
                  ))}
              </Table.Body>
            </Table>
      </ContentCard>
    </SettingsMailTemplatesBase>
  )
}

export default withTranslation()(withRouter(SystemMailTemplates))
