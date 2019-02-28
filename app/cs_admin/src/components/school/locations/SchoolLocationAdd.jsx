import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form, Field, ErrorMessage } from 'formik'
import validator from 'validator';
import { toast } from 'react-toastify';

import { GET_LOCATIONS_QUERY } from './queries'

// @flow

import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Badge,
  Button,
  Card,
  Container,
  List,
  Form as TablerForm,
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import SchoolMenu from "../SchoolMenu"


const ADD_LOCATION = gql`
    mutation CreateSchoolLocation($name: String!, $displayPublic:Boolean!) {
        createSchoolLocation(name: $name, displayPublic: $displayPublic) {
        id
        name
        displayPublic
        }
    }
`;

const return_url = "/school/locations"

const SchoolLocationAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title="School" />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('school.locations.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_LOCATION}> 
                {(addLocation, { data }) => (
                    <Formik
                        initialValues={{ name: '', displayPublic: false }}
                        validate={values => {
                            let errors = {};
                            if (!values.name) {
                            errors.name = t('form.errors.required')
                            } else if 
                                (!validator.isLength(values.name, {"min": 3})) {
                                    errors.name = t('form.errors.min_length_3');
                            }
                            return errors;
                        }}
                        onSubmit={(values, { setSubmitting }) => {
                            addLocation({ variables: {
                                name: values.name, 
                                displayPublic: values.displayPublic
                            }, refetchQueries: [
                                {query: GET_LOCATIONS_QUERY, variables: {"archived": false }}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                history.push(return_url)
                                toast.success((t('school.locations.toast_add_success')), {
                                    position: toast.POSITION.BOTTOM_RIGHT
                                  })
                              }).catch((error) => {
                                toast.error((t('toast_server_error')) + ': ' +  error, {
                                    position: toast.POSITION.BOTTOM_RIGHT
                                  })
                                console.log('there was an error sending the query', error);
                              })
                        }}
                        >
                        {({ isSubmitting, errors }) => (
                            <Form>
                                <Card.Body>
                                    <TablerForm.Label>{t('school.location.public')}</TablerForm.Label>
                                    <Field type="checkbox" name="displayPublic"/>
                                    <ErrorMessage name="displayPublic" component="div" />        
                                    <TablerForm.Label>{t('school.location.name')}</TablerForm.Label>
                                    <Field type="text" 
                                            name="name" 
                                            className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                            autoComplete="off" />
                                    <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                </Card.Body>
                                <Card.Footer>
                                    <button className="btn btn-primary pull-right" type="submit" disabled={isSubmitting}>
                                        {t('submit')}
                                    </button>
                                    <button className="btn btn-link" onClick={() => history.push(return_url)}>
                                        {t('cancel')}
                                    </button>
                                </Card.Footer>
                            </Form>
                        )}
                    </Formik>
                )}
                </Mutation>
          </Card>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="schoollocation">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('back')}
              </Button>
            </HasPermissionWrapper>
            <SchoolMenu active_link='schoollocation'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(SchoolLocationAdd))