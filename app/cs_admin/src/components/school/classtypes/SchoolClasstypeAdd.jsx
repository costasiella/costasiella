// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'


import { GET_CLASSTYPES_QUERY } from './queries'
import { CLASSTYPE_SCHEMA } from './yupSchema'


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

import SchoolMenu from "../SchoolMenu"


const ADD_CLASSTYPE = gql`
mutation CreateSchoolClasstype($input: CreateSchoolClasstypeInput!) {
  createSchoolClasstype(input: $input) {
    schoolClasstype {
      id
      archived
      name
      description
      displayPublic
      urlWebsite
    }
  }
}
`

const return_url = "/school/classtypes"

const SchoolClasstypeAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title="School" />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('school.classtypes.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_CLASSTYPE} onCompleted={() => history.push(return_url)}> 
                {(addClasstype, { data }) => (
                    <Formik
                        initialValues={{ name: '', description: '', displayPublic: true, link: '' }}
                        validationSchema={CLASSTYPE_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addClasstype({ variables: {
                              input: {
                                name: values.name, 
                                description: values.description,
                                displayPublic: values.displayPublic,
                                urlWebsite: values.urlWebsite
                              }
                            }, refetchQueries: [
                                {query: GET_CLASSTYPES_QUERY, variables: {"archived": false }}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('school.classtypes.toast_add_success')), {
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
                        {({ isSubmitting, errors, values }) => (
                            <FoForm>
                                <Card.Body>
                                    {/* <Form.Group label={t('school.location.public')}>
                                      <Field type="checkbox" name="displayPublic" checked={values.displayPublic} />
                                      <ErrorMessage name="displayPublic" component="div" />        
                                    </Form.Group> */}
                                    <Form.Group>
                                      <Form.Label className="custom-switch">
                                        <Field 
                                          className="custom-switch-input"
                                          type="checkbox" 
                                          name="displayPublic" 
                                          checked={values.displayPublic} />
                                        <span className="custom-switch-indicator" ></span>
                                        <span className="custom-switch-description">{t('school.classtype.public')}</span>
                                      </Form.Label>
                                      <ErrorMessage name="displayPublic" component="div" />   
                                    </Form.Group>    
                                    <Form.Group label={t('school.classtype.name')}>
                                      <Field type="text" 
                                              name="name" 
                                              className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                              autoComplete="off" />
                                      <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                    </Form.Group>
                                    <Form.Group label={t('description')}>
                                      <Field type="text" 
                                             component="textarea"
                                             name="description" 
                                             className={(errors.description) ? "form-control is-invalid" : "form-control"} 
                                             autoComplete="off" />
                                      <ErrorMessage name="description" component="span" className="invalid-feedback" />
                                    </Form.Group>
                                    <Form.Group label={t('school.classtype.url_website')}>
                                      <Field type="text" 
                                             name="urlWebsite" 
                                             className={(errors.urlWebsite) ? "form-control is-invalid" : "form-control"} 
                                             autoComplete="off" />
                                      <ErrorMessage name="urlWebsite" component="span" className="invalid-feedback" />
                                    </Form.Group>
                                </Card.Body>
                                <Card.Footer>
                                    <Button 
                                      color="primary"
                                      className="pull-right" 
                                      type="submit" 
                                      disabled={isSubmitting}
                                    >
                                      {t('submit')}
                                    </Button>
                                    <Button color="link" onClick={() => history.push(return_url)}>
                                        {t('cancel')}
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

export default withTranslation()(withRouter(SchoolClasstypeAdd))