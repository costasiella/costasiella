
import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
    Page,
    Grid,
    Icon,
    Button,
    Container,
  } from "tabler-react";

import CSLS from "../../../tools/cs_local_storage"
import InputSearch from "../../general/InputSearch"
import RelationsMenu from "../RelationsMenu"
import { get_list_query_variables } from "./tools"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"


const RelationsB2BBase = ({t, history, refetch, children }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("relations.title")}>
          <div className="page-options d-flex">
            <InputSearch 
              initialValueKey={CSLS.RELATIONS_BUSINESSES_SEARCH}
              placeholder="Search..."
              onChange={(value) => {
                console.log(value)
                localStorage.setItem(CSLS.RELATIONS_BUSINESSES_SEARCH, value)
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
                                  resource="business">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/relations/b2b/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('relations.b2b.add')}
              </Button>
            </HasPermissionWrapper>
            <RelationsMenu active_link='b2b'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
)


  export default withTranslation()(withRouter(RelationsB2BBase))