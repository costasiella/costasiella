// @flow

import React, { useState, useRef } from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'

import {
  Button,
  Icon
} from "tabler-react"

import { GET_SCHEDULE_EVENT_MEDIAS_QUERY, GET_SCHEDULE_EVENT_MEDIA_QUERY } from "./queries"
import { SCHEDULE_EVENT_MEDIA_SCHEMA } from './yupSchema'

import ScheduleEventMediaBack from "./ScheduleEventMediaBack"
import ScheduleEventMediaEditBase from "./ScheduleEventMediaEditBase"
import ScheduleEventMediaForm from "./ScheduleEventMediaForm"


const UPDATE_SCHEDULE_EVENT_MEDIA = gql`
  mutation UpdateScheduleEventMedia($input:UpdateScheduleEventMediaInput!) {
    updateScheduleEventMedia(input: $input) {
      scheduleEventMedia {
        id
      }
    }
  }
`


function ScheduleEventMediaEdit({ t, history, match }) {
  const eventId = match.params.event_id
  const scheduleEventMediaId = match.params.id
  const returnUrl = `/schedule/events/edit/${eventId}/media/`
  const activeTab = 'general'
  const cardTitle = t("schedule.events.media.edit")

  const [updateScheduleEventMedia] = useMutation(UPDATE_SCHEDULE_EVENT_MEDIA)
  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_EVENT_MEDIA_QUERY, {
    variables: {
      id: scheduleEventMediaId
  }})

  const sidebarContent = <ScheduleEventMediaBack />

  // Vars for document file input field start
  const [fileName, setFileName] = useState("")
  const inputFileName = useRef(null)
  const fileInputLabel = fileName || t("general.custom_file_input_inner_label")

  const handleFileInputChange = (event) => {
    console.log('on change triggered')
    setFileName(event.target.files[0].name)
  }

  if (loading) return (
    <ScheduleEventMediaEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      {t("general.loading_with_dots")}
    </ScheduleEventMediaEditBase>
  )
  if (error) return (
    <ScheduleEventMediaEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventMediaEditBase>
  )

  const inputData = data
  const scheduleEventMedia = data.scheduleEventMedia
  console.log(inputData)

  return (
    <ScheduleEventMediaEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      <Formik
        initialValues={{ 
          description: scheduleEventMedia.description,
          sortOrder: scheduleEventMedia.sortOrder
        }}
        validationSchema={SCHEDULE_EVENT_MEDIA_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("Submit values")
          console.log(values)
          console.log(fileName)

          let inputVars = {
            id: scheduleEventMediaId,
            description: values.description,
            sortOrder: values.sortOrder
          }

          function updateMedia() {
            updateScheduleEventMedia({ variables: {
              input: inputVars
            }, refetchQueries: [
                {query: GET_SCHEDULE_EVENT_MEDIAS_QUERY, variables: {scheduleEvent: eventId}}
            ]})
            .then(({ data }) => {
                console.log('got data', data);
                toast.success((t('schedule.events.media.toast_edit_success')), {
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
          }

          let reader = new FileReader()
          reader.onload = function(reader_event) {
            console.log(reader_event.target.result)
            let b64_enc_file = reader_event.target.result
            console.log(b64_enc_file)
            // Add uploaded document b64 encoded blob to input vars
            inputVars.image = b64_enc_file
            inputVars.imageFileName = fileName

            updateMedia()
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
            updateMedia()
          }
        }}
        >
        {({ isSubmitting, errors, values }) => (
          <ScheduleEventMediaForm
            isSubmitting={isSubmitting}
            errors={errors}
            values={values}
            inputFileName={inputFileName}
            fileInputLabel={fileInputLabel}
            handleFileInputChange={handleFileInputChange}
            returnUrl={returnUrl}
          />
        )}
      </Formik>
    </ScheduleEventMediaEditBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventMediaEdit))