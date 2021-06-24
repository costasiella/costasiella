// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from "uuid"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../plugin_config/tinymce"


import {
  Grid,
  Button,
  Card,
  Form
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"


class OrganizationClasspassForm extends Component {
  constructor(props) {
    super(props)
    console.log("Organization classpass form props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/organization/classpasses"
    const initialData = this.props.initialData
    const isSubmitting = this.props.isSubmitting
    const setFieldValue = this.props.setFieldValue
    const setFieldTouched = this.props.setFieldTouched
    const errors = this.props.errors
    const values = this.props.values

    return (
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
            <Grid.Row>
              <Grid.Col>
                <Form.Group>
                  <Form.Label className="custom-switch">
                      <Field 
                      className="custom-switch-input"
                      type="checkbox" 
                      name="trialPass" 
                      checked={values.trialPass} />
                      <span className="custom-switch-indicator" ></span>
                      <span className="custom-switch-description">{t('organization.classpass.trial_pass')}</span>
                  </Form.Label>
                  <ErrorMessage name="displayShop" component="div" />   
                </Form.Group>
              </Grid.Col>
            </Grid.Row>  
            { (!values.trialPass) ? "" : 
              <Form.Group label={t('organization.classpass.trial_times')} >
                <Field type="text" 
                    name="trialTimes" 
                    className={(errors.trialTimes) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
                <ErrorMessage name="trialTimes" component="span" className="invalid-feedback" />
              </Form.Group>
            }                
            <Form.Group label={t('general.name')} >
                <Field type="text" 
                    name="name" 
                    className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
                <ErrorMessage name="name" component="span" className="invalid-feedback" />
            </Form.Group>
            <Form.Group label={t('general.description')}>
                <Editor
                    textareaName="description"
                    initialValue={values.description}
                    init={tinymceBasicConf}
                    onChange={(e) => setFieldValue("description", e.target.getContent())}
                    onBlur={() => setFieldTouched("description", true)}
                />
                <ErrorMessage name="description" component="span" className="invalid-feedback" />
            </Form.Group>
            <Grid.Row>
              <Grid.Col>
                <Form.Group label={t('general.price')}>
                    <Field type="text" 
                        name="price" 
                        className={(errors.price) ? "form-control is-invalid" : "form-control"} 
                        autoComplete="off" />
                    <ErrorMessage name="price" component="span" className="invalid-feedback" />
                </Form.Group>
              </Grid.Col>
              <Grid.Col>
                <Form.Group label={t('general.taxrate')}>
                  <Field component="select" 
                          name="financeTaxRate" 
                          className={(errors.financeTaxRate) ? "form-control is-invalid" : "form-control"} 
                          autoComplete="off">
                  {console.log("query data in classpass add:")}
                  {console.log(initialData)}
                  <option value="" key={v4()}></option>
                  {initialData.financeTaxRates.edges.map(({ node }) =>
                      <option value={node.id} key={v4()}>{node.name} ({node.percentage}% {node.rateType})</option>
                  )}
                  </Field>
                  <ErrorMessage name="financeTaxRate" component="span" className="invalid-feedback" />
                </Form.Group>
              </Grid.Col>
            </Grid.Row>
            <Grid.Row>
              <Grid.Col>
                <Form.Group label={t('general.validity')}>
                  <Field type="text" 
                      name="validity" 
                      className={(errors.validity) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
                  <ErrorMessage name="validity" component="span" className="invalid-feedback" />
                </Form.Group>
              </Grid.Col>
              <Grid.Col>
                <Form.Group label={t('general.validity_unit')}>
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
              </Grid.Col>
            </Grid.Row>
            <Form.Group>
                <Form.Label className="custom-switch">
                    <Field 
                    className="custom-switch-input"
                    type="checkbox" 
                    name="unlimited" 
                    checked={values.unlimied} />
                    <span className="custom-switch-indicator" ></span>
                    <span className="custom-switch-description">{t('general.unlimited')}</span>
                </Form.Label>
                <ErrorMessage name="unlimited" component="div" />   
            </Form.Group>  
            { (values.unlimited) ? "" :
            <Form.Group label={t('general.classes')}>
                <Field type="text" 
                        name="classes" 
                        className={(errors.classes) ? "form-control is-invalid" : "form-control"} 
                        autoComplete="off" />
                <ErrorMessage name="classes" component="span" className="invalid-feedback" />
            </Form.Group> } 
            {/* <Form.Group label={t('general.membership')}>
                <Field component="select" 
                        name="organizationMembership" 
                        className={(errors.organizationMembership) ? "form-control is-invalid" : "form-control"} 
                        autoComplete="off">
                <option value="" key={v4()}>{t("general.membership_not_required")}</option>
                {initialData.organizationMemberships.edges.map(({ node }) =>
                    <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                )}
                </Field>
                <ErrorMessage name="organizationMembership" component="span" className="invalid-feedback" />
            </Form.Group>  */}
            { (values.unlimited) ? 
                    <Form.Group label={t('general.quickStatsAmount')}>
                    <Field type="text" 
                            name="quickStatsAmount" 
                            className={(errors.quickStatsAmount) ? "form-control is-invalid" : "form-control"} 
                            autoComplete="off" />
                    <ErrorMessage name="quickStatsAmount" component="span" className="invalid-feedback" />
                    </Form.Group>
                    : ""
            }
            <Grid.Row>
              <Grid.Col>
                <Form.Group label={t('general.glaccount')}>
                  <Field component="select" 
                          name="financeGlaccount" 
                          className={(errors.financeGlaccount) ? "form-control is-invalid" : "form-control"} 
                          autoComplete="off">
                  <option value="" key={v4()}></option>
                  {initialData.financeGlaccounts.edges.map(({ node }) =>
                      <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                  )}
                  </Field>
                  <ErrorMessage name="financeGlaccount" component="span" className="invalid-feedback" />
                </Form.Group>
              </Grid.Col>
              <Grid.Col>
                <Form.Group label={t('general.costcenter')}>
                  <Field component="select" 
                          name="financeCostcenter" 
                          className={(errors.financeCostcenter) ? "form-control is-invalid" : "form-control"} 
                          autoComplete="off">
                  <option value="" key={v4()}></option>
                  {initialData.financeCostcenters.edges.map(({ node }) =>
                      <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                  )}
                  </Field>
                  <ErrorMessage name="financeCostcenter" component="span" className="invalid-feedback" />
                </Form.Group>
              </Grid.Col>
            </Grid.Row>
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
    ) 
  }
}


export default withTranslation()(withRouter(OrganizationClasspassForm))