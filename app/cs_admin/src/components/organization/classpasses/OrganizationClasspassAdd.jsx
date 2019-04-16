// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'
import { v4 } from "uuid"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../plugin_config/tinymce"

import { GET_CLASSPASSES_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { CLASSPASS_SCHEMA } from './yupSchema'


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

import OrganizationMenu from "../OrganizationMenu"


const CREATE_CLASSPASS = gql`
  mutation CreateClasspass($input: CreateOrganizationClasspassInput!) {
    createOrganizationClasspass(input: $input) {
      organizationClasspass {
        id
        displayPublic
        displayShop
        name
        description
        price
        financeTaxRate {
          id
          name
        }
        validity
        validityUnit
        classes
        unlimited
        organizationMembership {
          id
          name
        }
        quickStatsAmount
        financeGlaccount {
          id
          name
        }
        financeCostcenter {
          id
          name
        }
      }
    }
  }
`


class OrganizationClasspassAdd extends Component {
  constructor(props) {
    super(props)
    console.log("Organization classpass add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/organization/classpasses"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.classpasses.title_add')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_INPUT_VALUES_QUERY} variables={{ id, archived: false }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('error_sad_smiley')}</p>
                    }
                    
                    console.log('query data')
                    console.log(data)
                    const inputData = data

                    return (
                      
                      <Mutation mutation={CREATE_CLASSPASS} onCompleted={() => history.push(return_url)}> 
                      {(createMembership, { data }) => (
                          <Formik
                              initialValues={{ 
                                displayPublic: true,
                                displayShop: true,
                                name: "",
                                description: "",
                                price: 0,
                                financeTaxRate: "",
                                validity: 1,
                                validityUnit: "MONTHS",
                                classes: 1,
                                unlimited: false,
                                organizationMembership: "",
                                quickStatsAmount: 0,
                                financeGlaccount: "",
                                financeCostcenter: ""
                              }}
                              validationSchema={CLASSPASS_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  createMembership({ variables: {
                                    input: {
                                      displayPublic: values.displayPublic,
                                      displayShop: values.displayShop,
                                      name: values.name,
                                      description: values.description,
                                      price: values.price,
                                      financeTaxRate: values.financeTaxRate,
                                      validity: values.validity,
                                      validityUnit: values.validityUnit,
                                      classes: values.classes,
                                      unlimited: values.unlimited,
                                      organizationMembership: values.organizationMembership,
                                      quickStatsAmount: values.quickStatsAmount,
                                      financeGlaccount: values.financeGlaccount,
                                      financeCostcenter: values.financeCostcenter
                                    }
                                  }, refetchQueries: [
                                      {query: GET_CLASSPASSES_QUERY, variables: {"archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.classpasses.toast_add_success')), {
                                          position: toast.POSITION.BOTTOM_RIGHT
                                        })
                                    }).catch((error) => {
                                      toast.error((t('toast_server_error')) + ': ' +  error, {
                                          position: toast.POSITION.BOTTOM_RIGHT
                                        })
                                      console.log('there was an error sending the query', error)
                                      setSubmitting(false)
                                    })
                              }}
                              >
                              {({ isSubmitting, setFieldValue, setFieldTouched, errors, values }) => (
                                  <FoForm>
                                      <Card.Body> 
                                        <Form.Group>
                                          <Form.Label className="custom-switch">
                                              <Field 
                                                className="custom-switch-input"
                                                type="checkbox" 
                                                name="displayPublic" 
                                                checked={values.displayPublic} />
                                              <span className="custom-switch-indicator" ></span>
                                              <span className="custom-switch-description">{t('organization.classpass.public')}</span>
                                            </Form.Label>
                                          <ErrorMessage name="displayPublic" component="div" />   
                                        </Form.Group>      
                                        <Form.Group>
                                          <Form.Label className="custom-switch">
                                              <Field 
                                                className="custom-switch-input"
                                                type="checkbox" 
                                                name="displayShop" 
                                                checked={values.displayShop} />
                                              <span className="custom-switch-indicator" ></span>
                                              <span className="custom-switch-description">{t('organization.classpass.shop')}</span>
                                            </Form.Label>
                                          <ErrorMessage name="displayShop" component="div" />   
                                        </Form.Group>      
                                        <Form.Group label={t('organization.classpass.name')} >
                                          <Field type="text" 
                                                name="name" 
                                                className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                                autoComplete="off" />
                                          <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                        </Form.Group>
                                        <Form.Group label={t('description')}>
                                          <Editor
                                              textareaName="description"
                                              initialValue={values.description}
                                              init={tinymceBasicConf}
                                              onChange={(e) => setFieldValue("description", e.target.getContent())}
                                              onBlur={() => setFieldTouched("description", true)}
                                            />
                                          <ErrorMessage name="description" component="span" className="invalid-feedback" />
                                        </Form.Group>
                                        <Form.Group label={t('organization.classpass.price')}>
                                          <Field type="text" 
                                                name="price" 
                                                className={(errors.price) ? "form-control is-invalid" : "form-control"} 
                                                autoComplete="off" />
                                          <ErrorMessage name="price" component="span" className="invalid-feedback" />
                                        </Form.Group>
                                        <Form.Group label={t('organization.classpass.taxrate')}>
                                          <Field component="select" 
                                                 name="financeTaxRate" 
                                                 className={(errors.financeTaxRate) ? "form-control is-invalid" : "form-control"} 
                                                 autoComplete="off">
                                            {console.log("query data in classpass add:")}
                                            {console.log(inputData)}
                                            <option value="" key={v4()}></option>
                                            {inputData.financeTaxrates.edges.map(({ node }) =>
                                              <option value={node.id} key={v4()}>{node.name} ({node.percentage}% {node.rateType})</option>
                                            )}
                                          </Field>
                                          <ErrorMessage name="financeTaxRate" component="span" className="invalid-feedback" />
                                        </Form.Group>
                                        <Form.Group label={t('organization.classpass.validity')}>
                                          <Field type="text" 
                                                name="validity" 
                                                className={(errors.validity) ? "form-control is-invalid" : "form-control"} 
                                                autoComplete="off" />
                                          <ErrorMessage name="validity" component="span" className="invalid-feedback" />
                                        </Form.Group>
                                        <Form.Group label={t('organization.classpass.validity_unit')}>
                                          <Field component="select" 
                                                 name="validityUnit" 
                                                 className={(errors.validityUnit) ? "form-control is-invalid" : "form-control"} 
                                                 autoComplete="off">
                                            <option value="DAYS" key={v4()}>{t('validity.days')}</option>
                                            <option value="WEEKS" key={v4()}>{t('validity.weeks')}</option>
                                            <option value="MONTHS" key={v4()}>{t('validity.months')}</option>
                                          </Field>
                                          <ErrorMessage name="validityUnit" component="span" className="invalid-feedback" />
                                        </Form.Group>
                                        <Form.Group>
                                          <Form.Label className="custom-switch">
                                              <Field 
                                                className="custom-switch-input"
                                                type="checkbox" 
                                                name="unlimited" 
                                                checked={values.unlimied} />
                                              <span className="custom-switch-indicator" ></span>
                                              <span className="custom-switch-description">{t('organization.classpass.unlimited')}</span>
                                            </Form.Label>
                                          <ErrorMessage name="unlimited" component="div" />   
                                        </Form.Group>  
                                        { (values.unlimited) ? "" :
                                        <Form.Group label={t('organization.classpass.classes')}>
                                          <Field type="text" 
                                                 name="classes" 
                                                 className={(errors.classes) ? "form-control is-invalid" : "form-control"} 
                                                 autoComplete="off" />
                                          <ErrorMessage name="classes" component="span" className="invalid-feedback" />
                                        </Form.Group> } 
                                        <Form.Group label={t('organization.classpass.membership')}>
                                          <Field component="select" 
                                                 name="organizationMembership" 
                                                 className={(errors.organizationMembership) ? "form-control is-invalid" : "form-control"} 
                                                 autoComplete="off">
                                            <option value="" key={v4()}>{t("general.membership_not_required")}</option>
                                            {inputData.organizationMemberships.edges.map(({ node }) =>
                                              <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                                            )}
                                          </Field>
                                          <ErrorMessage name="organizationMembership" component="span" className="invalid-feedback" />
                                        </Form.Group> 
                                        { (values.unlimited) ? 
                                          <Form.Group label={t('organization.classpass.quickStatsAmount')}>
                                            <Field type="text" 
                                                  name="quickStatsAmount" 
                                                  className={(errors.quickStatsAmount) ? "form-control is-invalid" : "form-control"} 
                                                  autoComplete="off" />
                                            <ErrorMessage name="quickStatsAmount" component="span" className="invalid-feedback" />
                                          </Form.Group>
                                          : ""
                                        }
                                        <Form.Group label={t('organization.classpass.glaccount')}>
                                          <Field component="select" 
                                                 name="financeGlaccount" 
                                                 className={(errors.financeGlaccount) ? "form-control is-invalid" : "form-control"} 
                                                 autoComplete="off">
                                            <option value="" key={v4()}></option>
                                            {inputData.financeGlaccounts.edges.map(({ node }) =>
                                              <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                                            )}
                                          </Field>
                                          <ErrorMessage name="financeGlaccount" component="span" className="invalid-feedback" />
                                        </Form.Group>
                                        <Form.Group label={t('organization.classpass.costcenter')}>
                                          <Field component="select" 
                                                 name="financeCostcenter" 
                                                 className={(errors.financeCostcenter) ? "form-control is-invalid" : "form-control"} 
                                                 autoComplete="off">
                                            <option value="" key={v4()}></option>
                                            {inputData.financeCostcenters.edges.map(({ node }) =>
                                              <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                                            )}
                                          </Field>
                                          <ErrorMessage name="financeCostcenter" component="span" className="invalid-feedback" />
                                        </Form.Group>
                                      </Card.Body>
                                      <Card.Footer>
                                          <Button 
                                            className="pull-right"
                                            color="primary"
                                            disabled={isSubmitting}
                                            type="submit"
                                          >
                                            {t('submit')}
                                          </Button>
                                          <Button
                                            type="button" 
                                            color="link" 
                                            onClick={() => history.push(return_url)}
                                          >
                                              {t('cancel')}
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
                <HasPermissionWrapper permission="add"
                                      resource="organizationclasspass">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('back')}
                  </Button>
                </HasPermissionWrapper>
                <OrganizationMenu active_link='organizationclasspasses'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationClasspassAdd))