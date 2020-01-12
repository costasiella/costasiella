// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks';

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SelfCheckinBase from "../SelfCheckinBase"

import HasPermissionWrapper from "../../HasPermissionWrapper"
import { GET_ORGANIZATION_LOCATIONS_QUERY } from "./queries"


function Locations({ t, match, history }) {
  const { loading, error, data } = useQuery(GET_ORGANIZATION_LOCATIONS_QUERY);

  if (loading) return (
    <SelfCheckinBase>
      {t("general.loading_with_dots")}
    </SelfCheckinBase>
  )
  if (error) return (
    <SelfCheckinBase>
      {t("selfcheckin.loadings.error_loading")}
    </SelfCheckinBase>
  )

  return (
    <SelfCheckinBase title={t("selfcheckin.locations.title")}>
      <Card>
        <Card.Header>
          <Card.Title>{t('home.title')}</Card.Title>
        </Card.Header>
        <Card.Body>
          Hello world from the self checkin component!
        </Card.Body>
      </Card>
    </SelfCheckinBase>
  )
}


export default withTranslation()(withRouter(Locations))