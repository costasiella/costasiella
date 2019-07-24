// @flow

import React from 'react'
import { Mutation, Query } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'


import { GET_APPOINTMENT_PRICES_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { APPOINTMENT_PRICE_SCHEMA } from './yupSchema'
import OrganizationAppointmentPriceForm from './OrganizationAppointmentPriceForm'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../../../SiteWrapper"
import HasPermissionWrapper from "../../../../HasPermissionWrapper"

import OrganizationMenu from "../../../OrganizationMenu"


const ADD_APPOINTMENT_PRICE = gql`
  mutation CreateOrganizationAppointmentPrice($input: CreateOrganizationAppointmentPriceInput!) {
    createOrganizationAppointmentPrice(input: $input) {
      organizationAppointmentPrice {
        id
        account {
          id
          fullName
        }
        organizationAppointment {
          id
          name
        }
        price
        financeTaxRate {
          id
          name
        }
      }
    }
  }
`

const return_url = "/organization/appointment_categories/appointments/"

const OrganizationAppointmentPriceAdd = ({ t, history, match }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('organization.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('organization.appointment_prices.title_add')}</Card.Title>
            </Card.Header>
            <Query query={GET_INPUT_VALUES_QUERY} variables = {{archived: false}} >
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
                  <Mutation mutation={ADD_APPOINTMENT_PRICE} onCompleted={
                    () => history.push("/organization/appointment_categories/" + match.params.category_id + "/appointments/prices/" + match.params.appointment_id)}> 
                      {(addAppointment, { data }) => (
                          <Formik
                              initialValues={{ 
                                organizationAppointment: '', 
                                account: '',
                                price: '',
                                financeTaxRate: "",
                              }}
                              validationSchema={APPOINTMENT_PRICE_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  addAppointment({ variables: {
                                    input: {
                                      organizationAppointment: match.params.appointment_id,
                                      account: values.account,
                                      price: values.price, 
                                      financeTaxRate: values.financeTaxRate,
                                    }
                                  }, refetchQueries: [
                                      {query: GET_APPOINTMENT_PRICES_QUERY,
                                      variables: {"organizationAppointment": match.params.appointment_id }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data);
                                      toast.success((t('organization.appointment_prices.toast_add_success')), {
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
                                <OrganizationAppointmentPriceForm
                                  inputData={inputData}
                                  isSubmitting={isSubmitting}
                                  errors={errors}
                                  values={values}
                                  return_url={"/organization/appointment_categories/" + match.params.category_id + "/appointments/prices/" + match.params.appointment_id}
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
                                  resource="organizationappointmentprice">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/appointment_categories/" + match.params.category_id + "/appointments/prices/" + match.params.appointment_id)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='appointments'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationAppointmentPriceAdd))