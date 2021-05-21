// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_BANK_ACCOUNTS_QUERY, UPDATE_ACCOUNT_BANK_ACCOUNT } from './queries'
// import { ACCOUNT_SCHEMA } from './yupSchema'

import {
  Card,
} from "tabler-react"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import RelationsAccountBankAccountBase from "./RelationsAccountBankAccountBase"
import RelationsAccountBankAccountForm from "./RelationsAccountBankAccountForm"



function RelationsAccountBankAccount({ t, match, history }) {
  const accountId = match.params.account_id
  const returnUrl = "/relations/accounts"

  const { loading, error, data } = useQuery(GET_ACCOUNT_BANK_ACCOUNTS_QUERY, {
    variables: { account: accountId }
  })

  const [ updateAccountBankAccount ] = useMutation(UPDATE_ACCOUNT_BANK_ACCOUNT)

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

  const accountBankAccounts = data.accountBankAccounts
  const accountBankAccount = accountBankAccounts.edges[0].node

  return (
    <RelationsAccountBankAccountBase bankAccountId={accountBankAccount.id}>
      <Card title={t('relations.account.bank_accounts.title')}>
        <Formik
          initialValues={{ 
            number: accountBankAccount.number,
            holder: accountBankAccount.holder,
            bic: accountBankAccount.bic
          }}
          // validationSchema={ACCOUNT_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
              console.log('submit values:')
              console.log(values)

              let input_vars = {
                id: accountBankAccount.id,
                number: values.number,
                holder: values.holder,
                bic: values.bic              
              }

              updateAccountBankAccount({ variables: {
                input: input_vars
              }, refetchQueries: [
                  // Refresh local cached results for this account
                  {query: GET_ACCOUNT_BANK_ACCOUNTS_QUERY, variables: { account: accountId }}
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  toast.success((t('relations.account.bank_accounts.toast_edit_success')), {
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
            <RelationsAccountBankAccountForm
              isSubmitting={isSubmitting}
              errors={errors}
              values={values}
            />
          )}
        </Formik>
      </Card>
    </RelationsAccountBankAccountBase>
  )
}


export default withTranslation()(withRouter(RelationsAccountBankAccount))