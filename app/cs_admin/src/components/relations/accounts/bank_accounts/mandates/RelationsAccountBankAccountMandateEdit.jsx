// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from '@apollo/react-hooks'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_BANK_ACCOUNT_MANDATE_QUERY, UPDATE_ACCOUNT_BANK_ACCOUNT_MANDATE } from './queries'
import { GET_ACCOUNT_BANK_ACCOUNTS_QUERY } from '../queries'
// import { SUBSCRIPTION_SCHEMA } from './yupSchema'
import RelationsAccountBankAccountMandateForm from './RelationsAccountBankAccountMandateForm'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";

import HasPermissionWrapper from "../../../../HasPermissionWrapper"
import { dateToLocalISO } from '../../../../../tools/date_tools'

import RelationsAccountBankAccountBase from '../RelationsAccountBankAccountBase'


function RelationsAccountBankAccountMandateEdit({ t, match, history }) {
  const accountId = match.params.account_id
  const bankAccountId = match.params.bank_account_id
  const mandateId = match.params.id
  const returnUrl = `/relations/accounts/${accountId}/bank_accounts`

  const { loading, error, data } = useQuery(GET_ACCOUNT_BANK_ACCOUNT_MANDATE_QUERY, {
    variables: {'id': mandateId},
  })
  const [updateAccountBankAccountMandate] = useMutation(UPDATE_ACCOUNT_BANK_ACCOUNT_MANDATE) 

  if (loading) return (
    <RelationsAccountBankAccountBase>
      <p>{t('general.loading_with_dots')}</p>
    </RelationsAccountBankAccountBase>
  )
  // Error
  if (error) {
    console.log(error)
    return (
      <RelationsAccountBankAccountBase>
        <p>{t('general.loading_with_dots')}</p><p>{t('general.error_sad_smiley')}</p>
      </RelationsAccountBankAccountBase>
    )
  }

  const mandate = data.accountBankAccountMandate
 

  return (
    <RelationsAccountBankAccountBase showBack={true}>
      <Card>
        <Card.Header>
          <Card.Title>{t('relations.account.bank_accounts.mandates.title_add')}</Card.Title>
        </Card.Header>
        <Formik
          initialValues={{
            reference: mandate.reference,
            content: mandate.content,
            signatureDate: mandate.signatureDate
          }}
          // validationSchema={INVOICE_GROUP_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
            console.log('submit values:')
            console.log(values)

            updateAccountBankAccountMandate({ variables: {
              input: {
                id: mandateId,
                reference: values.refrence, 
                content: values.content,
                signatureDate: dateToLocalISO(values.signatureDate)
              }
            }, refetchQueries: [
              {query: GET_ACCOUNT_BANK_ACCOUNTS_QUERY, variables: { account: accountId }}
            ]})
            .then(({ data }) => {
                console.log('got data', data)
                toast.success((t('relations.account.bank_accounts.mandates.toast_edit_success')), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                history.push(returnUrl)
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
            <RelationsAccountBankAccountMandateForm
              isSubmitting={isSubmitting}
              errors={errors}
              values={values}
              submitForm={submitForm}
              setFieldTouched={setFieldTouched}
              setFieldValue={setFieldValue}
              returnUrl={returnUrl}
            >
            </RelationsAccountBankAccountMandateForm>   
          )}
        </Formik>
      </Card>
    </RelationsAccountBankAccountBase>
  )
}


export default withTranslation()(withRouter(RelationsAccountBankAccountMandateEdit))
