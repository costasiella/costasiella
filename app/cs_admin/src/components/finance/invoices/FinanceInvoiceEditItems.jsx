// @flow

import React from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { v4 } from 'uuid'


import {
  Card, 
  Table
} from "tabler-react"


import { get_list_query_variables } from "./tools"
import { UPDATE_INVOICE, GET_INVOICES_QUERY } from "./queries"
import FinanceInvoiceEditItemForm from "./FinanceInvoiceEditItemForm"


export const UPDATE_INVOICE_ITEM = gql`
  mutation UpdateFinanceInvoiceItem($input: UpdateFinanceInvoiceItemInput!) {
    updateFinanceInvoiceItem(input: $input) {
      financeInvoiceItem {
        id
        productName
        description
        quantity
        price
        financeTaxRate {
          id
          name
        }
      }
    }
  }
`


function get_initial_values(node) {
  let initialValues = {
    productName: node.productName, 
    description: node.description, 
    quantity: node.quantity, 
    price: node.price, 
  }

  if (node.financeTaxRate) {
    initialValues.financeTaxRate = node.financeTaxRate.id
  }

  if (node.financeGlaccount) {
    initialValues.financeGlaccount = node.financeGlaccount.id
  }

  if (node.financeCostcenter) {
    initialValues.financeCostcenter = node.financeCostcenter.id
  }

  return initialValues

}



const FinanceInvoiceEditItems = ({ t, history, match, inputData }) => (
  <Card statusColor="blue">
    <Card.Header>
      <Card.Title>{t('general.items')}</Card.Title>
    </Card.Header>
    <Card.Body>
      <Table>
        <Table.Body>
          {inputData.financeInvoice.items.edges.map(({ node }) => (
            <Mutation mutation={UPDATE_INVOICE_ITEM}> 
              {(updateInvoiceItem, { data }) => (
                <Formik
                  initialValues={get_initial_values(node)}
                  // validationSchema={INVOICE_GROUP_SCHEMA}
                  onSubmit={(values, { setSubmitting }) => {
                    console.log('submit values:')
                    console.log(values)

                    updateInvoiceItem({ variables: {
                      input: {
                        id: node.id,
                        productName: values.productName, 
                        description: values.description,
                        quantity: values.quantity,
                        price: values.price,
                        financeTaxRate: values.financeTaxRate,
                        financeGlaccount: values.financeGlaccount,
                        financeCostcenter: values.financeCostcenter,
                      }
                    }, refetchQueries: [
                        // {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
                    ]})
                    .then(({ data }) => {
                        console.log('got data', data)
                        toast.success((t('finance.invoice.toast_edit_item_success')), {
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
                  {({ isSubmitting, errors, values, touched, handleChange, submitForm, setFieldValue, setFieldTouched }) => (
                    <FinanceInvoiceEditItemForm
                      isSubmitting={isSubmitting}
                      errors={errors}
                      values={values}
                      handleChange={handleChange}
                      submitForm={submitForm}
                      setFieldTouched={setFieldTouched}
                      setFieldValue={setFieldValue}
                      inputData={inputData}
                      node={node}
                      key={"invoice_item_" + node.id} // don't use uuid here, during re-render it causes the inputs to lose focus while typing due to a different key
                    >
                    </FinanceInvoiceEditItemForm>
                    
                  )}
                </Formik>
              )}
            </Mutation>
          ))}
        </Table.Body>
      </Table>
    </Card.Body>
  </Card>
)

export default withTranslation()(withRouter(FinanceInvoiceEditItems))