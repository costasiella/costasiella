// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_SCHEDULE_CLASS_TEACHERS_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { SCHEDULE_CLASS_TEACHER_SCHEMA } from './yupSchema'
import ScheduleClassTeacherForm from './ScheduleClassTeacherForm'
import { dateToLocalISO } from '../../../../../tools/date_tools'

import SiteWrapper from "../../../../SiteWrapper"

import ClassEditBase from "../ClassEditBase"
import ScheduleClassTeacherBack from "./ScheduleClassTeacherBack"


const ADD_SCHEDULE_CLASS_TEACHER = gql`
  mutation CreateScheduleItemTeacher($input:CreateScheduleItemTeacherInput!) {
    createScheduleItemTeacher(input:$input) {
      scheduleItemTeacher {
        id
      } 
    }
  }
`

const return_url = "/schedule/classes/all/teachers/"

const ScheduleClassTeacherAdd = ({ t, history, match }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Query query={GET_INPUT_VALUES_QUERY} >
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
            <ClassEditBase 
              card_title={t('schedule.classes.teachers.title_add')}
              menu_active_link="teachers"
              sidebar_button={<ScheduleClassTeacherBack classId={match.params.class_id} />}
            >
              <Mutation mutation={ADD_SCHEDULE_CLASS_TEACHER} onCompleted={() => history.push(return_url + match.params.class_id)}> 
                {(addScheduleClassTeacher, { data }) => (
                    <Formik
                        initialValues={{ 
                          price: "", 
                          dateStart: new Date() ,
                          account: "",
                          role: "",
                          account2: "",
                          role2: "",
                        }}
                        validationSchema={SCHEDULE_CLASS_TEACHER_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {

                            let dateEnd
                            if (values.dateEnd) {
                              dateEnd = dateToLocalISO(values.dateEnd)
                            } else {
                              dateEnd = values.dateEnd
                            }

                            addScheduleClassTeacher({ variables: {
                              input: {
                                scheduleItem: match.params.class_id,
                                account: values.account,
                                role: values.role,
                                account2: values.account2,
                                role2: values.role2,
                                dateStart: dateToLocalISO(values.dateStart),
                                dateEnd: dateEnd
                              }
                            }, refetchQueries: [
                                {query: GET_SCHEDULE_CLASS_TEACHERS_QUERY, variables: { scheduleItem: match.params.class_id }},
                                // {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }},
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('schedule.classes.teachers.toast_add_success')), {
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
                          <ScheduleClassTeacherForm
                            inputData={inputData}
                            isSubmitting={isSubmitting}
                            setFieldTouched={setFieldTouched}
                            setFieldValue={setFieldValue}
                            errors={errors}
                            values={values}
                            return_url={return_url + match.params.class_id}
                          />
                        )}
                    </Formik>
                )}
              </Mutation>
            </ClassEditBase>
          )
        }}
      </Query>
    </div>
  </SiteWrapper>
)


export default withTranslation()(withRouter(ScheduleClassTeacherAdd))