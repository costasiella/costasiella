// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_APPOINTMENTS_QUERY, GET_APPOINTMENT_QUERY } from './queries'
import { APPOINTMENT_SCHEMA } from './yupSchema'
import OrganizationAppointmentForm from './OrganizationAppointmentForm'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationMenu from "../../OrganizationMenu"


const UPDATE_APPOINTMENT = gql`
  mutation UpdateOrganizationAppointment($input: UpdateOrganizationAppointmentInput!) {
    updateOrganizationAppointment(input: $input) {
      organizationAppointment {
        id
        name
        displayPublic
      }
    }
  }
`


class OrganizationAppointmentEdit extends Component {
  constructor(props) {
    super(props)
    console.log("Organization appointment edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const category_id = match.params.category_id
    const return_url = "/organization/appointment_categories/" + match.params.category_id + "/appointments"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t('organization.title')} />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.appointments.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_APPOINTMENT_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const inputData = data
                    const initialData = data.organizationAppointment
                    console.log('query data')
                    console.log(data)

                    let initialGlaccount = ""
                    if (initialData.financeGlaccount) {
                      initialGlaccount =  initialData.financeGlaccount.id
                    } 

                    let initialCostcenter = ""
                    if (initialData.financeCostcenter) {
                      initialCostcenter =  initialData.financeCostcenter.id
                    } 

                    return (
                      
                      <Mutation mutation={UPDATE_APPOINTMENT} onCompleted={() => history.push(return_url)}> 
                      {(updateLocation, { data }) => (
                          <Formik
                              initialValues={{ 
                                name: initialData.name, 
                                displayPublic: initialData.displayPublic,
                                financeGlaccount: initialGlaccount,
                                financeCostcenter: initialCostcenter,
                              }}
                              validationSchema={APPOINTMENT_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  updateLocation({ variables: {
                                    input: {
                                      id: match.params.id,
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
                                      console.log('got data', data)
                                      toast.success((t('organization.appointments.toast_edit_success')), {
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
                <HasPermissionWrapper permission="change"
                                      resource="organizationappointment">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <OrganizationMenu active_link='appointments'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationAppointmentEdit))