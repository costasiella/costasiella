// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_PAYMENT_METHODS_QUERY, GET_PAYMENT_METHOD_QUERY } from './queries'
// import { PAYMENT_METHOD_SCHEMA } from './yupSchema'



import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

// import FinancePaymentMethodForm from './AppSettingsGeneralForm'
import AppSettingsMenu from "../AppSettingsMenu"


const UPDATE_PAYMENT_METHOD = gql`
  mutation UpdateFinancePaymentMethod($input: UpdateFinancePaymentMethodInput!) {
    updateFinancePaymentMethod(input: $input) {
      financePaymentMethod {
        id
        name
        code
      }
    }
  }
`

function AppSettingsGeneral({ t, match, history }) {

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('settings.title')} />
          <Grid.Row>
            <Grid.Col md={9}>
            <Card>
              <Card.Header>
                <Card.Title>{t('settings.general.title')}</Card.Title>
              </Card.Header>
              <Card.Body>
                content here
              </Card.Body>
            </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <AppSettingsMenu active_link="general" />
              {/* <HasPermissionWrapper permission="change"
                                    resource="financepaymentmethod">
                <Button color="primary btn-block mb-6"
                        onClick={() => history.push(return_url)}>
                  <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                </Button>
              </HasPermissionWrapper>
              <FinanceMenu active_link='payment_methods'/> */}
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(AppSettingsGeneral))