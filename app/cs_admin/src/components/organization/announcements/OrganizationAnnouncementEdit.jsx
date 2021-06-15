// @flow

import React from 'react'
import { useMutation, useQuery } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ANNOUNCEMENTS_QUERY, GET_ANNOUNCEMENT_QUERY, UPDATE_ANNOUNCEMENT } from './queries'
import { ANNOUNCEMENT_SCHEMA } from './yupSchema'
import OrganizationAnnouncementForm from './OrganizationAnnouncementForm'


import {
  Card,
} from "tabler-react"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationAnnouncementsBase from "./OrganizationAnnouncementsBase"
import { dateToLocalISO } from '../../../tools/date_tools'

function OrganizationAnnouncementEdit({t, history, match}) {
  const announcementId = match.params.id
  const cardTitle = t("organization.announcements.title_edit")
  const returnUrl = "/organization/announcements"
  
  const { loading, error, data } = useQuery(GET_ANNOUNCEMENT_QUERY, { variables: {
    id: announcementId
  }})
  const [updateAnnouncement] = useMutation(UPDATE_ANNOUNCEMENT)

  if (loading) return (
    <OrganizationAnnouncementsBase showEditBack={true}>
      <Card title={cardTitle}>
        <Card.Body>
          {t("general.loading_with_dots")}
        </Card.Body>
      </Card>
    </OrganizationAnnouncementsBase>
  )

  if (error) return (
    <OrganizationAnnouncementsBase showEditBack={true}>
      <Card title={cardTitle}>
        <Card.Body>
          {t("general.error_sad_smiley")}
        </Card.Body>
      </Card>
    </OrganizationAnnouncementsBase>
  )

  const organizationAnnouncement = data.organizationAnnouncement
  
  return (
    <OrganizationAnnouncementsBase showEditBack={true}>
      <Card>
        <Card.Header>
          <Card.Title>{cardTitle}</Card.Title>
        </Card.Header>
          <Formik
              initialValues={{ 
                displayPublic: organizationAnnouncement.displayPublic,
                displayShop: organizationAnnouncement.displayShop,
                displayBackend: organizationAnnouncement.displayBackend,
                title: organizationAnnouncement.title, 
                content: organizationAnnouncement.content,
                dateStart: organizationAnnouncement.dateStart,
                dateEnd: organizationAnnouncement.dateEnd,
                priority: organizationAnnouncement.priority,
              }}
              validationSchema={ANNOUNCEMENT_SCHEMA}
              onSubmit={(values, { setSubmitting }) => {
                let inputValues = {
                  id: announcementId,
                  displayPublic: values.displayPublic,
                  displayBackend: values.displayBackend,
                  displayShop: values.displayShop,
                  title: values.title, 
                  content: values.content,
                  dateStart: dateToLocalISO(values.dateStart),
                  dateEnd: dateToLocalISO(values.dateEnd),
                  priority: values.priority
                }

                updateAnnouncement({ variables: {
                  input: inputValues
                }, refetchQueries: [
                    {query: GET_ANNOUNCEMENTS_QUERY}
                ]})
                .then(({ data }) => {
                    console.log('got data', data)
                    history.push(returnUrl)
                    toast.success((t('organization.announcements.toast_edit_success')), {
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
              {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
                  <OrganizationAnnouncementForm 
                    isSubmitting={isSubmitting}
                    values={values}
                    errors={errors}
                    setFieldTouched={setFieldTouched}
                    setFieldValue={setFieldValue}
                    returnUrl={returnUrl}
                  />
              )}
          </Formik>
      </Card>
    </OrganizationAnnouncementsBase>
  )
}


export default withTranslation()(withRouter(OrganizationAnnouncementEdit))