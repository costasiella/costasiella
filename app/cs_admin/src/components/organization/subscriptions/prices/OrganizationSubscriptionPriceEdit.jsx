// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SUBSCRIPTION_PRICES_QUERY, GET_SUBSCRIPTION_PRICE_QUERY } from './queries'
import { GET_SUBSCRIPTIONS_QUERY } from '../queries'

import { SUBSCRIPTION_PRICE_SCHEMA } from './yupSchema'
import OrganizationSubscriptionPriceForm from './OrganizationSubscriptionPriceForm'
import { dateToLocalISO } from '../../../../tools/date_tools'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationMenu from "../../OrganizationMenu"


const UPDATE_SUBSCRIPTION_PRICE = gql`
  mutation UpdateOrganizationSubscriptionPrice($input: UpdateOrganizationSubscriptionPriceInput!) {
    updateOrganizationSubscriptionPrice(input: $input) {
      organizationSubscriptionPrice {
        id
        organizationSubscription {
          id
          name
        }
        price
        financeTaxRate {
          id
          name
        }
        dateStart
        dateEnd
      }
    }
  }
`


class OrganizationSubscriptionPriceEdit extends Component {
  constructor(props) {
    super(props)
    console.log("Organization location room edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const subscription_id = match.params.subscription_id
    const return_url = "/organization/subscriptions/prices/" + subscription_id

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.subscription_prices.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_SUBSCRIPTION_PRICE_QUERY} variables={{ id, archived: false }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.organizationSubscriptionPrice
                    console.log('query data')
                    console.log(data)
                    const inputData = data

                    return (
                      
                      <Mutation mutation={UPDATE_SUBSCRIPTION_PRICE} onCompleted={() => history.push(return_url)}> 
                      {(updateSubscriptionPrice, { data }) => (
                          <Formik
                              initialValues={{ 
                                price: initialData.price, 
                                financeTaxRate: initialData.financeTaxRate.id,
                                dateStart: initialData.dateStart,
                                dateEnd: initialData.dateEnd,
                              }}
                              validationSchema={SUBSCRIPTION_PRICE_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  let dateEnd
                                  if (values.dateEnd) {
                                    if (values.dateEnd instanceof Date) {
                                      dateEnd = dateToLocalISO(values.dateEnd)
                                    } else {
                                      dateEnd = values.dateEnd
                                    }
                                  } else {
                                    dateEnd = values.dateEnd
                                  }

                                  let dateStart
                                  if (values.dateStart instanceof Date) {
                                    dateStart = dateToLocalISO(values.dateStart)
                                  } else {
                                    // Input hasn't changed and DatePicket hasn't made a Date object out of it
                                    dateStart = values.dateStart
                                  }

                                  updateSubscriptionPrice({ variables: {
                                    input: {
                                      id: match.params.id,
                                      price: values.price,
                                      financeTaxRate: values.financeTaxRate,
                                      dateStart: dateStart,
                                      dateEnd: dateEnd,
                                    }
                                  }, refetchQueries: [
                                    {query: GET_SUBSCRIPTION_PRICES_QUERY, variables: { organizationSubscription: match.params.subscription_id }},
                                    {query: GET_SUBSCRIPTIONS_QUERY, variables: { "archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.subscription_prices.toast_edit_success')), {
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
                              {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
                                <OrganizationSubscriptionPriceForm
                                  inputData={inputData}
                                  isSubmitting={isSubmitting}
                                  setFieldTouched={setFieldTouched}
                                  setFieldValue={setFieldValue}
                                  errors={errors}
                                  values={values}
                                  return_url={return_url}
                                >
                                  {console.log(errors)}
                                </OrganizationSubscriptionPriceForm>
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
                                      resource="organizationlocationroom">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <OrganizationMenu active_link='locations'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationSubscriptionPriceEdit))