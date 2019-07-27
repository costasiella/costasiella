// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Grid
} from "tabler-react";

import FinanceInvoicesFilter from "./FinanceInvoicesFilter"
import FinanceMenu from "../FinanceMenu"


const FinanceInvoicesBase = ({ t, history, children, refetch }) => (
  <Grid.Row>
    <Grid.Col md={9}>
      {children}
    </Grid.Col>
    <Grid.Col md={3}>
      <h5 className="mt-2 pt-1">{t("general.filter")}</h5>
      <FinanceInvoicesFilter refetch={refetch}/>
      <h5>{t("general.menu")}</h5>
      <FinanceMenu active_link='invoices'/>
    </Grid.Col>
  </Grid.Row>
)

export default withTranslation()(withRouter(FinanceInvoicesBase))