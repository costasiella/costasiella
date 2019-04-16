// @flow

import React, { Component } from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../plugin_config/tinymce"

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

import OrganizationMenu from "../OrganizationMenu"


const ADD_CLASSTYPE = gql`
mutation CreateOrganizationClasstype($input: CreateOrganizationClasstypeInput!) {
  createOrganizationClasstype(input: $input) {
    organizationClasstype {
      id
      archived
      name
      description
      displayPublic
      urlWebsite
      image
    }
  }
}
`

const return_url = "/organization/classtypes"


class OrganizationClasstypeAdd extends Component {
  constructor(props) {
    super(props)
    console.log("Organization classtype add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const return_url = "/organization/classtypes"

    return(
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title="Organization" />
          <Grid.Row>
            <Grid.Col md={9}>
            <Card>
              <Card.Header>
                <Card.Title>{t('organization.classtypes.title_add')}</Card.Title>
              </Card.Header>
              <Mutation mutation={ADD_CLASSTYPE} onCompleted={() => history.push(return_url)}> 
                  {(addClasstype, { data }) => (
                      <Formik
                          initialValues={{ name: "", description: "", displayPublic: true, urlWebsite: '' }}
                          validationSchema={CLASSTYPE_SCHEMA}
                          onSubmit={(values, { setSubmitting }) => {
                              addClasstype({ variables: {
                                input: {
                                  name: values.name, 
                                  description: values.description,
                                  displayPublic: values.displayPublic,
                                  urlWebsite: values.urlWebsite,
                                  image: values.image
                                },
                                // file: values.image
                              }, refetchQueries: [
                                  {query: GET_CLASSTYPES_QUERY, variables: {"archived": false }}
                              ]})
                              .then(({ data }) => {
                                  console.log('got data', data);
                                  toast.success((t('organization.classtypes.toast_add_success')), {
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
                          {({ isSubmitting, setFieldValue, setFieldTouched, errors, values }) => (
                              <FoForm>
                                {/* {console.log('values in FoForm')}
                                {console.log(values)} */}
                                  <Card.Body>
                                      <Form.Group>
                                        <Form.Label className="custom-switch">
                                          <Field 
                                            className="custom-switch-input"
                                            type="checkbox" 
                                            name="displayPublic" 
                                            checked={values.displayPublic} />
                                          <span className="custom-switch-indicator" ></span>
                                          <span className="custom-switch-description">{t('organization.classtype.public')}</span>
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
                                      <Form.Group label={t('general.description')}>
                                        <Editor
                                            textareaName="description"
                                            initialValue={values.description}
                                            init={tinymceBasicConf}
                                            onChange={(e) => setFieldValue("description", e.target.getContent())}
                                            onBlur={() => setFieldTouched("description", true)}
                                          />
                                        <ErrorMessage name="description" component="span" className="invalid-feedback" />
                                      </Form.Group>
                                      <Form.Group label={t('organization.classtype.url_website')}>
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
                                    resource="organizationclasstype">
                <Button color="primary btn-block mb-6"
                        onClick={() => history.push(return_url)}>
                  <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                </Button>
              </HasPermissionWrapper>
              <OrganizationMenu active_link='classtypes'/>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
    ) 
  }
}

export default withTranslation()(withRouter(OrganizationClasstypeAdd))