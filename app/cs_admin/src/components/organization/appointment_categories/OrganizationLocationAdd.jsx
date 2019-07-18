// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'


import { GET_LOCATIONS_QUERY } from './queries'
import { LOCATION_SCHEMA } from './yupSchema'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationMenu from "../OrganizationMenu"


const ADD_LOCATION = gql`
  mutation CreateOrganizationLocation($input: CreateOrganizationLocationInput!) {
    createOrganizationLocation(input: $input) {
      organizationLocation {
        id
        archived
        displayPublic
        name
      }
    }
  }
`

const return_url = "/organization/locations"

const OrganizationLocationAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title="Organization" />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('organization.locations.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_LOCATION} onCompleted={() => history.push(return_url)}> 
                {(addLocation, { data }) => (
                    <Formik
                        initialValues={{ name: '', displayPublic: true }}
                        validationSchema={LOCATION_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addLocation({ variables: {
                              input: {
                                name: values.name, 
                                displayPublic: values.displayPublic
                              }
                            }, refetchQueries: [
                                {query: GET_LOCATIONS_QUERY, variables: {"archived": false }}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('organization.locations.toast_add_success')), {
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
                            <FoForm>
                                <Card.Body>
                                    <Form.Group>
                                      <Form.Label className="custom-switch">
                                        <Field 
                                          className="custom-switch-input"
                                          type="checkbox" 
                                          name="displayPublic" 
                                          checked={values.displayPublic} />
                                        <span className="custom-switch-indicator" ></span>
                                        <span className="custom-switch-description">{t('organization.location.public')}</span>
                                      </Form.Label>
                                      <ErrorMessage name="displayPublic" component="div" />   
                                    </Form.Group>    

                                    <Form.Group label={t('general.name')}>
                                      <Field type="text" 
                                              name="name" 
                                              className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                              autoComplete="off" />
                                      <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                    </Form.Group>
                                </Card.Body>
                                <Card.Footer>
                                    <Button 
                                      color="primary"
                                      className="pull-right" 
                                      type="submit" 
                                      disabled={isSubmitting}
                                    >
                                      {t('general.submit')}
                                    </Button>
                                    <Button color="link" onClick={() => history.push(return_url)}>
                                        {t('general.cancel')}
                                    </Button>
                                </Card.Footer>
                            </FoForm>
                        )}
                    </Formik>
                )}
                </Mutation>
          </Card>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="organizationlocation">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='locations'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationLocationAdd))