// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SCHEDULE_ITEM_PRICES_QUERY, GET_SINGLE_SCHEDULE_ITEM_PRICE_QUERY } from './queries'
import { SCHEDULE_CLASS_TEACHER_SCHEMA } from './yupSchema'
import ScheduleClassPriceForm from './ScheduleClassPriceForm'
import { dateToLocalISO } from '../../../../../tools/date_tools'


import SiteWrapper from "../../../../SiteWrapper"

import ClassEditBase from "../ClassEditBase"
import ScheduleClassPriceBack from "./ScheduleClassPriceBack"


const UPDATE_SCHEDULE_ITEM_PRICE = gql`
  mutation UpdateScheduleItemPrice($input: UpdateScheduleItemPriceInput!) {
    updateScheduleItemPrice(input:$input) {
      scheduleItemPrice {
        id
      } 
    }
  }
`

function ScheduleClassPriceEdit({ t, history, match }) {
  const classId = match.params.class_id
  const return_url = "/schedule/classes/all/prices/" + classId
  const id = match.params.id
  const { loading: queryLoading, error: queryError, data, } = useQuery(GET_SINGLE_SCHEDULE_ITEM_PRICE_QUERY, {
    variables: {
      id: id
    }
  })
  const [editScheduleClassPrice, { mutationData, mutationLoading, mutationError, onCompleted }] = useMutation(UPDATE_SCHEDULE_ITEM_PRICE, {
    onCompleted: () => history.push(return_url)
  })


  if (queryLoading) return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <p>{t('general.loading_with_dots')}</p>
      </div>
    </SiteWrapper>
  )
  // Error
  if (queryError) {
    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          console.log(error)
          return <p>{t('general.error_sad_smiley')}</p>
        </div>
      </SiteWrapper>
    )
  }


  console.log('query data')
  console.log(data)
  const inputData = data

  let initialOrganizationClasspassDropin
  let initialOrganizationClasspassTrial

  if (inputData.scheduleItemPrice.organizationClasspassDropin) {
    initialOrganizationClasspassDropin = inputData.scheduleItemPrice.organizationClasspassDropin.id
  }

  if (inputData.scheduleItemPrice.organizationClasspassTrial) {
    initialOrganizationClasspassTrial = inputData.scheduleItemPrice.organizationClasspassTrial.id
  }

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <ClassEditBase 
          card_title={t('schedule.classes.prices.title_edit')}
          menu_active_link="prices"
          sidebar_button={<ScheduleClassPriceBack classId={match.params.class_id} />}
        >
          <Formik
            initialValues={{ 
              dateStart: inputData.scheduleItemPrice.dateStart,
              dateEnd: inputData.scheduleItemPrice.dateEnd,
              organizationClasspassDropin: initialOrganizationClasspassDropin,
              organizationClasspassTrial: initialOrganizationClasspassTrial,
            }}
            // validationSchema={SCHEDULE_CLASS_TEACHER_SCHEMA}
            onSubmit={(values, { setSubmitting }) => {

                let dateEnd
                if (values.dateEnd) {
                  dateEnd = dateToLocalISO(values.dateEnd)
                } else {
                  dateEnd = values.dateEnd
                }

                editScheduleClassPrice({ variables: {
                  input: {
                    id: id,
                    dateStart: dateToLocalISO(values.dateStart),
                    dateEnd: dateEnd,
                    organizationClasspassDropin: values.organizationClasspassDropin,
                    organizationClasspassTrial: values.organizationClasspassTrial
                  }
                }, refetchQueries: [
                    {query: GET_SCHEDULE_ITEM_PRICES_QUERY, variables: { scheduleItem: match.params.class_id }},
                    // {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }},
                ]})
                .then(({ data }) => {
                    console.log('got data', data);
                    toast.success((t('schedule.classes.prices.toast_edit_success')), {
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
              <ScheduleClassPriceForm
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
        </ClassEditBase>
      </div>
    </SiteWrapper>
  )
}


// class ScheduleClassTeacherEdit extends Component {
//   constructor(props) {
//     super(props)
//     console.log("Schedule class teacher edit props:")
//     console.log(props)
//   }

//   render() {
//     const t = this.props.t
//     const match = this.props.match
//     const history = this.props.history
//     const id = match.params.id
//     const class_id = match.params.class_id
//     const return_url = "/schedule/classes/all/teachers/" + class_id

//     return (
//       <SiteWrapper>
//         <div className="my-3 my-md-5">
//           <Query query={GET_SINGLE_SCHEDULE_CLASS_TEACHERS_QUERY} variables={{id: id}}>
//             {({ loading, error, data, refetch }) => {
//               // Loading
//               if (loading) return <p>{t('general.loading_with_dots')}</p>
//               // Error
//               if (error) {
//                 console.log(error)
//                 return <p>{t('general.error_sad_smiley')}</p>
//               }
    
//               console.log('query data')
//               console.log(data)
//               const inputData = data
//               const initialData = data.scheduleItemTeacher

//               let initialAccount2 = ""
//               if (initialData.account2) {
//                 initialAccount2 =  initialData.account2.id
//               } 
    
//               return (
//                 <ClassEditBase 
//                   card_title={t('schedule.classes.teachers.title_edit')}
//                   menu_active_link="teachers"
//                   sidebar_button={<ScheduleClassTeacherBack classId={class_id} />}
//                 >
//                   <Mutation mutation={UPDATE_SCHEDULE_CLASS_TEACHER} onCompleted={() => history.push(return_url)}> 
//                     {(addScheduleClassTeacher, { data }) => (
//                         <Formik
//                             initialValues={{  
//                               dateStart: initialData.dateStart,
//                               dateEnd: initialData.dateEnd,
//                               account: initialData.account.id,
//                               role: initialData.role,
//                               account2: initialAccount2,
//                               role2: initialData.role2,
//                             }}
//                             validationSchema={SCHEDULE_CLASS_TEACHER_SCHEMA}
//                             onSubmit={(values, { setSubmitting }) => {
    
//                                 let dateEnd
//                                 if (values.dateEnd) {
//                                   dateEnd = dateToLocalISO(values.dateEnd)
//                                 } else {
//                                   dateEnd = values.dateEnd
//                                 }
    
//                                 addScheduleClassTeacher({ variables: {
//                                   input: {
//                                     id: match.params.id,
//                                     account: values.account,
//                                     role: values.role,
//                                     account2: values.account2,
//                                     role2: values.role2,
//                                     dateStart: dateToLocalISO(values.dateStart),
//                                     dateEnd: dateEnd
//                                   }
//                                 }, refetchQueries: [
//                                     {query: GET_SCHEDULE_CLASS_TEACHERS_QUERY, variables: { scheduleItem: match.params.class_id }},
//                                     // {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }},
//                                 ]})
//                                 .then(({ data }) => {
//                                     console.log('got data', data);
//                                     toast.success((t('schedule.classes.teachers.toast_edit_success')), {
//                                         position: toast.POSITION.BOTTOM_RIGHT
//                                       })
//                                   }).catch((error) => {
//                                     toast.error((t('general.toast_server_error')) + ': ' +  error, {
//                                         position: toast.POSITION.BOTTOM_RIGHT
//                                       })
//                                     console.log('there was an error sending the query', error)
//                                     setSubmitting(false)
//                                   })
//                             }}
//                             >
//                             {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
//                               <ScheduleClassTeacherForm
//                                 inputData={inputData}
//                                 isSubmitting={isSubmitting}
//                                 setFieldTouched={setFieldTouched}
//                                 setFieldValue={setFieldValue}
//                                 errors={errors}
//                                 values={values}
//                                 return_url={return_url}
//                               >
//                                 {console.log(errors)}
//                               </ScheduleClassTeacherForm>
//                             )}
//                         </Formik>
//                     )}
//                   </Mutation>
//                 </ClassEditBase>
//               )
//             }}
//           </Query>
//         </div>
//       </SiteWrapper>
//     )
//   }
// }


export default withTranslation()(withRouter(ScheduleClassPriceEdit))