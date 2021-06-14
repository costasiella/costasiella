// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_CLASSPASS_GROUPS_QUERY } from './queries'
import { CLASSPASS_GROUP_SCHEMA } from './yupSchema'

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

import OrganizationMenu from '../OrganizationMenu'


const ADD_CLASSPASS_GROUP = gql`
  mutation CreateOrganizationClasspassGroup($input:CreateOrganizationClasspassGroupInput!) {
    createOrganizationClasspassGroup(input: $input) {
      organizationClasspassGroup{
        id
      }
    }
  }
`

const return_url = "/organization/classpasses/groups"

const OrganizationClasspassGroupAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('organization.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('organization.classpass_groups.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_CLASSPASS_GROUP} onCompleted={() => history.push(return_url)}> 
                {(addLocation, { data }) => (
                    <Formik
                        initialValues={{ name: '', description: '' }}
                        validationSchema={CLASSPASS_GROUP_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addLocation({ variables: {
                              input: {
                                name: values.name, 
                                description: values.description, 
                              }
                            }, refetchQueries: [
                                {query: GET_CLASSPASS_GROUPS_QUERY}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('organization.classpass_groups.toast_add_success')), {
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
                        {({ isSubmitting, errors }) => (
                            <FoForm>
                                <Card.Body>
                                  <Form.Group label={t('general.name')}>
                                    <Field type="text" 
                                            name="name" 
                                            className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                            autoComplete="off" />
                                    <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                  </Form.Group>
                                  <Form.Group label={t('general.description')}>
                                    <Field type="text" 
                                            name="description" 
                                            className={(errors.description) ? "form-control is-invalid" : "form-control"} 
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
                                  resource="organizationclasspassgroup">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link=''/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
)

export default withTranslation()(withRouter(OrganizationClasspassGroupAdd))