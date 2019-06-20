// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../plugin_config/tinymce"

import { GET_CLASSTYPES_QUERY, GET_CLASSTYPE_QUERY } from './queries'
import { CLASSTYPE_SCHEMA } from './yupSchema'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationMenu from "../OrganizationMenu"


const UPDATE_CLASSTYPE = gql`
  mutation UpdateOrganizationClasstype($input: UpdateOrganizationClasstypeInput!) {
    updateOrganizationClasstype(input: $input) {
      organizationClasstype {
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


class OrganizationClasstypeEdit extends Component {
  constructor(props) {
    super(props)
    console.log("Organization classtype edit props:")
    console.log(props)
  }


  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/organization/classtypes"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.classtypes.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_CLASSTYPE_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.organizationClasstype
                    console.log('query data')
                    console.log(data)

                    return (
                      
                      <Mutation mutation={UPDATE_CLASSTYPE} onCompleted={() => history.push(return_url)}> 
                        {(updateClasstype, { data }) => (
                          <Formik
                              initialValues={{ 
                                name: initialData.name, 
                                description: initialData.description,
                                displayPublic: initialData.displayPublic,
                                urlWebsite: initialData.urlWebsite
                              }}
                              validationSchema={CLASSTYPE_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  updateClasstype({ variables: {
                                    input: {
                                      id: match.params.id,
                                      name: values.name,
                                      description: (values.description) ? values.description: '',
                                      displayPublic: values.displayPublic,
                                      urlWebsite: (values.urlWebsite) ? values.urlWebsite: ''
                                    }
                                  }, refetchQueries: [
                                      {query: GET_CLASSTYPES_QUERY, variables: {"archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.classtypes.toast_edit_success')), {
                                          position: toast.POSITION.BOTTOM_RIGHT
                                        })
                                    }).catch((error) => {
                                      toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                          position: toast.POSITION.BOTTOM_RIGHT
                                        })
                                      console.log('there was an error sending the query', error);
                                      setSubmitting(false)
                                    })
                              }}
                              >
                              {({ isSubmitting, errors, values, setFieldValue, setFieldTouched }) => (
                                  <FoForm>
                                      {console.log(values)}
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
                                          <Form.Group label={t('general.name')} >
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
                                            className="pull-right"
                                            color="primary"
                                            disabled={isSubmitting}
                                            type="submit"
                                          >
                                            {t('general.submit')}
                                          </Button>
                                          <Button
                                            type="button" 
                                            color="link" 
                                            onClick={() => history.push(return_url)}
                                          >
                                              {t('general.cancel')}
                                          </Button>
                                      </Card.Footer>
                                  </FoForm>
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
    )}
  }


export default withTranslation()(withRouter(OrganizationClasstypeEdit))