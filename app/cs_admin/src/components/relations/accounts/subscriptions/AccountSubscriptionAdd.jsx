// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_ACCOUNT_SUBSCRIPTIONS_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
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


const CREATE_ACCOUNT_SUBSCRIPTION = gql`
  mutation CreateAccountSubscription($input: CreateAccountSubscriptionInput!) {
    createAccountSubscription(input: $input) {
      accountSubscription {
        id
        displayPublic
        account {
          id
          firstName
          lastName
          email
        }
        organizationSubscription {
          id
          name
        }
        financePaymentMethod {
          id
          name
        }
        dateStart
        dateEnd
        note
        registrationFeePaid        
      }
    }
  }
`


class AccountSubscriptionAdd extends Component {
  constructor(props) {
    super(props)
    console.log("Account subscription add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const history = this.props.history
    const match = this.props.match
    const account_id = match.params.account_id
    const return_url = "/relations/accounts/" + account_id + "/subscriptions"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
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
              <Container>
               <Page.Header title="Organization" />
               <Grid.Row>
                  <Grid.Col md={9}>
                  <Card>
                    <Card.Header>
                      <Card.Title>{t('relations.account.subscriptions_title_add')}</Card.Title>
                    </Card.Header>
                      <Mutation mutation={CREATE_SUBSCRIPTION} onCompleted={() => history.push(return_url)}> 
                      {(createSubscription, { data }) => (
                          <Formik
                              initialValues={{ 
                                organizationSubscription: null,
                                financePaymentMethod: null,
                                dateStart: new Date(),
                                dateEnd: "",
                                note: "",
                                registrationFeePaid: false
                              }}
                              validationSchema={SUBSCRIPTION_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  createSubscription({ variables: {
                                    input: {
                                      account: account_id, 
                                      organizationSubscription: values.organizationSubscription,
                                      financePaymentMethod: values.financePaymentMethod,
                                      dateStart: dateStart,
                                      dateEnd: dateEnd,
                                      note: values.Note,
                                      registrationFeePaid: values.registrationFeePaid
                                    }
                                  }, refetchQueries: [
                                      // {query: GET_SUBSCRIPTIONS_QUERY, variables: {archived: false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('relations.account.subscriptions_toast_add_success')), {
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
                    </Card>
                  </Grid.Col>
                  <Grid.Col md={3}>
                    <HasPermissionWrapper permission="add"
                                          resource="accountsubscription">
                      <Link to={return_url}>
                        <Button color="primary btn-block mb-6">
                          <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                        </Button>
                      </Link>
                    </HasPermissionWrapper>
                    <OrganizationMenu active_link='subscriptions'/>
                  </Grid.Col>
                </Grid.Row>
              </Container>
            )}}
          </Query>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(AccountSubscriptionAdd))