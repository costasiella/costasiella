// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_MEMBERSHIPS_QUERY, GET_ACCOUNT_MEMBERSHIP_QUERY } from './queries'
import { MEMBERSHIP_SCHEMA } from './yupSchema'
import AccountMembershipForm from './AccountMembershipForm'

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
import { dateToLocalISO } from '../../../../tools/date_tools'

import ProfileMenu from "../ProfileMenu"


const UPDATE_ACCOUNT_MEMBERSHIP = gql`
  mutation UpdateAccountMembership($input: UpdateAccountMembershipInput!) {
    updateAccountMembership(input: $input) {
      accountMembership {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationMembership {
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
      }
    }
  }
`


class AccountMembershipEdit extends Component {
  constructor(props) {
    super(props)
    console.log("Account membership add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const history = this.props.history
    const match = this.props.match
    const id = match.params.id
    const account_id = match.params.account_id
    const return_url = "/relations/accounts/" + account_id + "/memberships"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
        <Query query={GET_ACCOUNT_MEMBERSHIP_QUERY} variables = {{archived: false,  accountId: account_id, id: id}} >
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
            const account = data.account
            const initialdata = data.accountMembership

            let initialPaymentMethod = ""
            if (initialdata.financePaymentMethod) {
              initialPaymentMethod = initialdata.financePaymentMethod.id
            }

            return (
              <Container>
               <Page.Header title={account.firstName + " " + account.lastName} />
               <Grid.Row>
                  <Grid.Col md={9}>
                  <Card>
                    <Card.Header>
                      <Card.Title>{t('relations.account.memberships.title_edit')}</Card.Title>
                    </Card.Header>
                      <Mutation mutation={UPDATE_ACCOUNT_MEMBERSHIP} onCompleted={() => history.push(return_url)}> 
                      {(updateMembership, { data }) => (
                          <Formik
                              initialValues={{ 
                                organizationMembership: initialdata.organizationMembership.id,
                                financePaymentMethod: initialPaymentMethod,
                                dateStart: initialdata.dateStart,
                                dateEnd: initialdata.dateEnd,
                                note: initialdata.note,
                                registrationFeePaid: initialdata.registrationFeePaid
                              }}
                              validationSchema={MEMBERSHIP_SCHEMA}
                              onSubmit={(values, { setSubmitting }, errors) => {
                                  console.log('submit values:')
                                  console.log(values)
                                  console.log(errors)

                                  
                                  let dateEnd
                                  if (values.dateEnd) {
                                    dateEnd = dateToLocalISO(values.dateEnd)
                                  } else {
                                    dateEnd = values.dateEnd
                                  }

                                  updateMembership({ variables: {
                                    input: {
                                      id: id,
                                      organizationMembership: values.organizationMembership,
                                      financePaymentMethod: values.financePaymentMethod,
                                      dateStart: dateToLocalISO(values.dateStart),
                                      dateEnd: dateEnd,
                                      note: values.note,
                                      registrationFeePaid: values.registrationFeePaid
                                    }
                                  }, refetchQueries: [
                                      {query: GET_ACCOUNT_MEMBERSHIPS_QUERY, variables: {archived: false, accountId: account_id}}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('relations.account.memberships.toast_edit_success')), {
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
                                <AccountMembershipForm
                                  inputData={inputData}
                                  isSubmitting={isSubmitting}
                                  setFieldValue={setFieldValue}
                                  setFieldTouched={setFieldTouched}
                                  errors={errors}
                                  values={values}
                                  return_url={return_url}
                                >
                                  {console.log(errors)}
                                </AccountMembershipForm>
                              )}
                          </Formik>
                      )}
                      </Mutation>
                    </Card>
                  </Grid.Col>
                  <Grid.Col md={3}>
                    <HasPermissionWrapper permission="change"
                                          resource="accountmembership">
                      <Link to={return_url}>
                        <Button color="primary btn-block mb-6">
                          <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                        </Button>
                      </Link>
                    </HasPermissionWrapper>
                    <ProfileMenu account_id={account_id} active_link='memberships'/>
                  </Grid.Col>
                </Grid.Row>
              </Container>
            )}}
          </Query>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(AccountMembershipEdit))
