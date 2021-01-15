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

import { GET_SCHEDULE_EVENT_MEDIAS_QUERY } from "./queries"
import { SCHEDULE_EVENT_MEDIA_SCHEMA } from './yupSchema'

import ScheduleEventMediaBack from "./ScheduleEventMediaBack"
import ScheduleEventEditBase from "../edit/ScheduleEventEditBase"
import ScheduleEventMediaForm from "./ScheduleEventMediaForm"


const ADD_SCHEDULE_EVENT_MEDIA = gql`
  mutation CreateScheduleEventMedia($input:CreateScheduleEventMediaInput!) {
    createScheduleEventMedia(input: $input) {
      scheduleEventMedia {
        id
      }
    }
  }
`


function ScheduleEventMediaAdd({ t, history, match }) {
  const eventId = match.params.event_id
  const returnUrl = `/schedule/events/edit/${eventId}/media/`
  const activeLink = 'media'
  const cardTitle = t("schedule.events.media.add")

  const [addScheduleEventMedia] = useMutation(ADD_SCHEDULE_EVENT_MEDIA, {
    onCompleted: () => history.push(returnUrl),
  })

  // Vars for document file input field start
  const [fileName, setFileName] = useState("")
  const inputFileName = useRef(null)
  const fileInputLabel = fileName || t("general.custom_file_input_inner_label")

  const handleFileInputChange = (event) => {
    console.log('on change triggered')
    setFileName(event.target.files[0].name)
  }

  const sidebarContent = <ScheduleEventMediaBack />

  return (
    <ScheduleEventEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      <Formik
        initialValues={{ 
          description: "",
          sortOrder: 0,
        }}
        validationSchema={SCHEDULE_EVENT_MEDIA_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("Submit values")
          console.log(values)
          console.log(fileName)

          let inputVars = {
            scheduleEvent: eventId,
            description: values.description,
            sortOrder: values.sortOrder,
            imageFileName: fileName,
          }

          let reader = new FileReader()
          reader.onload = function(reader_event) {
            console.log(reader_event.target.result)
            let b64_enc_file = reader_event.target.result
            console.log(b64_enc_file)
            // Add uploaded document b64 encoded blob to input vars
            inputVars.image = b64_enc_file

            addScheduleEventMedia({ variables: {
              input: inputVars
            }, refetchQueries: [
                {query: GET_SCHEDULE_EVENT_MEDIAS_QUERY, variables: {scheduleEvent: eventId}}
            ]})
            .then(({ data }) => {
                console.log('got data', data);
                toast.success((t('schedule.events.media.toast_add_success')), {
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
    </ScheduleEventEditBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventMediaAdd))