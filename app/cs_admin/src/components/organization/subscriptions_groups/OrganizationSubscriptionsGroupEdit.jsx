// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_SUBSCRIPTION_GROUPS_QUERY, GET_SUBSCRIPTION_GROUP_QUERY } from './queries'
import { SUBSCRIPTION_GROUP_SCHEMA } from './yupSchema'
import OrganizationSubscriptionGroupForm from './OrganizationSubscriptionsGroupForm'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationMenu from "../OrganizationMenu"


const UPDATE_SUBSCRIPTION_GROUP = gql`
  mutation UpdateOrganizationSubscriptionGroup($input: UpdateOrganizationSubscriptionGroupInput!) {
    updateOrganizationSubscriptionGroup(input: $input) {
      organizationSubscriptionGroup {
        id
      }
    }
  }
`


class OrganizationSubscriptionGroupEdit extends Component {
  constructor(props) {
    super(props)
    console.log("Organization subscriptiongroup edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/organization/subscriptions/groups"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.subscription_groups.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_SUBSCRIPTION_GROUP_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.organizationSubscriptionGroup;
                    console.log('query data')
                    console.log(data)

                    return (
                      
                      <Mutation mutation={UPDATE_SUBSCRIPTION_GROUP} onCompleted={() => history.push(return_url)}> 
                      {(updateSubscriptionGroup, { data }) => (
                          <Formik
                              initialValues={{ 
                                name: initialData.name, 
                                description: initialData.description,
                              }}
                              validationSchema={SUBSCRIPTION_GROUP_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  updateSubscriptionGroup({ variables: {
                                    input: {
                                      id: match.params.id,
                                      name: values.name,
                                      description: values.description,
                                    }
                                  }, refetchQueries: [
                                      {query: GET_SUBSCRIPTION_GROUPS_QUERY}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.subscription_groups.toast_edit_success')), {
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
                                <OrganizationSubscriptionGroupForm
                                  isSubmitting={isSubmitting}
                                  errors={errors}
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
    )}
  }


export default withTranslation()(withRouter(OrganizationSubscriptionGroupEdit))