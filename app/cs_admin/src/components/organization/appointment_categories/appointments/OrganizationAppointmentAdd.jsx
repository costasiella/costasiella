// @flow

import React from 'react'
import { Mutation, Query } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'


import { GET_APPOINTMENTS_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { APPOINTMENT_SCHEMA } from './yupSchema'
import OrganizationAppointmentForm from './OrganizationAppointmentForm'

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


const ADD_APPOINTMENT = gql`
  mutation CreateOrganizationAppointment($input: CreateOrganizationAppointmentInput!) {
    createOrganizationAppointment(input: $input) {
      organizationAppointment {
        id
        organizationAppointmentCategory {
          id
          name
        }
        archived
        displayPublic
        name
      }
    }
  }
`

const return_url = "/organization/appointment_categories/appointments/"

const OrganizationAppointmentAdd = ({ t, history, match }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('organization.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('organization.appointments.title_add')}</Card.Title>
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
                  <Mutation mutation={ADD_APPOINTMENT} onCompleted={() => history.push("/organization/appointment_categories/" + match.params.category_id + "/appointments")}> 
                      {(addAppointment, { data }) => (
                          <Formik
                              initialValues={{ name: '', displayPublic: true }}
                              validationSchema={APPOINTMENT_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  addAppointment({ variables: {
                                    input: {
                                      organizationAppointmentCategory: match.params.category_id,
                                      name: values.name, 
                                      displayPublic: values.displayPublic,
                                      financeGlaccount: values.financeGlaccount,
                                      financeCostcenter: values.financeCostcenter
                                    }
                                  }, refetchQueries: [
                                      {query: GET_APPOINTMENTS_QUERY,
                                      variables: {"archived": false, "organizationAppointmentCategory": match.params.category_id }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data);
                                      toast.success((t('organization.appointments.toast_add_success')), {
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
                                <OrganizationAppointmentForm
                                  inputData={inputData}
                                  isSubmitting={isSubmitting}
                                  errors={errors}
                                  values={values}
                                  return_url={"/organization/appointment_categories/" + match.params.category_id + "/appointments"}
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
                                  resource="organizationappointment">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url + match.params.category_id)}>
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

export default withTranslation()(withRouter(OrganizationAppointmentAdd))