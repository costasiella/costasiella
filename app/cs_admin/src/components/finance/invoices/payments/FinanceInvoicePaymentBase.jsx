// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


// import { GET_INVOICE_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { GET_INVOICE_QUERY } from "../queries"

import SiteWrapper from "../../../../SiteWrapper"
// import ScheduleClassPriceBack from "./ScheduleClassPriceBack"


function FinanceInvoicePaymentBase({ t, history, match, form_type="create" }) {
  const invoiceId = match.params.invoice_id
  const return_url = "/finance/invoices/edit/" + invoiceId
  const { loading: queryLoading, error: queryError, data, } = useQuery(GET_INVOICE_QUERY)
  const [addInvoicePayment, { mutationData, mutationLoading, mutationError, onCompleted }] = useMutation(ADD_INVOICE_PAYMENT, {
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
          { console.log(error) }
          <p>{t('general.error_sad_smiley')}</p>
        </div>
      </SiteWrapper>
    )
  }

  console.log('query data')
  console.log(data)
  const inputData = data
  const invoice_number = inputData.financeInvoice.invoiceNumber

  let title
  if ( form_type == "create" ) {
    title = t('finance.invoice.payment.add')
  } else {
    title = t('finance.invoice.payment.edit')
  }

  title = title + " #" + invoice_number

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={ title }>
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={6}>
              {/* Form can go here */}
              {children} 
            </Grid.Col>
            <Grid.Col md={6}>
              invoice data here...
            </Grid.Col>
          </Grid.Row>
        </Container>
        {/* <ClassEditBase 
          card_title={t('schedule.classes.prices.title_add')}
          menu_active_link="prices"
          sidebar_button={<ScheduleClassPriceBack classId={match.params.class_id} />}
        >
          <Formik
            initialValues={{ 
              dateStart: new Date() ,
              organizationClasspassDropin: "",
              organizationClasspassTrial: "",
            }}
            // validationSchema={SCHEDULE_CLASS_TEACHER_SCHEMA}
            onSubmit={(values, { setSubmitting }) => {

                let dateEnd
                if (values.dateEnd) {
                  dateEnd = dateToLocalISO(values.dateEnd)
                } else {
                  dateEnd = values.dateEnd
                }

                addScheduleClassPrice({ variables: {
                  input: {
                    scheduleItem: match.params.class_id,
                    dateStart: dateToLocalISO(values.dateStart),
                    dateEnd: dateEnd,
                    organizationClasspassDropin: values.organizationClasspassDropin,
                    organizationClasspassTrial: values.organizationClasspassTrial
                  }
                }, refetchQueries: [
                    {query: GET_SCHEDULE_ITEM_PRICES_QUERY, variables: { scheduleItem: match.params.class_id }},
                    // {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }},
                ]})
                .then(({ data }) => {
                    console.log('got data', data);
                    toast.success((t('schedule.classes.prices.toast_add_success')), {
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
            {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
              <ScheduleClassPriceForm
                inputData={inputData}
                isSubmitting={isSubmitting}
                setFieldTouched={setFieldTouched}
                setFieldValue={setFieldValue}
                errors={errors}
                values={values}
                return_url={return_url + match.params.class_id}
              />
            )}
        </Formik>
        </ClassEditBase> */}
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(FinanceInvoicePaymentBase))