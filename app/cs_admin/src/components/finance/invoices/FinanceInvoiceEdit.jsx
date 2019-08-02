// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_INVOICES_QUERY, GET_INVOICE_QUERY } from './queries'
import { COSTCENTER_SCHEMA } from './yupSchema'



import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import FinanceMenu from "../FinanceMenu"


const UPDATE_COSTCENTER = gql`
  mutation UpdateFinanceCostCenter($input: UpdateFinanceCostCenterInput!) {
    updateFinanceCostcenter(input: $input) {
      financeCostcenter {
        id
        name
        code
      }
    }
  }
`


class FinanceInvoiceEdit extends Component {
  constructor(props) {
    super(props)
    console.log("finance invoice edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/finance/invoices"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Query query={GET_INVOICE_QUERY} variables={{ id }} >
            {({ loading, error, data, refetch }) => {
              // Loading
              if (loading) return <p>{t('general.loading_with_dots')}</p>
              // Error
              if (error) {
                console.log(error)
              return <p>{t('general.error_sad_smiley')}</p>
              }
              
              console.log('query data')
              console.log(data)

              return (
                <Container>
                  <Page.Header title={t('finance.invoice.title') + ' #' + data.financeInvoice.invoiceNumber}>
                    <div className="page-options d-flex">
                      <Link to={return_url} 
                            className='btn btn-link'>
                          <Icon prefix="fe" name="arrow-left" /> {t('general.back')} 
                      </Link>
                    </div>
                  </Page.Header>
                  <Grid.Row>
                    <Grid.Col md={9}>
                      invoice content here

{/*                             
                            <Mutation mutation={UPDATE_COSTCENTER} onCompleted={() => history.push(return_url)}> 
                            {(updateGlaccount, { data }) => (
                                <Formik
                                    initialValues={{ 
                                      name: initialData.name, 
                                      code: initialData.code
                                    }}
                                    validationSchema={COSTCENTER_SCHEMA}
                                    onSubmit={(values, { setSubmitting }) => {
                                        console.log('submit values:')
                                        console.log(values)

                                        updateGlaccount({ variables: {
                                          input: {
                                            id: match.params.id,
                                            name: values.name,
                                            code: values.code
                                          }
                                        }, refetchQueries: [
                                            {query: GET_COSTCENTERS_QUERY, variables: {"archived": false }}
                                        ]})
                                        .then(({ data }) => {
                                            console.log('got data', data)
                                            toast.success((t('finance.costcenters.toast_edit_success')), {
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
                                        <FoForm>
                                            <Card.Body>
                                              <Form.Group label={t('general.name')}>
                                                <Field type="text" 
                                                        name="name" 
                                                        className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                                        autoComplete="off" />
                                                <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                              </Form.Group>
                                              <Form.Group label={t('finance.code')}>
                                                <Field type="text" 
                                                        name="code" 
                                                        className={(errors.code) ? "form-control is-invalid" : "form-control"} 
                                                        autoComplete="off" />
                                                <ErrorMessage name="code" component="span" className="invalid-feedback" />
                                              </Form.Group>
                                            </Card.Body>
                                            <Card.Footer>
                                                <Button 
                                                  className="pull-right"
                                                  color="primary"
                                                  disabled={isSubmitting}
                                                  type="submit"
                                                >
                                                  {t('general.submit')}
                                                </Button>
                                                <Button
                                                  type="button" 
                                                  color="link" 
                                                  onClick={() => history.push(return_url)}
                                                >
                                                    {t('general.cancel')}
                                                </Button>
                                            </Card.Footer>
                                        </FoForm>
                                    )}
                                </Formik>
                            )}
                            </Mutation> */}
                    </Grid.Col>
                    <Grid.Col md={3}>
                      <Card>
                        <Card.Body>
                          <div>
                            <span className="pull-left bold">
                              {t('general.subtotal')}
                            </span>
                            <span className="pull-right">
                              {data.financeInvoice.subtotalDisplay}
                            </span>
                          </div>
                        </Card.Body>
                      </Card>
                      sidebar here
                    </Grid.Col>
                  </Grid.Row>
                </Container>
          )}}
        </Query>
      </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(FinanceInvoiceEdit))