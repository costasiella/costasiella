// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'


import { GET_SUBSCRIPTION_PRICES_QUERY } from './queries'
import { SUBSCRIPTION_PRICE_SCHEMA } from './yupSchema'
import OrganizationSubscriptionPriceForm from './OrganizationSubscriptionPriceForm'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationMenu from "../../OrganizationMenu"


const ADD_SUBSCRIPTION_PRICE = gql`
  mutation CreateOrganizationSubscriptionPrice($input: CreateOrganizationSubscriptionPriceInput!) {
    createOrganizationSubscriptionPrice(input: $input) {
      organizationSubscriptionPrice {
        id
        organizationSubscription {
          id
          name
        }
        price
        financeTaxRate {
          id
          name
        }
        dateStart
        dateEnd
      }
    }
  }
`

const return_url = "/organization/subscriptions/prices/"

const OrganizationSubscriptionPriceAdd = ({ t, history, match }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title="Organization" />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('organization.subscription_prices.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_SUBSCRIPTION_PRICE} onCompleted={() => history.push(return_url + match.params.subscription_id)}> 
                {(addLocation, { data }) => (
                    <Formik
                        initialValues={{ name: '', displayPublic: true }}
                        validationSchema={SUBSCRIPTION_PRICE_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addLocation({ variables: {
                              input: {
                                organizationSubscription: match.params.subscription_id,
                                price: values.price,
                                financeTaxRate: values.financeTaxRate,
                                dateStart: values.dateStart
                              }
                            }, refetchQueries: [
                                {query: GET_SUBSCRIPTION_PRICES_QUERY,
                                 variables: {"organizationSubscription": match.params.subscription_id }}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('organization.subscription_prices.toast_add_success')), {
                                    position: toast.POSITION.BOTTOM_RIGHT
                                  })
                              }).catch((error) => {
                                toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                    position: toast.POSITION.BOTTOM_RIGHT
                                  })
                                console.log('there was an error sending the query', error)
                                setSubmitting(false)
                              })
                        }}
                        >
                        {({ isSubmitting, errors, values }) => (
                          <OrganizationSubscriptionPriceForm
                            inputData={inputData}
                            isSubmitting={isSubmitting}
                            errors={errors}
                            values={values}
                            return_url={return_url}
                            />
                        )}
                    </Formik>
                )}
                </Mutation>
          </Card>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="organizationsubscriptionprice">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url + match.params.subscription_id)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='subscriptions'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationSubscriptionPriceAdd))