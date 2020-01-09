// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


// import { GET_INVOICE_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { GET_INVOICE_QUERY } from "../queries"

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
// import ScheduleClassPriceBack from "./ScheduleClassPriceBack"
import FinanceInvoiceEditBalance from "../edit/FinanceInvoiceEditBalance"


function FinanceInvoicePaymentBase({ t, history, match, children, form_type="create" }) {
  const invoiceId = match.params.invoice_id
  const return_url = "/finance/invoices/edit/" + invoiceId
  const { loading: queryLoading, error: queryError, data, } = useQuery(GET_INVOICE_QUERY, {
    variables: {
      id: invoiceId
    }
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
  const invoice_number = inputData.financeInvoice.invoiceNumber

  let title
  if ( form_type == "create" ) {
    title = t('finance.invoice.payments.add')
  } else {
    title = t('finance.invoice.payments.edit')
  }

  title = title + " #" + invoice_number

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={ title }>
            <div className="page-options d-flex">
              {/* Back */}
              <Link to={return_url} 
                    className='btn btn-secondary mr-2'>
                  <Icon prefix="fe" name="arrow-left" /> {t('general.back')} 
              </Link>
            </div>
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={8}>
              {/* Form can go here */}
              {children} 
            </Grid.Col>
            <Grid.Col md={4}>
            <Card statusColor="blue">
              <Card.Header>
                <Card.Title>{t('general.info')}</Card.Title>
              </Card.Header>
              <Card.Body padding={0}>
                <h4> #{ invoice_number } </h4>
                { inputData.financeInvoice.account.fullName } <br />
                { inputData.financeInvoice.summary }
              </Card.Body>
            </Card>
            <FinanceInvoiceEditBalance financeInvoice={inputData.financeInvoice} />
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(FinanceInvoicePaymentBase))