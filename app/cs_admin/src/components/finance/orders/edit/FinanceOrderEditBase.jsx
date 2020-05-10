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


const FinanceOrderEditBase = ({ t, history, children, refetch }) => (
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
            <HasPermissionWrapper permission="change"
                                  resource="financeorder">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
              </Button>
            </HasPermissionWrapper>            
            <h5>{t("general.menu")}</h5>
            <FinanceMenu active_link='orders'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
)

export default withTranslation()(withRouter(FinanceOrderEditBase))