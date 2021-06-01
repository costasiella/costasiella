// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'
import { v4 } from "uuid"

import { GET_CLASSPASSES_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { CLASSPASS_SCHEMA } from './yupSchema'


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
import OrganizationClasspassForm from "./OrganizationClasspassForm"


const CREATE_CLASSPASS = gql`
  mutation CreateClasspass($input: CreateOrganizationClasspassInput!) {
    createOrganizationClasspass(input: $input) {
      organizationClasspass {
        id
        displayPublic
        displayShop
        name
        description
        price
        financeTaxRate {
          id
          name
        }
        validity
        validityUnit
        classes
        unlimited
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


class OrganizationClasspassAdd extends Component {
  constructor(props) {
    super(props)
    console.log("Organization classpass add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/organization/classpasses"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.classpasses.title_add')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_INPUT_VALUES_QUERY} variables={{ id, archived: false }} >
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

                    return (
                      
                      <Mutation mutation={CREATE_CLASSPASS} onCompleted={() => history.push(return_url)}> 
                      {(createMembership, { data }) => (
                          <Formik
                              initialValues={{ 
                                displayPublic: true,
                                displayShop: true,
                                trialPass: false,
                                trialTimes: 1,
                                name: "",
                                description: "",
                                price: 0,
                                financeTaxRate: "",
                                validity: 1,
                                validityUnit: "MONTHS",
                                classes: 1,
                                unlimited: false,
                                organizationMembership: "",
                                quickStatsAmount: 0,
                                financeGlaccount: "",
                                financeCostcenter: ""
                              }}
                              validationSchema={CLASSPASS_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  createMembership({ variables: {
                                    input: {
                                      displayPublic: values.displayPublic,
                                      displayShop: values.displayShop,
                                      trialPass: values.trialPass,
                                      trialTimes: values.trialTimes,
                                      name: values.name,
                                      description: values.description,
                                      price: values.price,
                                      financeTaxRate: values.financeTaxRate,
                                      validity: values.validity,
                                      validityUnit: values.validityUnit,
                                      classes: values.classes,
                                      unlimited: values.unlimited,
                                      organizationMembership: values.organizationMembership,
                                      quickStatsAmount: values.quickStatsAmount,
                                      financeGlaccount: values.financeGlaccount,
                                      financeCostcenter: values.financeCostcenter
                                    }
                                  }, refetchQueries: [
                                      {query: GET_CLASSPASSES_QUERY, variables: {"archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.classpasses.toast_add_success')), {
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
                                <OrganizationClasspassForm 
                                  initialData = {initialData}
                                  isSubmitting = {isSubmitting}
                                  setFieldValue = {setFieldValue}
                                  setFieldTouched = {setFieldTouched}
                                  errors = {errors}
                                  values = {values}
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
                                      resource="organizationclasspass">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <OrganizationMenu active_link='classpasses'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationClasspassAdd))