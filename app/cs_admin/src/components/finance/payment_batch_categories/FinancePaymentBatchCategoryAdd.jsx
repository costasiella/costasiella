// @flow

import React from 'react'
import { useMutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_PAYMENT_BATCH_CATEGORIES_QUERY } from './queries'
import { PAYMENT_BATCH_CATEGORY_SCHEMA } from './yupSchema'
import { get_list_query_variables } from "./tools"


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import FinanceMenu from '../FinanceMenu'
import FinancePaymentBatchCategoriesBase from './FinancePaymentBatchCategoriesBase'
import FinancePaymentBatchCategoryForm from './FinancePaymentBatchCategoryForm'

const ADD_PAYMENT_BATCH_CATEGORY = gql`
  mutation CreateFinancePaymentBatchCategory($input:CreateFinancePaymentBatchCategoryInput!) {
    createFinancePaymentBatchCategory(input: $input) {
      financePaymentBatchCategory {
        id
      }
    }
  }
`

function FinancePaymentBatchCategoryAdd({ t, history }) {
  const returnUrl = "/finance/paymentbatchcategories"
  const [addFinancePaymentBatchCategory] = useMutation(ADD_PAYMENT_BATCH_CATEGORY, {
    onCompleted: () => history.push(returnUrl),
  })

  return (
    <FinancePaymentBatchCategoriesBase showBack={true}>
      <Card>
        <Card.Header>
          <Card.Title>{t('finance.payment_batch_categories.title_add')}</Card.Title>
        </Card.Header>
        <Formik
          initialValues={{ name: '', batchCategoryType: "COLLECTION", description: '' }}
          validationSchema={PAYMENT_BATCH_CATEGORY_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
            addFinancePaymentBatchCategory({ variables: {
              input: {
                name: values.name, 
                batchCategoryType: values.batchCategoryType,
                description: values.description
              }
            }, refetchQueries: [
                {query: GET_PAYMENT_BATCH_CATEGORIES_QUERY, variables: get_list_query_variables()}
            ]})
            .then(({ data }) => {
                console.log('got data', data);
                toast.success((t('finance.payment_batch_categories.toast_add_success')), {
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
          {({ isSubmitting, errors }) => (
              <FinancePaymentBatchCategoryForm
                create={true}
                isSubmitting={isSubmitting}
                errors={errors}
                returnUrl={returnUrl}
              />
          )}
        </Formik>
      </Card>
    </FinancePaymentBatchCategoriesBase>
  )
}

export default withTranslation()(withRouter(FinancePaymentBatchCategoryAdd))