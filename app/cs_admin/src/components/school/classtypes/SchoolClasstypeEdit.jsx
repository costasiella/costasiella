// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

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

import SchoolMenu from "../SchoolMenu"


const UPDATE_CLASSTYPE = gql`
  mutation UpdateSchoolClasstype($input: UpdateSchoolClasstypeInput!) {
    updateSchoolClasstype(input: $input) {
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


class SchoolClasstypeEdit extends Component {
  constructor(props) {
    super(props)
    console.log("School classtype edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/school/classtypes"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="School" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('school.classtypes.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_CLASSTYPE_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.schoolClasstype
                    console.log('query data')
                    console.log(data)

                    return (
                      
                      <Mutation mutation={UPDATE_CLASSTYPE} onCompleted={() => history.push(return_url)}> 
                      {(updateLocation, { data }) => (
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

                                  updateLocation({ variables: {
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
                                      toast.success((t('school.classtypes.toast_edit_success')), {
                                          position: toast.POSITION.BOTTOM_RIGHT
                                        })
                                    }).catch((error) => {
                                      toast.error((t('toast_server_error')) + ': ' +  error, {
                                          position: toast.POSITION.BOTTOM_RIGHT
                                        })
                                      console.log('there was an error sending the query', error);
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
                                              <span className="custom-switch-description">{t('school.location.public')}</span>
                                            </Form.Label>
                                            <ErrorMessage name="displayPublic" component="div" />   
                                          </Form.Group>     
                                          <Form.Group label={t('school.location.name')} >
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
                                            className="pull-right"
                                            color="primary"
                                            disabled={isSubmitting}
                                            type="submit"
                                          >
                                            {t('submit')}
                                          </Button>
                                          <Button
                                            type="button" 
                                            color="link" 
                                            onClick={() => history.push(return_url)}
                                          >
                                              {t('cancel')}
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
    )}
  }


export default withTranslation()(withRouter(SchoolClasstypeEdit))