// @flow

import React, { useContext } from 'react'
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'

import AppSettingsContext from '../../../context/AppSettingsContext'
import moment from 'moment'

import { GET_ACCOUNT_BANK_ACCOUNTS_QUERY, UPDATE_ACCOUNT_BANK_ACCOUNT } from './queries'
import { DELETE_ACCOUNT_BANK_ACCOUNT_MANDATE } from './mandates/queries'
// import { ACCOUNT_SCHEMA } from './yupSchema'

import {
  Button,
  Card, 
  Grid,
  Icon
} from "tabler-react"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import confirm_delete from "../../../../tools/confirm_delete"

import RelationsAccountBankAccountBase from "./RelationsAccountBankAccountBase"
import RelationsAccountBankAccountForm from "./RelationsAccountBankAccountForm"



function RelationsAccountBankAccount({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  
  const accountId = match.params.account_id
  const returnUrl = "/relations/accounts"

  const { loading, error, data } = useQuery(GET_ACCOUNT_BANK_ACCOUNTS_QUERY, {
    variables: { account: accountId }
  })

  const [ updateAccountBankAccount ] = useMutation(UPDATE_ACCOUNT_BANK_ACCOUNT)
  const [ deleteAccountBankAccountMandate ] = useMutation(DELETE_ACCOUNT_BANK_ACCOUNT_MANDATE)

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
  const mandates = accountBankAccount.mandates
  console.log(accountBankAccount)

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
      {(mandates.edges.length) ? <h5>{t("relations.account.bank_accounts.mandates.title")}</h5> : ""}
      <Grid.Row>
      {mandates.edges.map(({ node }) => (
        <Grid.Col md={6}>
          <Card title={t("general.ID") + ": " + node.reference}>
            <Card.Body>
              {t("relations.account.bank_accounts.mandates.signature_date")} {moment(node.signatureDate).format(dateFormat)}
              <div dangerouslySetInnerHTML={{ __html: node.content}} />
            </Card.Body>
            <Card.Footer>
              <Button 
                className="pull-right"
                color="danger"
                type="button"
                onClick={() => {
                  confirm_delete({
                    t: t,
                    msgConfirm: t("relations.account.bank_accounts.mandates.delete_confirm_msg"),
                    msgDescription: <p>{node.reference}</p>,
                    msgSuccess: t('relations.account.bank_accounts.mandates.deleted'),
                    deleteFunction: deleteAccountBankAccountMandate,
                    functionVariables: { 
                      variables: {
                        input: {
                          id: node.id
                        }
                      }, 
                      refetchQueries: [
                        {query: GET_ACCOUNT_BANK_ACCOUNTS_QUERY, variables: { account: accountId} } 
                      ]
                    }
                  })
                }}
              >
                <Icon name="trash-2" />
              </Button>
              <Link to={`/relations/accounts/${accountId}/bank_accounts/${accountBankAccount.id}/mandates/edit/${node.id}`}>
                <Button
                  type="button" 
                  color="secondary" 
                >
                    {t('general.edit')}
                </Button>
              </Link>
            </Card.Footer>
          </Card>
        </Grid.Col>
      ))}
      </Grid.Row>
    </RelationsAccountBankAccountBase>
  )
}


export default withTranslation()(withRouter(RelationsAccountBankAccount))