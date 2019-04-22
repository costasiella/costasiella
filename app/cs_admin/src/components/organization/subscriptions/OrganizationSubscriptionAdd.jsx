// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_SUBSCRIPTIONS_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { SUBSCRIPTION_SCHEMA } from './yupSchema'
import OrganizationSubscriptionForm from './OrganizationSubscriptionForm'


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

import OrganizationMenu from "../OrganizationMenu"


const CREATE_SUBSCRIPTION = gql`
  mutation CreateSubscription($input: CreateOrganizationSubscriptionInput!) {
    createOrganizationSubscription(input: $input) {
      organizationSubscription {
        id
        displayPublic
        displayShop
        name
        description
        sortOrder
        minDuration
        classes
        subscriptionUnit
        subscriptionUnitDisplay
        reconciliationClasses
        creditValidity
        unlimited
        termsAndConditions
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


class OrganizationSubscriptionAdd extends Component {
  constructor(props) {
    super(props)
    console.log("Organization subscription add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const return_url = "/organization/subscriptions"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.subscriptions.title_add')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_INPUT_VALUES_QUERY} variables = {{archived: false}} >
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
                    const inputData = data

                    return (
                      
                      <Mutation mutation={CREATE_SUBSCRIPTION} onCompleted={() => history.push(return_url)}> 
                      {(createSubscription, { data }) => (
                          <Formik
                              initialValues={{ 
                                displayPublic: true,
                                displayShop: true,
                                name: "",
                                description: "",
                                sortOrder: 0,
                                minDuration: 1,
                                classes: 1,
                                subscriptionUnit: "WEEK",
                                reconciliationClasses: 0,
                                creditValidity: 1,
                                unlimited: false,
                                termsAndConditions: "",
                                organizationMembership: "",
                                quickStatsAmount: 0,
                                financeGlaccount: "",
                                financeCostcenter: ""
                              }}
                              validationSchema={SUBSCRIPTION_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  createSubscription({ variables: {
                                    input: {
                                      displayPublic: values.displayPublic,
                                      displayShop: values.displayShop,
                                      name: values.name,
                                      description: values.description,
                                      sortOrder: values.sortOrder,
                                      minDuration: values.minDuration,
                                      classes: values.classes,
                                      subscriptionUnit: values.subscriptionUnit,
                                      reconciliationClasses: values.reconciliationClasses,
                                      creditValidity: values.creditValidity,
                                      unlimited: values.unlimited,
                                      termsAndConditions: values.termsAndConditions,
                                      quickStatsAmount: values.quickStatsAmount,
                                      financeGlaccount: values.financeGlaccount,
                                      financeCostcenter: values.financeCostcenter
                                    }
                                  }, refetchQueries: [
                                      {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.subscriptions.toast_add_success')), {
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
                              {({ isSubmitting, setFieldValue, setFieldTouched, errors, values }) => (
                                <OrganizationSubscriptionForm
                                  inputData={inputData}
                                  isSubmitting={isSubmitting}
                                  setFieldValue={setFieldValue}
                                  setFieldTouched={setFieldTouched}
                                  errors={errors}
                                  values={values}
                                  return_url={return_url}
                                />
                                  // <FoForm>
                                  //     <Card.Body> 
                                  //       <Form.Group>
                                  //         <Form.Label className="custom-switch">
                                  //             <Field 
                                  //               className="custom-switch-input"
                                  //               type="checkbox" 
                                  //               name="displayPublic" 
                                  //               checked={values.displayPublic} />
                                  //             <span className="custom-switch-indicator" ></span>
                                  //             <span className="custom-switch-description">{t('organization.subscription.public')}</span>
                                  //           </Form.Label>
                                  //         <ErrorMessage name="displayPublic" component="div" />   
                                  //       </Form.Group>      
                                  //       <Form.Group>
                                  //         <Form.Label className="custom-switch">
                                  //             <Field 
                                  //               className="custom-switch-input"
                                  //               type="checkbox" 
                                  //               name="displayShop" 
                                  //               checked={values.displayShop} />
                                  //             <span className="custom-switch-indicator" ></span>
                                  //             <span className="custom-switch-description">{t('organization.subscription.shop')}</span>
                                  //           </Form.Label>
                                  //         <ErrorMessage name="displayShop" component="div" />   
                                  //       </Form.Group>      
                                  //       <Form.Group label={t('general.name')} >
                                  //         <Field type="text" 
                                  //               name="name" 
                                  //               className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                  //               autoComplete="off" />
                                  //         <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                  //       </Form.Group>
                                  //       <Form.Group label={t('general.description')}>
                                  //         <Editor
                                  //             textareaName="description"
                                  //             initialValue={values.description}
                                  //             init={tinymceBasicConf}
                                  //             onChange={(e) => setFieldValue("description", e.target.getContent())}
                                  //             onBlur={() => setFieldTouched("description", true)}
                                  //           />
                                  //         <ErrorMessage name="description" component="span" className="invalid-feedback" />
                                  //       </Form.Group>
                                  //       <Form.Group label={t('general.sort_order')}>
                                  //         <Field type="text" 
                                  //               name="sortOrder" 
                                  //               className={(errors.sortOrder) ? "form-control is-invalid" : "form-control"} 
                                  //               autoComplete="off" />
                                  //         <ErrorMessage name="sortOrder" component="span" className="invalid-feedback" />
                                  //       </Form.Group>
                                  //       <Form.Group label={t('general.min_duration')}>
                                  //         <Field type="text" 
                                  //               name="minDuration" 
                                  //               className={(errors.minDuration) ? "form-control is-invalid" : "form-control"} 
                                  //               autoComplete="off" />
                                  //         <ErrorMessage name="minDuration" component="span" className="invalid-feedback" />
                                  //       </Form.Group>
                                  //       <Form.Group>
                                  //         <Form.Label className="custom-switch">
                                  //             <Field 
                                  //               className="custom-switch-input"
                                  //               type="checkbox" 
                                  //               name="unlimited" 
                                  //               checked={values.unlimied} />
                                  //             <span className="custom-switch-indicator" ></span>
                                  //             <span className="custom-switch-description">{t('general.unlimited')}</span>
                                  //           </Form.Label>
                                  //         <ErrorMessage name="unlimited" component="div" />   
                                  //       </Form.Group>  
                                  //       {/* Show if unlimited */}
                                  //       { (values.unlimited) ? 
                                  //         <Form.Group label={t('general.quickStatsAmount')}>
                                  //           <Field type="text" 
                                  //                 name="quickStatsAmount" 
                                  //                 className={(errors.quickStatsAmount) ? "form-control is-invalid" : "form-control"} 
                                  //                 autoComplete="off" />
                                  //           <ErrorMessage name="quickStatsAmount" component="span" className="invalid-feedback" />
                                  //         </Form.Group>
                                  //         : 
                                  //         // Show if not unlimited
                                  //         <span>
                                  //           <Form.Group label={t('general.classes')}>
                                  //             <Field type="text" 
                                  //                   name="classes" 
                                  //                   className={(errors.classes) ? "form-control is-invalid" : "form-control"} 
                                  //                   autoComplete="off" />
                                  //             <ErrorMessage name="classes" component="span" className="invalid-feedback" />
                                  //           </Form.Group> 
                                  //           <Form.Group label={t('general.subscription_unit')}>
                                  //             <Field component="select" 
                                  //                   name="subscriptionUnit" 
                                  //                   className={(errors.subscriptionUnit) ? "form-control is-invalid" : "form-control"} 
                                  //                   autoComplete="off">
                                  //               <option value="WEEK" key={v4()}>{t('subscription_unit.week')}</option>
                                  //               <option value="MONTH" key={v4()}>{t('subscription_init.month')}</option>
                                  //             </Field>
                                  //             <ErrorMessage name="subscriptionUnit" component="span" className="invalid-feedback" />
                                  //           </Form.Group>
                                  //           <Form.Group label={t('general.credit_validity')}>
                                  //             <Field type="text" 
                                  //                   name="creditValidity" 
                                  //                   className={(errors.creditValidity) ? "form-control is-invalid" : "form-control"} 
                                  //                   autoComplete="off" />
                                  //             <ErrorMessage name="creditValidity" component="span" className="invalid-feedback" />
                                  //           </Form.Group>
                                  //         </span>
                                  //       } 
                                  //       <Form.Group label={t('general.terms_and_conditions')}>
                                  //         <Editor
                                  //             textareaName="termsAndConditions"
                                  //             initialValue={values.termsAndConditions}
                                  //             init={tinymceBasicConf}
                                  //             onChange={(e) => setFieldValue("termsAndConditions", e.target.getContent())}
                                  //             onBlur={() => setFieldTouched("termsAndConditions", true)}
                                  //           />
                                  //         <ErrorMessage name="termsAndConditions" component="span" className="invalid-feedback" />
                                  //       </Form.Group>
                                  //       <Form.Group label={t('general.membership')}>
                                  //         <Field component="select" 
                                  //                name="organizationMembership" 
                                  //                className={(errors.organizationMembership) ? "form-control is-invalid" : "form-control"} 
                                  //                autoComplete="off">
                                  //           <option value="" key={v4()}>{t("general.membership_not_required")}</option>
                                  //           {inputData.organizationMemberships.edges.map(({ node }) =>
                                  //             <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                                  //           )}
                                  //         </Field>
                                  //         <ErrorMessage name="organizationMembership" component="span" className="invalid-feedback" />
                                  //       </Form.Group> 
                                  //       <Form.Group label={t('general.glaccount')}>
                                  //         <Field component="select" 
                                  //                name="financeGlaccount" 
                                  //                className={(errors.financeGlaccount) ? "form-control is-invalid" : "form-control"} 
                                  //                autoComplete="off">
                                  //           <option value="" key={v4()}></option>
                                  //           {inputData.financeGlaccounts.edges.map(({ node }) =>
                                  //             <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                                  //           )}
                                  //         </Field>
                                  //         <ErrorMessage name="financeGlaccount" component="span" className="invalid-feedback" />
                                  //       </Form.Group>
                                  //       <Form.Group label={t('general.costcenter')}>
                                  //         <Field component="select" 
                                  //                name="financeCostcenter" 
                                  //                className={(errors.financeCostcenter) ? "form-control is-invalid" : "form-control"} 
                                  //                autoComplete="off">
                                  //           <option value="" key={v4()}></option>
                                  //           {inputData.financeCostcenters.edges.map(({ node }) =>
                                  //             <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                                  //           )}
                                  //         </Field>
                                  //         <ErrorMessage name="financeCostcenter" component="span" className="invalid-feedback" />
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
                <HasPermissionWrapper permission="add"
                                      resource="organizationsubscription">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <OrganizationMenu active_link='subscriptions'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationSubscriptionAdd))