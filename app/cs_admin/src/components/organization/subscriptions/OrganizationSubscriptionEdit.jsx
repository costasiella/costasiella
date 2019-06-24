// @flow

import React, { Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SUBSCRIPTIONS_QUERY, GET_SUBSCRIPTION_QUERY } from './queries'
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


const UPDATE_SUBSCRIPTION = gql`
  mutation UpdateOrganizationSubscription($input: UpdateOrganizationSubscriptionInput!) {
    updateOrganizationSubscription(input: $input) {
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


class OrganizationSubscriptionEdit extends Component {
  constructor(props) {
    super(props)
    console.log("Organization subscription edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
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
                  <Card.Title>{t('organization.subscriptions.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_SUBSCRIPTION_QUERY} variables={{ "id": id, "archived": false}} >
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
                    const initialData = data

                    let initialMembership = ""
                    if (initialData.organizationSubscription.organizationMembership) {
                      initialMembership =  initialData.organizationSubscription.organizationMembership.id
                    } 

                    let initialGlaccount = ""
                    if (initialData.organizationSubscription.financeGlaccount) {
                      initialGlaccount =  initialData.organizationSubscription.financeGlaccount.id
                    } 

                    let initialCostcenter = ""
                    if (initialData.organizationSubscription.financeCostcenter) {
                      initialCostcenter =  initialData.organizationSubscription.financeCostcenter.id
                    } 

                    return (
                      <Mutation mutation={UPDATE_SUBSCRIPTION} onCompleted={() => history.push(return_url)}> 
                      {(createSubscription, { data }) => (
                          <Formik
                              initialValues={{ 
                                displayPublic: initialData.organizationSubscription.displayPublic,
                                displayShop: initialData.organizationSubscription.displayShop,
                                name: initialData.organizationSubscription.name,
                                description: initialData.organizationSubscription.description,
                                sortOrder: initialData.organizationSubscription.sortOrder,
                                minDuration: initialData.organizationSubscription.minDuration,
                                classes: initialData.organizationSubscription.classes,
                                subscriptionUnit: initialData.organizationSubscription.subscriptionUnit,
                                reconciliationClasses: initialData.organizationSubscription.reconciliationClasses,
                                creditValidity: initialData.organizationSubscription.creditValidity,
                                unlimited: initialData.organizationSubscription.unlimited,
                                termsAndConditions: initialData.organizationSubscription.termsAndConditions,
                                organizationMembership: initialMembership,
                                quickStatsAmount: initialData.organizationSubscription.quickStatsAmount,
                                financeGlaccount:  initialGlaccount,
                                financeCostcenter: initialCostcenter
                              }}
                              validationSchema={SUBSCRIPTION_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  createSubscription({ variables: {
                                    input: {
                                      id: match.params.id,
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
                                      {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.subscriptions.toast_edit_success')), {
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
                                  inputData={initialData}
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
                <HasPermissionWrapper permission="change"
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


export default withTranslation()(withRouter(OrganizationSubscriptionEdit))