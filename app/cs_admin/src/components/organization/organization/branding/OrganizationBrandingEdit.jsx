// @flow

import React, { useState, useRef } from 'react'
import gql from "graphql-tag"
import { useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ORGANIZATION_QUERY } from '../queries'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react";

import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationBrandingBase from "./OrganizationBrandingBase"
import OrganizationBrandingEditForm from "./OrganizationBrandingEditForm"
import { updateLocale } from 'moment'


const UPDATE_ORGANIZATION = gql`
  mutation UpdateOrganization($input: UpdateOrganizationInput!) {
    updateOrganization(input: $input) {
      organization {
        id
      }
    }
  }
`


function OrganizationBrandingEdit({t, match, history}) {
  const id = match.params.id
  const updateField = match.params.update_field
  const returnUrl = `/organization/edit/${id}/branding`

  let formTitle = ""
  switch (updateField) {
    case "logoLogin":
      formTitle = t("organization.branding.logo_login")
      break
    default:
      break
  }


  const [updateOrganization] = useMutation(UPDATE_ORGANIZATION)

  // Vars for document file input field start
  const [fileName, setFileName] = useState("")
  const inputFileName = useRef(null)
  const fileInputLabel = fileName || t("general.custom_file_input_inner_label")

  const handleFileInputChange = (event) => {
    console.log('on change triggered')
    setFileName(event.target.files[0].name)
  }

  return (
 
    <OrganizationBrandingBase>
      <Formik
        initialValues={{}}
        onSubmit={(values, { setSubmitting }) => {
          console.log("Submit values")
          console.log(values)
          console.log(fileName)

          let inputVars = {
            id: id
          }

          let reader = new FileReader()
          reader.onload = function(reader_event) {
            console.log(reader_event.target.result)
            let b64_enc_file = reader_event.target.result
            console.log(b64_enc_file)
            // Add uploaded document b64 encoded blob to input vars
            switch(updateField) {
              case "logoLogin":
                inputVars.logoLoginFileName = fileName
                inputVars.logoLogin = b64_enc_file
                break
              case "logoInvoice":
                inputVars.logoInvoiceFileName = fileName
                inputVars.logoInvoice = b64_enc_file
                break
              case "logoEmail":
                inputVars.logoEmailFileName = fileName
                inputVars.logoEmail = b64_enc_file
                break
              case "logoShopHeader":
                inputVars.logoShopHeaderFileName = fileName
                inputVars.logoShopHeader = b64_enc_file
                break
              case "logoSelfCheckin":
                inputVars.logoSelfCheckinFileName = fileName
                inputVars.logoSelfCheckin = b64_enc_file
                break
              default:
                break              
            }
            
            updateOrganization({ variables: {
              input: inputVars
            }, refetchQueries: [
                {query: GET_ORGANIZATION_QUERY, variables: {id: id}}
            ]})
            .then(({ data }) => {
                console.log('got data', data);
                setSubmitting(false)
                history.push(returnUrl)
                toast.success((t('organization.branding.toast_edit_success')), {
                    position: toast.POSITION.BOTTOM_RIGHT
                })
              }).catch((error) => {
                toast.error((t('general.toast_server_error')) + ': ' +  error, {
                    position: toast.POSITION.BOTTOM_RIGHT
                })
                console.log('there was an error sending the query', error)
                setSubmitting(false)
              })
          }
          
          let file = inputFileName.current.files[0]
          if (file && file.size < 5242880) {
            reader.readAsDataURL(file)
          } else if (file && file.size > 5242880) { 
            toast.error(t("error_messages.selected_file_exceeds_max_filesize"), {
              position: toast.POSITION.BOTTOM_RIGHT
            })
            setSubmitting(false)
          } else {
            toast.error(t("general.please_select_a_file"), {
              position: toast.POSITION.BOTTOM_RIGHT
            })
            setSubmitting(false)
          }
        }}
      >
        {({ isSubmitting }) => (
          <OrganizationBrandingEditForm 
            isSubmitting={isSubmitting}
            formTitle={formTitle}
            inputFileName={inputFileName}
            fileInputLabel={fileInputLabel}
            handleFileInputChange={handleFileInputChange}
          />
        )}
      </Formik>
    </OrganizationBrandingBase>
  )
}


export default withTranslation()(withRouter(OrganizationBrandingEdit))