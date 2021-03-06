// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_TAXRATES_QUERY, GET_TAXRATE_QUERY } from './queries'
import { TAX_RATE_SCHEMA } from './yupSchema'



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


const UPDATE_TAXRATE = gql`
  mutation UpdateFinanceTaxRate($input: UpdateFinanceTaxRateInput!) {
    updateFinanceTaxRate(input: $input) {
      financeTaxRate {
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


class FinanceTaxRateEdit extends Component {
  constructor(props) {
    super(props)
    console.log("finance taxrate edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/finance/taxrates"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t('finance.taxrates.title')} />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('finance.taxrates.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_TAXRATE_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                    return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.financeTaxRate;
                    console.log('query data')
                    console.log(data)

                    return (
                      
                      <Mutation mutation={UPDATE_TAXRATE} onCompleted={() => history.push(return_url)}> 
                      {(updateTaxrate, { data }) => (
                          <Formik
                              initialValues={{ 
                                name: initialData.name, 
                                percentage: initialData.percentage,
                                rateType: initialData.rateType,
                                code: initialData.code,
                              }}
                              validationSchema={TAX_RATE_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  updateTaxrate({ variables: {
                                    input: {
                                      id: match.params.id,
                                      name: values.name,
                                      percentage: values.percentage,
                                      rateType: values.rateType,
                                      code: values.code,
                                    }
                                  }, refetchQueries: [
                                      {query: GET_TAXRATES_QUERY, variables: {"archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('finance.taxrates.toast_edit_success')), {
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
                      </Mutation>
                      )}}
                </Query>
              </Card>
              </Grid.Col>
              <Grid.Col md={3}>
                <HasPermissionWrapper permission="change"
                                      resource="taxrate">
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
    )}
  }


export default withTranslation()(withRouter(FinanceTaxRateEdit))