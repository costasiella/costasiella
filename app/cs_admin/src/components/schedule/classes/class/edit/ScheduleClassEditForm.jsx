import React, { Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"

import {
    Button,
    Card,
    Form,
    Grid
  } from "tabler-react"
import { Form as FoForm, Field, ErrorMessage } from 'formik'

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../../../plugin_config/tinymce"
import CSDatePicker from "../../../../ui/CSDatePicker"
import CSTimePicker from "../../../../ui/CSTimePicker"

const ScheduleClassEditForm = ({ t, history, inputData, isSubmitting, setFieldValue, setFieldTouched, errors, values, touched, return_url }) => (
    <FoForm>
      <Card.Body>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.status')}>
              <Field component="select" 
                      name="status" 
                      className={(errors.status) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                <option value="" key={v4()}>{t('')}</option>
                <option value="CANCELLED" key={v4()}>{t('general.cancelled')}</option>
                <option value="OPEN" key={v4()}>{t('schedule.classes.no_teacher')}</option>
              </Field>
              <ErrorMessage name="status" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.description')}>
              <Field type="text" 
                      name="description" 
                      className={(errors.description) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="description" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.teacher')}>
              <Field component="select" 
                      name="account" 
                      className={(errors.account) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                {console.log("query data in schedule class teacher add:")}
                {console.log(inputData)}
                <option value="" key={v4()}>{t('general.please_select')}</option>
                {inputData.accounts.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.fullName}</option>
                )}
              </Field>
              <ErrorMessage name="account" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.teacher_role')}>
              <Field component="select" 
                      name="role" 
                      className={(errors.role) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                <option value="" key={v4()}></option>
                <option value="SUB" key={v4()}>{t('schedule.classes.teacher_roles.sub')}</option>
                <option value="ASSISTANT" key={v4()}>{t('schedule.classes.teacher_roles.assistant')}</option>
                <option value="KARMA" key={v4()}>{t('schedule.classes.teacher_roles.karma')}</option>
              </Field>
              <ErrorMessage name="role" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.teacher2')}>
              <Field component="select" 
                      name="account2" 
                      className={(errors.account2) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                <option value="" key={v4()}></option>
                {inputData.accounts.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.fullName}</option>
                )}
              </Field>
              <ErrorMessage name="account2" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.teacher_role2')}>
              <Field component="select" 
                      name="role2" 
                      className={(errors.role2) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                <option value="" key={v4()}></option>
                <option value="SUB" key={v4()}>{t('schedule.classes.teacher_roles.sub')}</option>
                <option value="ASSISTANT" key={v4()}>{t('schedule.classes.teacher_roles.assistant')}</option>
                <option value="KARMA" key={v4()}>{t('schedule.classes.teacher_roles.karma')}</option>
              </Field>
              <ErrorMessage name="role2" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.location')}>
              <Field component="select" 
                    name="organizationLocationRoom" 
                    className={(errors.organizationLocationRoom) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="" key={v4()}>{t("general.no_change")}</option>
                {inputData.organizationLocationRooms.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.organizationLocation.name} - {node.name}</option>
                )}
              </Field>
              <ErrorMessage name="organizationLocationRoom" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.level')}>
              <Field component="select" 
                    name="organizationLevel" 
                    className={(errors.organizationLevels) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="" key={v4()}>{t("general.no_change")}</option>
                {inputData.organizationLevels.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.name}</option>
                )}
              </Field>
              <ErrorMessage name="organizationLevels" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
        </Grid.Row>
        <Form.Group label={t('general.class')}>
          <Field component="select" 
                name="organizationClasstype" 
                className={(errors.organizationClasstype) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off">
            <option value="" key={v4()}>{t("general.no_change")}</option>
            {inputData.organizationClasstypes.edges.map(({ node }) =>
              <option value={node.id} key={v4()}>{node.name}</option>
            )}
          </Field>
          <ErrorMessage name="organizationClasstype" component="span" className="invalid-feedback" />
        </Form.Group> 
        <Grid.Row>
          <Grid.Col>
           <Form.Group label={t('general.time_start')}>
              <CSTimePicker 
                className={(errors.timeStart) ? "form-control is-invalid" : "form-control"} 
                selected={values.timeStart}
                onChange={(date) => setFieldValue("timeStart", date)}
                onBlur={() => setFieldTouched("timeStart", true)}
                clearable={false}
              />
              {/* {errors.timeStart}
              {errors.timeStart && touched.timeStart ? (
                <span className="invalid-feedback">{errors.timeStart} - hacky thingy</span>
              ) : null} */}
              <ErrorMessage name="timeStart" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
           <Form.Group label={t('general.time_end')}>
              <CSTimePicker 
                className={(errors.timeEnd) ? "form-control is-invalid" : "form-control"} 
                selected={values.timeEnd}
                onChange={(date) => setFieldValue("timeEnd", date)}
                onBlur={() => setFieldTouched("timeEnd", true)}
                clearable={false}
              />
              <ErrorMessage name="timeEnd" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('schedule.classes.spaces')}>
              <Field type="text" 
                    name="spaces" 
                    className={(errors.spaces) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
              <ErrorMessage name="spaces" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('schedule.classes.spaces_walk_in')}>
              <Field type="text" 
                    name="walkInSpaces" 
                    className={(errors.walkInSpaces) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
              <ErrorMessage name="walkInSpaces" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
        </Grid.Row>
        <Form.Group label={t('general.info_mail')}>
          <Editor
              textareaName="infoMailContent"
              initialValue={values.infoMailContent}
              init={tinymceBasicConf}
              onChange={(e) => setFieldValue("infoMailContent", e.target.getContent())}
              onBlur={() => setFieldTouched("infoMailContent", true)}
            />
          <ErrorMessage name="note" component="span" className="invalid-feedback" />
        </Form.Group>
        {/* <Form.Group label={t('general.note')}>
          <Editor
              textareaName="note"
              initialValue={values.note}
              init={tinymceBasicConf}
              onChange={(e) => setFieldValue("note", e.target.getContent())}
              onBlur={() => setFieldTouched("note", true)}
            />
          <ErrorMessage name="note" component="span" className="invalid-feedback" />
        </Form.Group> */}
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
)
  
  
  export default withTranslation()(withRouter(ScheduleClassEditForm))