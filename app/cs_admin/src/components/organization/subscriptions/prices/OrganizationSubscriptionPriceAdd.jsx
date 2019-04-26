// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'


import { GET_SUBSCRIPTION_PRICES_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { GET_SUBSCRIPTIONS_QUERY } from '../queries'
import { SUBSCRIPTION_PRICE_SCHEMA } from './yupSchema'
import OrganizationSubscriptionPriceForm from './OrganizationSubscriptionPriceForm'
import { dateToLocalISO } from '../../../../tools/date_tools'

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
            <Query query={GET_INPUT_VALUES_QUERY} variables={{ archived: false }} >
              {({ loading, error, data, refetch }) => {
                  // Loading
                  if (loading) return <p>{t('general.loading_with_dots')}</p>
                  // Error
                  if (error) {
                    console.log(error)
                    return <p>{t('general.error_sad_smiley')}</p>
                  }
                  
                  console.log('query data')
                  console.log(data)
                  const inputData = data

                  return (
                    <Mutation mutation={ADD_SUBSCRIPTION_PRICE} onCompleted={() => history.push(return_url + match.params.subscription_id)}> 
                      {(addSubscription, { data }) => (
                          <Formik
                              initialValues={{ price: "", dateStart: new Date() }}
                              validationSchema={SUBSCRIPTION_PRICE_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {

                                  let dateEnd
                                  if (values.dateEnd) {
                                    dateEnd = dateToLocalISO(values.dateEnd)
                                  } else {
                                    dateEnd = values.dateEnd
                                  }

                                  addSubscription({ variables: {
                                    input: {
                                      organizationSubscription: match.params.subscription_id,
                                      price: values.price,
                                      financeTaxRate: values.financeTaxRate,
                                      dateStart: dateToLocalISO(values.dateStart),
                                      dateEnd: dateEnd
                                    }
                                  }, refetchQueries: [
                                      {query: GET_SUBSCRIPTION_PRICES_QUERY, variables: {"organizationSubscription": match.params.subscription_id }},
                                      {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }},
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
                              {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
                                <OrganizationSubscriptionPriceForm
                                  inputData={inputData}
                                  isSubmitting={isSubmitting}
                                  setFieldTouched={setFieldTouched}
                                  setFieldValue={setFieldValue}
                                  errors={errors}
                                  values={values}
                                  return_url={return_url}
                                />
                              )}
                          </Formik>
                      )}
                    </Mutation>
                  )}}
                </Query>
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