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


import { UPDATE_INVOICE } from "./queries"
import FinanceInvoiceEditSummaryForm from "./FinanceInvoiceEditSummaryForm"


const FinanceInvoiceEditSummary = ({ t, history, match, initialData }) => (
  <Card statusColor="blue">
    <Card.Header>
      <Card.Title>{t('general.summary')}</Card.Title>
    </Card.Header>
    <Card.Body>
      <Mutation mutation={UPDATE_INVOICE}> 
        {(updateInvoice, { data }) => (
          <Formik
              initialValues={{ 
                summary: initialData.financeInvoice.summary, 
              }}
              // validationSchema={INVOICE_GROUP_SCHEMA}
              onSubmit={(values, { setSubmitting }) => {
                  console.log('submit values:')
                  console.log(values)

                  updateInvoice({ variables: {
                    input: {
                      id: match.params.id,
                      summary: values.name, 
                    }
                  }, refetchQueries: [
                      // {query: GET_INVOICE_GROUPS_QUERY, variables: {"archived": false }}
                  ]})
                  .then(({ data }) => {
                      console.log('got data', data)
                      toast.success((t('finance.invoice.toast_edit_summary_success')), {
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
              {({ isSubmitting, errors, values, setFieldValue, setFieldTouched }) => (
                <FinanceInvoiceEditSummaryForm
                  data={initialData}
                  isSubmitting={isSubmitting}
                  errors={errors}
                  values={values}
                  setFieldTouched={setFieldTouched}
                  setFieldTouched={setFieldValue}
                />
              )}
          </Formik>
        )}
      </Mutation>
    </Card.Body>
  </Card>
)

export default withTranslation()(withRouter(FinanceInvoiceEditSummary))