import React from 'react'
import { Query } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form, Field, ErrorMessage } from 'formik'
import validator from 'validator';


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

const GET_LOCATIONS = gql`
  {
    schoolLocations {
        id
        name
        displayPublic
    }
  }
`

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
            <Formik
                initialValues={{ name: '', public: true }}
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
                    setTimeout(() => {
                    alert(JSON.stringify(values, null, 2));
                    setSubmitting(false);
                    }, 400);
                }}
                >
                {({ isSubmitting, errors }) => (
                    <Form>
                        <Card.Body>
                        <TablerForm.Label>{t('school.location.public')}</TablerForm.Label>
                        <Field type="checkbox" name="public" checked/>
                        <ErrorMessage name="public" component="div" />        
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
                {/* <Formik
                    initialValues={{ name: '', displayPublic: '' }}
                    validate={values => {
                        let errors = {};
                        if (!values.name) {
                        errors.name = 'Required';
                        } else if (
                        !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)
                        ) {
                        errors.name = 'Invalid email address';
                        }
                        return errors;
                    }}
                    onSubmit={(values, { setSubmitting }) => {
                        setTimeout(() => {
                        alert(JSON.stringify(values, null, 2));
                        setSubmitting(false);
                        }, 400);
                    }}
                    >
                    {({ isSubmitting }) => (
                    <Form>
                        <TablerForm.Label>{t('school.location.name')}</TablerForm.Label>
                        <Field className="form-control" type="text" name="name" />
                        <ErrorMessage name="text" component="div" />
                        <TablerForm.Label>{t('school.location.public')}</TablerForm.Label>
                        <Field type="checkbox" name="displayPublic" />
                        <ErrorMessage name="displayPublic" component="div" />
                        <br/>
                        <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                            {t('save')}
                        </button>
                    </Form>
                    )}
                </Formik> */}
              {/* <Query query={GET_LOCATIONS}>
                {({ loading, error, data }) => {
                  // Loading
                  if (loading) return (
                    <Dimmer active={true}
                            loader={true} />
                  )
                  // Error
                  if (error) return <p>{t('school.locations.error_loading')}</p>
                  // Empty list
                  if (!data.schoolLocations) {
                    return t('school.locations.empty_list')
                  } else {
                    // Life's good! :)
                    return (
                      <Table>
                        <Table.Header>
                          <Table.Row key={v4()}>
                            <Table.ColHeader>{t('name')}</Table.ColHeader>
                            <Table.ColHeader>{t('public')}</Table.ColHeader>
                          </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {console.log(data.schoolLocations)}
                            {data.schoolLocations.map(({ id, name, displayPublic }) => (
                              <Table.Row key={v4()}>
                                <Table.Col key={v4()}>
                                  {name}
                                </Table.Col>
                                <Table.Col key={v4()}>
                                  {(displayPublic) ? 'yep': 'nope'}
                                </Table.Col>
                              </Table.Row>
                            ))}
                        </Table.Body>
                      </Table>
                    )
                  }
                }}
              </Query> */}
            {/* </Card.Body> */}
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