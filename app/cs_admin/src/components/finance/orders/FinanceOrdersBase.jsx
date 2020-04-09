// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Container,
  Grid,
  Page
} from "tabler-react";

import SiteWrapper from "../../SiteWrapper"

import FinanceOrdersFilter from "./FinanceOrdersFilter"
import FinanceMenu from "../FinanceMenu"


const FinanceOrdersBase = ({ t, history, children, refetch }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("finance.title")}>
          <div className="page-options d-flex">
          </div>
        </Page.Header>
        <Grid.Row>
          <Grid.Col md={9}>
            {children}
          </Grid.Col>
          <Grid.Col md={3}>
            <h5 className="mt-2 pt-1">{t("general.filter")}</h5>
            <FinanceOrdersFilter refetch={refetch}/>
            <h5>{t("general.menu")}</h5>
            <FinanceMenu active_link='orders'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
)

export default withTranslation()(withRouter(FinanceOrdersBase))