// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_PAYMENT_METHODS_QUERY, GET_PAYMENT_METHOD_QUERY } from './queries'
import { PAYMENT_METHOD_SCHEMA } from './yupSchema'



import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import FinanceMenu from "../FinanceMenu"
import FinancePaymentMethodForm from './FinancePaymentMethodForm'


const UPDATE_PAYMENT_METHOD = gql`
  mutation UpdateFinancePaymentMethod($input: UpdateFinancePaymentMethodInput!) {
    updateFinancePaymentMethod(input: $input) {
      financePaymentMethod {
        id
        name
        code
      }
    }
  }
`


class FinancePaymentMethodEdit extends Component {
  constructor(props) {
    super(props)
    console.log("finance payment method edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/finance/paymentmethods"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t('finance.payment_methods.title')} />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('finance.payment_methods.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_PAYMENT_METHOD_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                    return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.financePaymentMethod;
                    console.log('query data')
                    console.log(data)

                    return (
                      
                      <Mutation mutation={UPDATE_PAYMENT_METHOD} onCompleted={() => history.push(return_url)}> 
                      {(updateGlaccount, { data }) => (
                          <Formik
                              initialValues={{ 
                                name: initialData.name, 
                                code: initialData.code
                              }}
                              validationSchema={PAYMENT_METHOD_SCHEMA}
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
                                      {query: GET_PAYMENT_METHODS_QUERY, variables: {"archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('finance.payment_methods.toast_edit_success')), {
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
                                  <FinancePaymentMethodForm
                                    isSubmitting={isSubmitting}
                                    errors={errors}
                                    values={values}
                                    return_url={return_url}
                                  />
                                  // <FoForm>
                                  //     <Card.Body>
                                  //       <Form.Group label={t('general.name')}>
                                  //         <Field type="text" 
                                  //                 name="name" 
                                  //                 className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                  //                 autoComplete="off" />
                                  //         <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                  //       </Form.Group>
                                  //       <Form.Group label={t('finance.code')}>
                                  //         <Field type="text" 
                                  //                 name="code" 
                                  //                 className={(errors.code) ? "form-control is-invalid" : "form-control"} 
                                  //                 autoComplete="off" />
                                  //         <ErrorMessage name="code" component="span" className="invalid-feedback" />
                                  //       </Form.Group>
                                  //     </Card.Body>
                                  //     <Card.Footer>
                                  //         <Button 
                                  //           className="pull-right"
                                  //           color="primary"
                                  //           disabled={isSubmitting}
                                  //           type="submit"
                                  //         >
                                  //           {t('general.submit')}
                                  //         </Button>
                                  //         <Button
                                  //           type="button" 
                                  //           color="link" 
                                  //           onClick={() => history.push(return_url)}
                                  //         >
                                  //             {t('general.cancel')}
                                  //         </Button>
                                  //     </Card.Footer>
                                  // </FoForm>
                              )}
                          </Formik>
                      )}
                      </Mutation>
                      )}}
                </Query>
              </Card>
              </Grid.Col>
              <Grid.Col md={3}>
                <HasPermissionWrapper permission="change"
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
    )}
  }


export default withTranslation()(withRouter(FinancePaymentMethodEdit))