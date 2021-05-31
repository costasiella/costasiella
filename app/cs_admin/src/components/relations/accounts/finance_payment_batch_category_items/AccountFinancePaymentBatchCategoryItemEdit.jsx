// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { 
  GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEMS_QUERY, 
  GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM_QUERY, 
  UPDATE_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM
} from './queries'
import { ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM_SCHEMA } from './yupSchema'
import AccountFinancePaymentBatchCategoryItemsForm from './AccountFinancePaymentBatchCategoryItemsForm'

import {
  Card,
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import AccountFinancePaymentBatchCategoryItemsBase from "./AccountFinancePaymentBatchCategoryItemsBase"

function AccountFinancePaymentBatchCategoryItemEdit({ t, history, match }) {
  const accountId = match.params.account_id
  const accountFinancePaymentBatchCategoryItemId = match.params.id
  const returnUrl = `/relations/accounts/${accountId}/finance_payment_batch_category_items`
  const cardTitle = t('relations.account.finance_payment_batch_category_items.title_edit')

  const { loading, error, data } = useQuery(GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM_QUERY, { variables: {
    id: accountFinancePaymentBatchCategoryItemId
  }})
  const [updateAccountFinancePaymentBatchCategoryItem] = useMutation(
    UPDATE_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM
  )

  if (loading) {
    return (
      <AccountFinancePaymentBatchCategoryItemsBase showBack={true}>
        <Card title={cardTitle}>
          <Card.Body>
            {t("general.loading_with_dots")}
          </Card.Body>
        </Card>
      </AccountFinancePaymentBatchCategoryItemsBase>
    )
  }

  if (error) {
    return (
      <AccountFinancePaymentBatchCategoryItemsBase showBack={true}>
        <Card title={cardTitle}>
          <Card.Body>
            {t("relations.account.finance_payment_batch_category_items.error_loading")}
          </Card.Body>
        </Card>
      </AccountFinancePaymentBatchCategoryItemsBase>
    )
  }

  const inputData = data
  const initialValues = data.accountFinancePaymentBatchCategoryItem

  return (
    <AccountFinancePaymentBatchCategoryItemsBase showBack={true}>
      <Card title={cardTitle}>
        <Formik
          initialValues={{ 
            financePaymentBatchCategory: initialValues.financePaymentBatchCategory.id,
            year: initialValues.year,
            month: initialValues.month,
            amount: initialValues.amount,
            description: initialValues.description
          }}
          validationSchema={ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM_SCHEMA}
          onSubmit={(values, { setSubmitting }, errors) => {
              console.log('submit values:')
              console.log(values)
              console.log(errors)

              updateAccountFinancePaymentBatchCategoryItem({ variables: {
                input: {
                  id: accountFinancePaymentBatchCategoryItemId, 
                  amount: values.amount,
                  year: values.year,
                  month: values.month,
                  financePaymentBatchCategory: values.financePaymentBatchCategory,
                  description: values.description
                }
              }, refetchQueries: [
                  {query: GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEMS_QUERY, variables: {account: accountId}}
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  history.push(returnUrl)
                  toast.success((t('relations.account.finance_payment_batch_category_items.toast_edit_success')), {
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
          {({ isSubmitting, errors, values }) => (
            <AccountFinancePaymentBatchCategoryItemsForm
              inputData={inputData}
              isSubmitting={isSubmitting}
              errors={errors}
              returnUrl={returnUrl}
            >
              {console.log(errors)}
            </AccountFinancePaymentBatchCategoryItemsForm>
          )}
        </Formik>
      </Card>
    </AccountFinancePaymentBatchCategoryItemsBase>
  )
}

export default withTranslation()(withRouter(AccountFinancePaymentBatchCategoryItemEdit))
