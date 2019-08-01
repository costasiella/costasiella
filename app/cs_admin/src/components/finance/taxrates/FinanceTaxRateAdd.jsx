// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'


import { GET_TAXRATES_QUERY } from './queries'
import { TAX_RATE_SCHEMA } from './yupSchema'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import FinanceMenu from '../FinanceMenu'


const ADD_TAXRATE = gql`
  mutation CreateFinanceTaxRate($input:CreateFinanceTaxRateInput!) {
    createFinanceTaxRate(input: $input) {
      financeTaxRate{
        id
        archived
        name
        percentage
        rateType
        code
      }
    }
  }
`

const return_url = "/finance/taxrates"

const FinanceTaxRateAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('finance.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('finance.taxrates.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_TAXRATE} onCompleted={() => history.push(return_url)}> 
                {(addLocation, { data }) => (
                    <Formik
                        initialValues={{ name: "", percentage: "", rateType: "IN", code: "" }}
                        validationSchema={TAX_RATE_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addLocation({ variables: {
                              input: {
                                name: values.name,
                                percentage: values.percentage,
                                rateType: values.rateType, 
                                code: values.code,
                              }
                            }, refetchQueries: [
                                {query: GET_TAXRATES_QUERY, variables: {"archived": false }}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('finance.taxrates.toast_add_success')), {
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
                            <FoForm>
                                <Card.Body>
                                    <Form.Group label={t('general.name')}>
                                      <Field type="text" 
                                              name="name" 
                                              className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                              autoComplete="off" />
                                      <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                    </Form.Group>
                                    <Form.Group label={t('finance.taxrates.percentage')}>
                                      <Field type="text" 
                                             name="percentage" 
                                             className={(errors.percentage) ? "form-control is-invalid" : "form-control"} 
                                             autoComplete="off" />
                                      <ErrorMessage name="percentage" component="span" className="invalid-feedback" />
                                    </Form.Group>
                                    <Form.Group label={t('finance.taxrates.rateType')}>
                                      <Field component="select" 
                                             name="rateType" 
                                             className={(errors.rateType) ? "form-control is-invalid" : "form-control"} 
                                             autoComplete="off">
                                        <option value="IN">{t('finance.taxrates.including')}</option>
                                        <option value="EX">{t('finance.taxrates.excluding')}</option>
                                      </Field>
                                      <ErrorMessage name="rateType" component="span" className="invalid-feedback" />
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
                                      color="primary"
                                      className="pull-right" 
                                      type="submit" 
                                      disabled={isSubmitting}
                                    >
                                      {t('general.submit')}
                                    </Button>
                                    <Button color="link" onClick={() => history.push(return_url)}>
                                        {t('general.cancel')}
                                    </Button>
                                </Card.Footer>
                            </FoForm>
                        )}
                    </Formik>
                )}
                </Mutation>
          </Card>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="financetaxrate">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
              </Button>
            </HasPermissionWrapper>
            <FinanceMenu active_link='taxrates'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
)

export default withTranslation()(withRouter(FinanceTaxRateAdd))