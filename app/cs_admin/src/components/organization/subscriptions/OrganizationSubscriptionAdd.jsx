// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_SUBSCRIPTIONS_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { SUBSCRIPTION_SCHEMA } from './yupSchema'
import OrganizationSubscriptionForm from './OrganizationSubscriptionForm'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationMenu from "../OrganizationMenu"


const CREATE_SUBSCRIPTION = gql`
  mutation CreateSubscription($input: CreateOrganizationSubscriptionInput!) {
    createOrganizationSubscription(input: $input) {
      organizationSubscription {
        id
        displayPublic
        displayShop
        name
        description
        sortOrder
        minDuration
        classes
        subscriptionUnit
        subscriptionUnitDisplay
        reconciliationClasses
        creditValidity
        unlimited
        termsAndConditions
        organizationMembership {
          id
          name
        }
        quickStatsAmount
        financeGlaccount {
          id
          name
        }
        financeCostcenter {
          id
          name
        }
      }
    }
  }
`


class OrganizationSubscriptionAdd extends Component {
  constructor(props) {
    super(props)
    console.log("Organization subscription add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const history = this.props.history
    const return_url = "/organization/subscriptions"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.subscriptions.title_add')}</Card.Title>
                </Card.Header>
                <Query query={GET_INPUT_VALUES_QUERY} variables = {{archived: false}} >
                  {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    console.log('query data')
                    console.log(data)
                    const inputData = data

                    return (
                      
                      <Mutation mutation={CREATE_SUBSCRIPTION} onCompleted={() => history.push(return_url)}> 
                      {(createSubscription, { data }) => (
                          <Formik
                              initialValues={{ 
                                displayPublic: true,
                                displayShop: true,
                                name: "",
                                description: "",
                                sortOrder: 0,
                                minDuration: 1,
                                classes: 1,
                                subscriptionUnit: "WEEK",
                                reconciliationClasses: 0,
                                creditValidity: 1,
                                unlimited: false,
                                termsAndConditions: "",
                                organizationMembership: "",
                                quickStatsAmount: 0,
                                financeGlaccount: "",
                                financeCostcenter: ""
                              }}
                              validationSchema={SUBSCRIPTION_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  createSubscription({ variables: {
                                    input: {
                                      displayPublic: values.displayPublic,
                                      displayShop: values.displayShop,
                                      name: values.name,
                                      description: values.description,
                                      sortOrder: values.sortOrder,
                                      minDuration: values.minDuration,
                                      classes: values.classes,
                                      subscriptionUnit: values.subscriptionUnit,
                                      reconciliationClasses: values.reconciliationClasses,
                                      creditValidity: values.creditValidity,
                                      unlimited: values.unlimited,
                                      termsAndConditions: values.termsAndConditions,
                                      quickStatsAmount: values.quickStatsAmount,
                                      financeGlaccount: values.financeGlaccount,
                                      financeCostcenter: values.financeCostcenter
                                    }
                                  }, refetchQueries: [
                                      {query: GET_SUBSCRIPTIONS_QUERY, variables: {archived: false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.subscriptions.toast_add_success')), {
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
                                <OrganizationSubscriptionForm
                                  inputData={inputData}
                                  isSubmitting={isSubmitting}
                                  setFieldValue={setFieldValue}
                                  setFieldTouched={setFieldTouched}
                                  errors={errors}
                                  values={values}
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
                <HasPermissionWrapper permission="add"
                                      resource="organizationsubscription">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <OrganizationMenu active_link='subscriptions'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationSubscriptionAdd))