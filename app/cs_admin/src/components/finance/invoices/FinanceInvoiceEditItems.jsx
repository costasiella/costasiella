// @flow

import React from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import {
  Card
} from "tabler-react"


import { get_list_query_variables } from "./tools"
import { UPDATE_INVOICE, GET_INVOICES_QUERY } from "./queries"
import FinanceInvoiceEditItemForm from "./FinanceInvoiceEditItemForm"

export const UPDATE_INVOICE_ITEM = gql`
  mutation UpdateFinanceInvoiceItem($input: UpdateFinanceInvoiceItemInput!) {
    updateFinanceInvoiceItem(input: $input) {
      financeInvoiceItem {
        id
        summary
      }
    }
  }
`


const FinanceInvoiceEditItems = ({ t, history, match, data }) => (
  <Card statusColor="blue">
    <Card.Header>
      <Card.Title>{t('general.items')}</Card.Title>
    </Card.Header>
    <Card.Body>
      {data.financeInvoice.items.edges.map(({ node }) => (
        <Mutation mutation={UPDATE_INVOICE}> 
          {(updateInvoice, { data }) => (
            <Formik
              initialValues={{ 
                productName: node.productName, 
                description: node.description, 
                quantity: node.quantity, 
                price: node.price, 
                financeTaxRate: node.financeTaxRate, 
                financeGlaccount: node.financeGlaccount, 
                financeCostcenter: node.financeCostcenter, 
              }}
              // validationSchema={INVOICE_GROUP_SCHEMA}
              onSubmit={(values, { setSubmitting }) => {
                console.log('submit values:')
                console.log(values)

                updateInvoice({ variables: {
                  input: {
                    id: match.params.id,
                    productName: values.productName, 
                    description: values.description,
                    quantity: values.quantity,
                    price: values.price,
                    financeTaxRate: values.financeTaxRate,
                    financeGlaccount: values.financeGlaccount,
                    financeCostcenter: values.financeCostcenter,
                  }
                }, refetchQueries: [
                    {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
                ]})
                .then(({ data }) => {
                    console.log('got data', data)
                    toast.success((t('finance.invoice.toast_edit_summary_success')), {
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
              {({ isSubmitting, errors, values, touched, handleChange, submitForm }) => (
                <FinanceInvoiceEditItemForm
                  isSubmitting={isSubmitting}
                  errors={errors}
                  values={values}
                  handleChange={handleChange}
                  submitForm={submitForm}
                >
                </FinanceInvoiceEditItemForm>
              )}
            </Formik>
          )}
        </Mutation>
      ))}
    </Card.Body>
  </Card>
)

export default withTranslation()(withRouter(FinanceInvoiceEditItems))