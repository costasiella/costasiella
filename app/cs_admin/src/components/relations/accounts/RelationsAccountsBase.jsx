
import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
    Badge,
    Page,
    Grid,
    Icon,
    Dimmer,
    Button,
    Card,
    Container,
    Table
  } from "tabler-react";

import CSLS from "../../../tools/cs_local_storage"
import ContentCard from "../../general/ContentCard"
import InputSearch from "../../general/InputSearch"
import RelationsMenu from "../RelationsMenu"
import { get_list_query_variables } from "./tools"
import HasPermissionWrapper from "../../HasPermissionWrapper"


const RelationsAccountsBase = ({t, history, refetch, children }) => (
    <Container>
      <Page.Header title={t("relations.title")}>
        <div className="page-options d-flex">
          <InputSearch 
            initialValueKey={CSLS.RELATIONS_ACCOUNTS_SEARCH}
            placeholder="Search..."
            onChange={(value) => {
              console.log(value)
              localStorage.setItem(CSLS.RELATIONS_ACCOUNTS_SEARCH, value)
              refetch(get_list_query_variables())
            }}
          />
        </div>
      </Page.Header>
      <Grid.Row>
        <Grid.Col md={9}>
          {children}
        </Grid.Col>
        <Grid.Col md={3}>
          <HasPermissionWrapper permission="add"
                                resource="account">
            <Button color="primary btn-block mb-6"
                    onClick={() => history.push("/relations/accounts/add")}>
              <Icon prefix="fe" name="plus-circle" /> {t('relations.accounts.add')}
            </Button>
          </HasPermissionWrapper>
          <RelationsMenu active_link='accounts'/>
        </Grid.Col>
      </Grid.Row>
    </Container>
  )


  export default withTranslation()(withRouter(RelationsAccountsBase))