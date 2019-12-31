// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_SCHEDULE_ITEM_PRICES_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { FINANCE_INVOICE_PAYMENT_SCHEMA } from './yupSchema'
// import ScheduleClassPriceForm from './ScheduleClassPriceForm'
// import { dateToLocalISO } from '../../../../../tools/date_tools'

import SiteWrapper from "../../../SiteWrapper"

import FinanceInvoicePaymentBase from "./FinanceInvoicePaymentBase"


const ADD_FINANCE_INVOICE_PAYMENT = gql`
  mutation CreateFinanceInvoicePayment($input:CreateFinanceInvoicePaymentInput!) {
    createFinanceInvoicePayment(input:$input) {
      financeInvoicePayment {
        id
      } 
    }
  }
`


function FinanceInvoicePaymentAdd({ t, history, match }) {
  const invoiceId = match.params.class_id
  const return_url = "/finance/invoice/edit/" + invoiceId
  const { loading: queryLoading, error: queryError, data, } = useQuery(GET_INPUT_VALUES_QUERY)
  const [addInvoicePayment, { mutationData, mutationLoading, mutationError, onCompleted }] = useMutation(ADD_FINANCE_INVOICE_PAYMENT, {
    onCompleted: () => history.push(return_url),
  })

  if (queryLoading) return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <p>{t('general.loading_with_dots')}</p>
      </div>
    </SiteWrapper>
  )
  // Error
  if (queryError) {
    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          { console.log(queryError) }
          <p>{t('general.error_sad_smiley')}</p>
        </div>
      </SiteWrapper>
    )
  }

  console.log('query data')
  console.log(data)
  const inputData = data


  return (
    <FinanceInvoicePaymentBase form_type={"create"}>
      form here...
    </FinanceInvoicePaymentBase>
        //   <Formik
        //     initialValues={{ 
        //       dateStart: new Date() ,
        //       organizationClasspassDropin: "",
        //       organizationClasspassTrial: "",
        //     }}
        //     // validationSchema={SCHEDULE_CLASS_TEACHER_SCHEMA}
        //     onSubmit={(values, { setSubmitting }) => {

        //         let dateEnd
        //         if (values.dateEnd) {
        //           dateEnd = dateToLocalISO(values.dateEnd)
        //         } else {
        //           dateEnd = values.dateEnd
        //         }

        //         addScheduleClassPrice({ variables: {
        //           input: {
        //             scheduleItem: match.params.class_id,
        //             dateStart: dateToLocalISO(values.dateStart),
        //             dateEnd: dateEnd,
        //             organizationClasspassDropin: values.organizationClasspassDropin,
        //             organizationClasspassTrial: values.organizationClasspassTrial
        //           }
        //         }, refetchQueries: [
        //             {query: GET_SCHEDULE_ITEM_PRICES_QUERY, variables: { scheduleItem: match.params.class_id }},
        //             // {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }},
        //         ]})
        //         .then(({ data }) => {
        //             console.log('got data', data);
        //             toast.success((t('schedule.classes.prices.toast_add_success')), {
        //                 position: toast.POSITION.BOTTOM_RIGHT
        //               })
        //           }).catch((error) => {
        //             toast.error((t('general.toast_server_error')) + ': ' +  error, {
        //                 position: toast.POSITION.BOTTOM_RIGHT
        //               })
        //             console.log('there was an error sending the query', error)
        //             setSubmitting(false)
        //           })
        //     }}
        //     >
        //     {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
        //       <ScheduleClassPriceForm
        //         inputData={inputData}
        //         isSubmitting={isSubmitting}
        //         setFieldTouched={setFieldTouched}
        //         setFieldValue={setFieldValue}
        //         errors={errors}
        //         values={values}
        //         return_url={return_url + match.params.class_id}
        //       />
        //     )}
        // </Formik>
  )
}


export default withTranslation()(withRouter(FinanceInvoicePaymentAdd))