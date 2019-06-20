// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_PAYMENT_METHODS_QUERY } from './queries'
import { PAYMENT_METHOD_SCHEMA } from './yupSchema'


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
import FinancePaymentMethodForm from './FinancePaymentMethodForm'

const ADD_PAYMENT_METHOD = gql`
  mutation CreateFinancePaymentMethod($input:CreateFinancePaymentMethodInput!) {
    createFinancePaymentMethod(input: $input) {
      financePaymentMethod{
        id
        archived
        name
        code
      }
    }
  }
`

const return_url = "/finance/paymentmethods"

const FinancePaymentMethodAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('finance.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('finance.payment_methods.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_PAYMENT_METHOD} onCompleted={() => history.push(return_url)}> 
                {(addLocation, { data }) => (
                    <Formik
                        initialValues={{ name: '', code: '' }}
                        validationSchema={PAYMENT_METHOD_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addLocation({ variables: {
                              input: {
                                name: values.name, 
                                code: values.code
                              }
                            }, refetchQueries: [
                                {query: GET_PAYMENT_METHODS_QUERY, variables: {"archived": false }}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('finance.payment_methods.toast_add_success')), {
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
                            <FinancePaymentMethodForm
                              isSubmitting={isSubmitting}
                              errors={errors}
                              return_url={return_url}
                            />
                            // <FoForm>
                            //     <Card.Body>
                            //         <Form.Group label={t('general.name')}>
                            //           <Field type="text" 
                            //                   name="name" 
                            //                   className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                            //                   autoComplete="off" />
                            //           <ErrorMessage name="name" component="span" className="invalid-feedback" />
                            //         </Form.Group>
                            //         <Form.Group label={t('finance.code')}>
                            //           <Field type="text" 
                            //                   name="code" 
                            //                   className={(errors.code) ? "form-control is-invalid" : "form-control"} 
                            //                   autoComplete="off" />
                            //           <ErrorMessage name="code" component="span" className="invalid-feedback" />
                            //         </Form.Group>
                            //     </Card.Body>
                            //     <Card.Footer>
                            //         <Button 
                            //           color="primary"
                            //           className="pull-right" 
                            //           type="submit" 
                            //           disabled={isSubmitting}
                            //         >
                            //           {t('general.submit')}
                            //         </Button>
                            //         <Button color="link" onClick={() => history.push(return_url)}>
                            //             {t('general.cancel')}
                            //         </Button>
                            //     </Card.Footer>
                            // </FoForm>
                        )}
                    </Formik>
                )}
                </Mutation>
          </Card>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="financepaymentmethod">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
              </Button>
            </HasPermissionWrapper>
            <FinanceMenu active_link='payment_methods'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
)

export default withTranslation()(withRouter(FinancePaymentMethodAdd))