// @flow

import React from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, UPDATE_SCHEDULE_CLASS_WEEKLY_OTC } from './queries'
// import { SCHEDULE_CLASS_TEACHER_SCHEMA } from './yupSchema'
import ScheduleClassEditForm from './ScheduleClassEditForm'
import { dateToLocalISO } from '../../../../../tools/date_tools'


import SiteWrapper from "../../../../SiteWrapper"

import ClassEditBase from "../ClassEditBase"
import ScheduleClassTeacherBack from "./ScheduleClassTeacherBack"



function ScheduleClassEdit({ t, match, history }) {
  const schedule_item_id = match.params.class_id
  const class_date = match.params.date
  const query_vars = {
    scheduleItem: schedule_item_id,
    date: class_date
  }

  const [ updateScheduleClassWeeklyOTC, { date } ] = useMutation(UPDATE_SCHEDULE_CLASS_WEEKLY_OTC)

  const { queryLoading, queryError, queryData } = useQuery(GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, {
    variables: query_vars,
  })

  if (queryLoading) return <p>{t('general.loading_with_dots')}</p>
  // Error
  if (queryError) {
    console.log(queryAttendanceError)
    return <p>{t('general.error_sad_smiley')}</p>
  }

  const inputData = queryData
  let initialData
  let initialValues = {}
  if (queryData.edges) {
    initialData = queryData.edges[0]

    if (initialData.organizationLocationRoom) {
      initialValues.organizationLocationRoom = initialData.organizationLocationRoom.id
    }
    if (initialData.organizationClasstype) {
      initialValues.organizationClasstype = initialData.organizationClasstype.id
    }
    if (initialData.organizationLevel) {
      initialValues.organizationLevel = initialData.organizationLevel.id
    }
    InitialValues.timeStart = initialData.timeStart
    InitialValues.timeEnd = initialData.timeEnd
  } else {
    initialValues.organizationLocationRoom = ""
    initialValues.organizationClasstype = ""
    initialValues.organizationLevel = ""
    initialValues.timeStart = ""
    initialValues.timeEnd = ""
  }

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">


            return (
              <ClassEditBase 
                card_title={t('schedule.classes.teachers.title_edit')}
                menu_active_link="teachers"
                sidebar_button={<ScheduleClassTeacherBack classId={class_id} />}
              >
                    <Formik
                      initialValues={initialValues}
                      // validationSchema={SCHEDULE_CLASS_TEACHER_SCHEMA}
                      onSubmit={(values, { setSubmitting }) => {

                          // let dateEnd
                          // if (values.dateEnd) {
                          //   dateEnd = dateToLocalISO(values.dateEnd)
                          // } else {
                          //   dateEnd = values.dateEnd
                          // }

                          updateScheduleClassWeeklyOTC({ variables: {
                            input: {
                              scheduleItem: schedule_item_id,
                              date: class_date,
                              organizationLocationRoom: values.organizationLocationRoom,
                              organizationClasstype: values.organizationClasstype,
                              organizationLevel: values.organizationLevel
                            }
                          }, refetchQueries: [
                              {query: GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, variables: query_vars},
                              // {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }},
                          ]})
                          .then(({ data }) => {
                              console.log('got data', data);
                              toast.success((t('schedule.classes.teachers.toast_edit_success')), {
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
                        <ScheduleClassEditForm
                          inputData={inputData}
                          isSubmitting={isSubmitting}
                          setFieldTouched={setFieldTouched}
                          setFieldValue={setFieldValue}
                          errors={errors}
                          values={values}
                          return_url={return_url}
                        >
                          {console.log(errors)}
                        </ScheduleClassEditForm>
                      )}
                  </Formik>
              </ClassEditBase>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(ScheduleClassEdit))