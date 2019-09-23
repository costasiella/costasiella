// @flow

import React from 'react'
import { useMutation, useQuery } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { 
  Formik,
  Form as FoForm, 
  Field, 
  ErrorMessage 
} from 'formik'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'

import { UPDATE_DOCUMENT, GET_DOCUMENT_QUERY, GET_DOCUMENTS_QUERY } from "./queries"
import { DOCUMENT_SCHEMA } from './yupSchema'
import { dateToLocalISO } from "../../../../tools/date_tools"
// import OrganizationDocumentForm from './OrganizationDocumentForm'
import CSDatePicker from "../../../ui/CSDatePicker"

import {
  Grid,
  Icon,
  Button,
  Card,
  Form,
} from "tabler-react"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationDocumentsBase from "./OrganizationDocumentsBase"
import { getSubtitle } from './tools'


function OrganizationDocumentEdit({ t, match, history }) {
  const organizationId = match.params.organization_id
  const documentType = match.params.document_type
  const id = match.params.id
  const subTitle = getSubtitle(t, documentType)
  
  const returnUrl = `/organization/documents/${organizationId}/${documentType}`
  const sidebarButton = <HasPermissionWrapper 
    permission="change"
    resource="organizationdocument">
      <Link to={returnUrl} >
        <Button color="primary btn-block mb-6" >
          <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
        </Button>
      </Link>
  </HasPermissionWrapper>

  const [updateDocument, { data: dataUpdate }] = useMutation(UPDATE_DOCUMENT, {
    onCompleted: () => history.push(returnUrl)
  })
  const { loading, error, data } = useQuery(GET_DOCUMENT_QUERY, {
    variables: { "id": id }
  })

  if (loading) {
    return (
      <OrganizationDocumentsBase sidebarButton={sidebarButton}>
        {t("general.loading_with_dots")}
      </OrganizationDocumentsBase>
    )
  }

  if (error) {
    return (
      <OrganizationDocumentsBase sidebarButton={sidebarButton}>
        {t("organization.documents.error_loading")}
      </OrganizationDocumentsBase>
    )
  }


  return (
    <OrganizationDocumentsBase sidebarButton={sidebarButton}>
      <Card>
        <Card.Header>
          <Card.Title>
            {t('organization.documents.edit') + ' - ' + subTitle}
          </Card.Title>
        </Card.Header>
        <Formik
          initialValues={{ 
            version: data.organizationDocument.version,
            dateStart: data.organizationDocument.dateStart, 
            dateEnd: data.organizationDocument.dateEnd,
          }}
          // validationSchema={DOCUMENT_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
            console.log("Submit values")
            console.log(values)

            let inputVars = {
              id: id,
              version: values.version,
              dateStart: dateToLocalISO(values.dateStart),
            }

            if (values.dateEnd) {
              inputVars.dateEnd = dateToLocalISO(values.dateEnd)
            }

            updateDocument({ variables: {
              input: inputVars
            }, refetchQueries: [
                {query: GET_DOCUMENTS_QUERY, variables: {documentType: documentType}}
            ]})
            .then(({ data }) => {
                console.log('got data', data);
                toast.success((t('organization.documents.toast_edit_success')), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                  setSubmitting(false)
              }).catch((error) => {
                toast.error((t('general.toast_server_error')) + ': ' +  error, {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                console.log('there was an error sending the query', error)
                setSubmitting(false)
              })
          }}
          >
          {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
            <FoForm>
            <Card.Body>
              <Grid.Row>
                <Grid.Col>
                  <Form.Group label={t('general.version')}>
                    <Field type="text" 
                          name="version" 
                          className={(errors.version) ? "form-control is-invalid" : "form-control"} 
                          autoComplete="off" />
                    <ErrorMessage name="version" component="span" className="invalid-feedback" />
                  </Form.Group>
                </Grid.Col>
                {/* <Grid.Col>
                  <Form.Group label={t('general.custom_file_input_label')}>
                    <div className="custom-file">
                      <input type="file" ref={inputFileName} className="custom-file-input" onChange={handleFileInputChange} />
                      <label className="custom-file-label" style={customFileInputLabelStyle}>
                        {fileInputLabel}
                      </label>
                    </div>
                  </Form.Group>
                </Grid.Col> */}
              </Grid.Row>
              <Grid.Row>
                <Grid.Col>
                  <Form.Group label={t('general.date_start')}>
                    <CSDatePicker 
                      selected={values.dateStart}
                      onChange={(date) => setFieldValue("dateStart", date)}
                      onBlur={() => setFieldTouched("dateStart", true)}
                    />
                    <ErrorMessage name="dateStart" component="span" className="invalid-feedback" />
                  </Form.Group>
                </Grid.Col>
                <Grid.Col>
                  <Form.Group label={t('general.date_end')}>
                    <CSDatePicker 
                      selected={values.dateEnd}
                      onChange={(date) => setFieldValue("dateEnd", date)}
                      onBlur={() => setFieldTouched("dateEnd", true)}
                    />
                    <ErrorMessage name="dateEnd" component="span" className="invalid-feedback" />
                  </Form.Group>
                </Grid.Col>
              </Grid.Row>
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
              <Button color="link" onClick={() => history.push(returnUrl)}>
                {t('general.cancel')}
              </Button>
            </Card.Footer>
          </FoForm>
          )}
        </Formik>
      </Card>
    </OrganizationDocumentsBase>
  )
}

export default withTranslation()(OrganizationDocumentEdit)
