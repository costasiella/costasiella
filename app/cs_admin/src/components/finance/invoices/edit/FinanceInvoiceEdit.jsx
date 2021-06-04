// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'
import { toast } from 'react-toastify'

import { GET_INVOICES_QUERY, GET_INVOICE_QUERY, CANCEL_AND_CREATE_CREDIT_INVOICE } from '../queries'
import { TOKEN_REFRESH } from "../../../../queries/system/auth"
import { refreshTokenAndOpenExportLinkInNewTab } from "../../../../tools/refresh_token_and_open_export_link"

import {
  Dropdown,
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import FinanceMenu from "../../FinanceMenu"

import CSLS from "../../../../tools/cs_local_storage"

import FinanceInvoiceEditBase from "./FinanceInvoiceEditBase"
import FinanceInvoiceEditItems from "./FinanceInvoiceEditItems"
import FinanceInvoiceEditAdditional from "./FinanceInvoiceEditAdditional"
import FinanceInvoiceEditBalance from "./FinanceInvoiceEditBalance"
import FinanceInvoiceEditOptions from "./FinanceInvoiceEditOptions"
import FinanceInvoiceEditOrganization from "./FinanceInvoiceEditOrganization"
import FinanceInvoiceEditSummary from "./FinanceInvoiceEditSummary"
import FinanceInvoiceEditTo from "./FinanceInvoiceEditTo"


function FinanceInvoiceEdit({t, match, history}) {
  const id = match.params.id
  const { loading, error, data, refetch } = useQuery(GET_INVOICE_QUERY, {
    variables: {
      id: id
    }
  })

  const [doTokenRefresh] = useMutation(TOKEN_REFRESH)
  const [cancelAndCreateCreditInvoice] = useMutation(CANCEL_AND_CREATE_CREDIT_INVOICE)
  
  // Loading
  if (loading) return <FinanceInvoiceEditBase>{t('general.loading_with_dots')}</FinanceInvoiceEditBase>
  // Error
  if (error) {
    console.log(error)
    return <FinanceInvoiceEditBase>{t('general.error_sad_smiley')}</FinanceInvoiceEditBase>
  }

  console.log(data)
  // Fetch back location from localStorage, if no value set, default back to /finance/invoices
  let return_url = localStorage.getItem(CSLS.FINANCE_INVOICES_EDIT_RETURN)
  if (!return_url) {
    return_url = "/finance/invoices"
  }
  const export_url = "/d/export/invoice/pdf/" + id
  const payment_add_url = "/finance/invoices/" + id + "/payment/add"

  return (
    <FinanceInvoiceEditBase>
      <Page.Header title={t('finance.invoice.title') + ' #' + data.financeInvoice.invoiceNumber}>
        <div className="page-options d-flex">
          {/* Back */}
          <Link to={return_url} 
                className='btn btn-secondary mr-2'>
              <Icon prefix="fe" name="arrow-left" /> {t('general.back')} 
          </Link>
          {/* Add payment */}
          <Link to={payment_add_url} 
              className='btn btn-secondary mr-2'>
              <Icon prefix="fe" name="dollar-sign" /> {t('finance.invoice.payments.add')} 
          </Link>
          {/* Export as PDF */}
          <Button
            color="secondary"
            icon="printer"
            className="mr-2"
            onClick={() => refreshTokenAndOpenExportLinkInNewTab(
              doTokenRefresh, history, export_url
            )}
          >
            {t('general.pdf')} 
          </Button>
          {/* Tools */}
          <Dropdown
            className=""
            type="button"
            toggle
            icon="tool"
            color="secondary"
            triggerContent={t("general.tools")}
            items={[
              <HasPermissionWrapper permission="change" resource="financeinvoice">
                <Dropdown.Item
                  key={v4()}
                  icon="slash"
                  onClick={() => {
                    cancelAndCreateCreditInvoice({ variables: {
                      input: {
                        id: id,
                      }
                    }, refetchQueries: []
                    })
                    .then(({ data }) => {
                        console.log('got data', data)
                        const creditInvoiceId = data.cancelAndCreateCreditFinanceInvoice.financeInvoice.id
                        history.push(`/finance/invoices/edit/${creditInvoiceId}`)
                        toast.success((t('finance.invoice.now_editing_credit_invoice')), {
                            position: toast.POSITION.BOTTOM_RIGHT
                          })
                      }).catch((error) => {
                        toast.error((t('general.toast_server_error')) + ': ' +  error, {
                            position: toast.POSITION.BOTTOM_RIGHT
                          })
                        console.log('there was an error sending the query', error)
                      })
                  }}>
                    {t('finance.invoice.cancel_and_create_credit_invoice')}
                </Dropdown.Item>
              </HasPermissionWrapper>
            ]}>
          </Dropdown>
        </div>
      </Page.Header>
      <Grid.Row>
        <Grid.Col md={9}>
          <FinanceInvoiceEditSummary 
            initialData={data}
          />
          <Grid.Row>
            <Grid.Col md={6} ml={0}>
              <FinanceInvoiceEditOrganization organization={data.organization} />
            </Grid.Col>
            <Grid.Col md={6} ml={0}>
              <FinanceInvoiceEditTo initialData={data} />
            </Grid.Col>
          </Grid.Row>
        </Grid.Col>
        <Grid.Col md={3}>
          <FinanceInvoiceEditBalance financeInvoice={data.financeInvoice} />
          <FinanceInvoiceEditOptions
            initialData={data}
          />
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        <Grid.Col md={12}>
          <FinanceInvoiceEditItems inputData={data} refetchInvoice={refetch} />
          <FinanceInvoiceEditAdditional initialData={data} />
        </Grid.Col>
      </Grid.Row>
    </FinanceInvoiceEditBase>
  )

}


// class FinanceInvoiceEdit extends Component {
//   constructor(props) {
//     super(props)
//     console.log("finance invoice edit props:")
//     console.log(props)
//   }

//   render() {
//     const t = this.props.t
//     const match = this.props.match
//     const history = this.props.history
//     const id = match.params.id
//     // Fetch back location from localStorage, if no value set, default back to /finance/invoices
//     let return_url = localStorage.getItem(CSLS.FINANCE_INVOICES_EDIT_RETURN)
//     if (!return_url) {
//       return_url = "/finance/invoices"
//     }

//     const export_url = "/d/export/invoice/pdf/" + id
//     const payment_add_url = "/finance/invoices/" + id + "/payment/add"

//     return (
//       <SiteWrapper>
//         <div className="my-3 my-md-5">
//           <Query query={GET_INVOICE_QUERY} variables={{ id }} >
//             {({ loading, error, data, refetch }) => {
//               // Loading
//               if (loading) return <FinanceInvoiceEditBase>{t('general.loading_with_dots')}</FinanceInvoiceEditBase>
//               // Error
//               if (error) {
//                 console.log(error)
//                 return <p>{t('general.error_sad_smiley')}</p>
//               }
              
//               console.log('query data')
//               console.log(data)

//               return (
//                 <Container>
                  

// {/*                             
//                             <Mutation mutation={UPDATE_COSTCENTER} onCompleted={() => history.push(return_url)}> 
//                             {(updateGlaccount, { data }) => (
//                                 <Formik
//                                     initialValues={{ 
//                                       name: initialData.name, 
//                                       code: initialData.code
//                                     }}
//                                     validationSchema={COSTCENTER_SCHEMA}
//                                     onSubmit={(values, { setSubmitting }) => {
//                                         console.log('submit values:')
//                                         console.log(values)

//                                         updateGlaccount({ variables: {
//                                           input: {
//                                             id: match.params.id,
//                                             name: values.name,
//                                             code: values.code
//                                           }
//                                         }, refetchQueries: [
//                                             {query: GET_COSTCENTERS_QUERY, variables: {"archived": false }}
//                                         ]})
//                                         .then(({ data }) => {
//                                             console.log('got data', data)
//                                             toast.success((t('finance.costcenters.toast_edit_success')), {
//                                                 position: toast.POSITION.BOTTOM_RIGHT
//                                               })
//                                           }).catch((error) => {
//                                             toast.error((t('general.toast_server_error')) + ': ' +  error, {
//                                                 position: toast.POSITION.BOTTOM_RIGHT
//                                               })
//                                             console.log('there was an error sending the query', error)
//                                             setSubmitting(false)
//                                           })
//                                     }}
//                                     >
//                                     {({ isSubmitting, errors, values }) => (
//                                         <FoForm>
//                                             <Card.Body>
//                                               <Form.Group label={t('general.name')}>
//                                                 <Field type="text" 
//                                                         name="name" 
//                                                         className={(errors.name) ? "form-control is-invalid" : "form-control"} 
//                                                         autoComplete="off" />
//                                                 <ErrorMessage name="name" component="span" className="invalid-feedback" />
//                                               </Form.Group>
//                                               <Form.Group label={t('finance.code')}>
//                                                 <Field type="text" 
//                                                         name="code" 
//                                                         className={(errors.code) ? "form-control is-invalid" : "form-control"} 
//                                                         autoComplete="off" />
//                                                 <ErrorMessage name="code" component="span" className="invalid-feedback" />
//                                               </Form.Group>
//                                             </Card.Body>
//                                             <Card.Footer>
//                                                 <Button 
//                                                   className="pull-right"
//                                                   color="primary"
//                                                   disabled={isSubmitting}
//                                                   type="submit"
//                                                 >
//                                                   {t('general.submit')}
//                                                 </Button>
//                                                 <Button
//                                                   type="button" 
//                                                   color="link" 
//                                                   onClick={() => history.push(return_url)}
//                                                 >
//                                                     {t('general.cancel')}
//                                                 </Button>
//                                             </Card.Footer>
//                                         </FoForm>
//                                     )}
//                                 </Formik>
//                             )}
//                             </Mutation> */}

//                 </Container>
//           )}}
//         </Query>
//       </div>
//     </SiteWrapper>
//     )}
//   }


export default withTranslation()(withRouter(FinanceInvoiceEdit))