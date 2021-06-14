// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_SUBSCRIPTION_GROUPS_QUERY } from './queries'
import { SUBSCRIPTION_GROUP_SCHEMA } from './yupSchema'
import OrganizationSubscriptionGroupForm from './OrganizationSubscriptionsGroupForm'

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


const ADD_SUBSCRIPTION_GROUP = gql`
  mutation CreateOrganizationSubscriptionGroup($input:CreateOrganizationSubscriptionGroupInput!) {
    createOrganizationSubscriptionGroup(input: $input) {
      organizationSubscriptionGroup{
        id
      }
    }
  }
`

const return_url = "/organization/subscriptions/groups"

const OrganizationSubscriptionGroupAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('organization.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('organization.subscription_groups.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_SUBSCRIPTION_GROUP} onCompleted={() => history.push(return_url)}> 
                {(addLocation, { data }) => (
                    <Formik
                        initialValues={{ name: '', description: '' }}
                        validationSchema={SUBSCRIPTION_GROUP_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addLocation({ variables: {
                              input: {
                                name: values.name, 
                                description: values.description,
                              }
                            }, refetchQueries: [
                                {query: GET_SUBSCRIPTION_GROUPS_QUERY}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('organization.subscription_groups.toast_add_success')), {
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
                          <OrganizationSubscriptionGroupForm
                            isSubmitting={isSubmitting}
                            errors={errors}
                            return_url={return_url}
                          />
                        )}
                    </Formik>
                )}
                </Mutation>
          </Card>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="organizationsubscriptiongroup">
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

export default withTranslation()(withRouter(OrganizationSubscriptionGroupAdd))