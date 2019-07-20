// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNTS_QUERY, GET_ACCOUNT_QUERY } from './queries'
import { ACCOUNT_SCHEMA } from './yupSchema'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { dateToLocalISO } from '../../../tools/date_tools'
import ProfileCardSmall from "../../ui/ProfileCardSmall"

import { get_list_query_variables } from "./tools"
import RelationsAccountsBack from "./RelationsAccountsBack"
import RelationsAccountProfileForm from "./RelationsAccountProfileForm"

// import OrganizationMenu from "../OrganizationMenu"
import ProfileMenu from "./ProfileMenu"


const UPDATE_ACCOUNT = gql`
  mutation UpdateAccount($input:UpdateAccountInput!) {
    updateAccount(input: $input) {
      account {
        id
        firstName
        lastName
        email
      }
    }
  }
`


class RelationsAccountProfile extends Component {
  constructor(props) {
    super(props)
    console.log("Organization profile props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const account_id = match.params.account_id
    const return_url = "/relations/accounts"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Query query={GET_ACCOUNT_QUERY} variables={{ id: account_id }} >
              {({ loading, error, data, refetch }) => {
                  // Loading
                  if (loading) return <p>{t('general.loading_with_dots')}</p>
                  // Error
                  if (error) {
                    console.log(error)
                    return <p>{t('general.error_sad_smiley')}</p>
                  }
                  
                  const initialData = data.account;
                  console.log('query data')
                  console.log(data)

                  // DatePicker doesn't like a string as an initial value
                  // This makes it a happy DatePicker :)
                  let dateOfBirth = null
                  if (initialData.dateOfBirth) {
                    dateOfBirth = new Date(initialData.dateOfBirth)
                  }

                  return (
                    <div>
                      <Page.Header title={initialData.firstName + " " + initialData.lastName}>
                        <RelationsAccountsBack />
                      </Page.Header>
                      <Grid.Row>
                        <Grid.Col md={9}>
                        <Card>
                          <Card.Header>
                            <Card.Title>{t('relations.accounts.profile')}</Card.Title>
                            {console.log(match.params.account_id)}
                          </Card.Header>
                        <Mutation mutation={UPDATE_ACCOUNT}> 
                         {(updateAccount, { data }) => (
                          <Formik
                            initialValues={{ 
                              customer: initialData.customer, 
                              teacher: initialData.teacher, 
                              employee: initialData.employee, 
                              firstName: initialData.firstName, 
                              lastName: initialData.lastName, 
                              email: initialData.email,
                              dateOfBirth: dateOfBirth,
                              gender: initialData.gender,
                              emergency: initialData.emergency,
                              phone: initialData.phone,
                              mobile: initialData.mobile,
                              address: initialData.address,
                              postcode: initialData.postcode,
                              city: initialData.city,
                              country: initialData.country,
                            }}
                            validationSchema={ACCOUNT_SCHEMA}
                            onSubmit={(values, { setSubmitting }) => {
                                console.log('submit values:')
                                console.log(values)

                                let input_vars = {
                                  id: match.params.account_id,
                                  customer: values.customer,
                                  teacher: values.teacher,
                                  employee: values.employee,
                                  firstName: values.firstName,
                                  lastName: values.lastName,
                                  email: values.email,
                                  gender: values.gender,
                                  emergency: values.emergency,
                                  phone: values.phone,
                                  mobile: values.mobile,
                                  address: values.address,
                                  postcode: values.postcode,
                                  city: values.city,
                                  country: values.country
                                }

                                if (values.dateOfBirth) {
                                  input_vars['dateOfBirth'] = dateToLocalISO(values.dateOfBirth)
                                } 

                                updateAccount({ variables: {
                                  input: input_vars
                                }, refetchQueries: [
                                    // Refetch list
                                    {query: GET_ACCOUNTS_QUERY, variables: get_list_query_variables()},
                                    // Refresh local cached results for this account
                                    {query: GET_ACCOUNT_QUERY, variables: {"id": match.params.account_id}}
                                ]})
                                .then(({ data }) => {
                                    console.log('got data', data)
                                    toast.success((t('relations.accounts.toast_edit_success')), {
                                        position: toast.POSITION.BOTTOM_RIGHT
                                      })
                                    setSubmitting(false)
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
                              <RelationsAccountProfileForm
                                isSubmitting={isSubmitting}
                                setFieldTouched={setFieldTouched}
                                setFieldValue={setFieldValue}
                                errors={errors}
                                values={values}
                              />
                            )}
                          </Formik>
                        )}
                      </Mutation>
                    </Card>
                    </Grid.Col>                                    
                    <Grid.Col md={3}>
                      <ProfileCardSmall user={initialData}/>
                      <ProfileMenu 
                        active_link='profile'
                        account_id={account_id}
                      /> 
                    </Grid.Col>
                  </Grid.Row>
                </div>
              )}}
            </Query>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(RelationsAccountProfile))