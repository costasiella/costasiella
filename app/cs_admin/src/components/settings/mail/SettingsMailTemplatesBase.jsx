// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
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

import BadgeBoolean from "../../ui/BadgeBoolean"

import ContentCard from "../../general/ContentCard"
import OrganizationMenu from "../OrganizationMenu"



function SettingsMailTemplates({ t }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("settings.mail.templates.title")}>
            {/* To do: back button here */}
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={12}>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(SettingsMailTemplates))