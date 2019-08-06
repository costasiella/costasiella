// @flow

import React from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo"
import { useMutation } from '@apollo/react-hooks';
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
import { UPDATE_INVOICE_ITEM } from "./queries"
import FinanceInvoiceEditItemProductNameForm from "./FinanceInvoiceEditItemProductNameForm"
import FinanceInvoiceEditItemDescriptionForm from "./FinanceInvoiceEditItemDescriptionForm"





function UpdateProductName({t, node}) {
  let input;
  const [updateInvoiceItem, { data }] = useMutation(UPDATE_INVOICE_ITEM)

    return (
      <Formik
        initialValues={{
          productName: node.productName
        }}
        // validationSchema={INVOICE_GROUP_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log('submit values:')
          console.log(values)

          updateInvoiceItem({ variables: {
            input: {
              id: node.id,
              productName: values.productName, 
            }
          }, refetchQueries: [
              // {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
          ]})
          .then(({ data }) => {
              console.log('got data', data)
              toast.success((t('finance.invoice.toast_edit_item_product_name_success')), {
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
          <FinanceInvoiceEditItemProductNameForm
            isSubmitting={isSubmitting}
            errors={errors}
            values={values}
            handleChange={handleChange}
            submitForm={submitForm}
            key={"invoice_item_product_name" + node.id} // don't use uuid here, during re-render it causes the inputs to lose focus while typing due to a different key
          >
          </FinanceInvoiceEditItemProductNameForm>   
        )}
      </Formik>
    )
}



const FinanceInvoiceEditItems = ({ t, history, match, inputData }) => (
  <Card statusColor="blue">
    <Card.Header>
      <Card.Title>{t('general.items')}</Card.Title>
    </Card.Header>
    <Card.Body>
      <Table>
        <Table.Header>
          <Table.ColHeader>{t("general.product_name")}</Table.ColHeader>
          <Table.ColHeader>{t("general.description")}</Table.ColHeader>
          <Table.ColHeader>{t("general.quantity_short")}</Table.ColHeader>
          <Table.ColHeader>{t("general.price")}</Table.ColHeader>
          <Table.ColHeader>{t("general.tax")}</Table.ColHeader>
          <Table.ColHeader>{t("general.subtotal")}</Table.ColHeader>
          <Table.ColHeader>{t("general.tax")}</Table.ColHeader>
          <Table.ColHeader>{t("general.total")}</Table.ColHeader>
        </Table.Header>
        <Table.Body>
          {inputData.financeInvoice.items.edges.map(({ node }) => (
            <Table.Row>
              <Table.Col>
                <UpdateProductName t={t} node={node} />
              </Table.Col>
              <Table.Col>
                <Mutation mutation={UPDATE_INVOICE_ITEM}> 
                  {(updateInvoiceItem, { data }) => (
                    <Formik
                      initialValues={{
                        description: node.description
                      }}
                      // validationSchema={INVOICE_GROUP_SCHEMA}
                      onSubmit={(values, { setSubmitting }) => {
                        console.log('submit values:')
                        console.log(values)

                        updateInvoiceItem({ variables: {
                          input: {
                            id: node.id,
                            description: values.description, 
                          }
                        }, refetchQueries: [
                            // {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
                        ]})
                        .then(({ data }) => {
                            console.log('got data', data)
                            toast.success((t('finance.invoice.toast_edit_item_description_success')), {
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
                        <FinanceInvoiceEditItemDescriptionForm
                          isSubmitting={isSubmitting}
                          errors={errors}
                          values={values}
                          handleChange={handleChange}
                          submitForm={submitForm}
                          key={"invoice_item_description" + node.id} // don't use uuid here, during re-render it causes the inputs to lose focus while typing due to a different key
                        >
                        </FinanceInvoiceEditItemDescriptionForm>
                        
                      )}
                    </Formik>
                  )}
                </Mutation>
              </Table.Col>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    </Card.Body>
  </Card>
)

export default withTranslation()(withRouter(FinanceInvoiceEditItems))