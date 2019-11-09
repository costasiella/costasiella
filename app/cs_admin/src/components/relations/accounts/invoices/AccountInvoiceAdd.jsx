// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from '@apollo/react-hooks'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTIONS_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { SUBSCRIPTION_SCHEMA } from './yupSchema'
import AccountInvoiceAddForm from './AccountInvoiceAddForm'

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


const CREATE_ACCOUNT_INVOICE= gql`
  mutation CreateFinanceInvoice($input: CreateFinanceInvoiceInput!) {
    createFinanceInvoice(input: $input) {
      financeInvoice {
        id
      }
    }
  }
`


function AccountInvoiceAdd({ t, match, history }) {
  const account_id = match.params.account_id
  const return_url = "/relations/accounts/" + account_id + '/invoices'
  const { loading: queryLoading, error: queryError, data: queryData } = useQuery(
    GET_INPUT_VALUES_QUERY, {
      variables: {
        accountId: account_id
      }
    }
  )
  const [createInvoice, { data }] = useMutation(CREATE_ACCOUNT_INVOICE, {
    // onCompleted = () => history.push('/finance/invoices/edit/')
  }) 

  // Query
  // Loading
  if (queryLoading) return <p>{t('general.loading_with_dots')}</p>
  // Error
  if (queryError) {
    console.log(queryError)
    return <p>{t('general.error_sad_smiley')}</p>
  }
  
  console.log(queryData)
  const account = queryData.account


  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={account.firstName + " " + account.lastName} />
          <Grid.Row>
              <Grid.Col md={9}>
                <Card>
                  <Card.Header>
                    <Card.Title>{t('relations.account.invoices.title_add')}</Card.Title>
                  </Card.Header>
                  <Formik
                    initialValues={{
                      financeInvoiceGroup: "",
                      summary: ""
                    }}
                    // validationSchema={INVOICE_GROUP_SCHEMA}
                    onSubmit={(values, { setSubmitting }) => {
                      console.log('submit values:')
                      console.log(values)

                      createInvoice({ variables: {
                        input: {
                          account: account_id, 
                          financeInvoiceGroup: values.financeInvoiceGroup,
                          summary: values.summary
                        }
                      }, refetchQueries: [
                      ]})
                      .then(({ data }) => {
                          console.log('got data', data)
                          toast.success((t('relations.account.invoices.title_add')), {
                              position: toast.POSITION.BOTTOM_RIGHT
                            })
                          history.push('/finance/invoices/edit/' + data.createFinanceInvoice.financeInvoice.id)
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
                    {({ isSubmitting, errors, values, submitForm, setFieldTouched, setFieldValue }) => (
                      <AccountInvoiceAddForm
                        inputData={queryData}
                        isSubmitting={isSubmitting}
                        errors={errors}
                        values={values}
                        submitForm={submitForm}
                        setFieldTouched={setFieldTouched}
                        setFieldValue={setFieldValue}
                        return_url={return_url}
                      >
                      </AccountInvoiceAddForm>   
                    )}
                  </Formik>
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
                <ProfileMenu 
                  active_link='invoices'
                  account_id={match.params.account_id}
                />
              </Grid.Col>
            </Grid.Row>
          </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(AccountInvoiceAdd))
