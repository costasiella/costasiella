// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'


import {
  Page,
  Dimmer,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import { get_list_query_variables } from "./tools"


import { GET_SCHEDULE_EVENTS_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
// import { LEVEL_SCHEMA } from './yupSchema'
import ScheduleEventForm from './ScheduleEventForm'
import ScheduleEventsBase from './ScheduleEventsBase'
import formatISODateStr from '../../ui/ISODateString';


const CREATE_SCHEDULE_EVENT = gql`
  mutation CreateScheduleEvent($input:CreateScheduleEventInput!) {
    createScheduleEvent(input: $input) {
      scheduleEvent{
        id
      }
    }
  }
`

const return_url = "/organization/events"

function ScheduleEventAdd({ t, history }) {
  const returnUrl = "/schedule/events"
  const sidebarContent = <Link to={returnUrl}>
      <Button color="primary btn-block mb-6">
        <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
      </Button>
    </Link>

  const { loading, error, data } = useQuery(GET_INPUT_VALUES_QUERY)
  const [ createScheduleEvent ] = useMutation(CREATE_SCHEDULE_EVENT)

  if (loading) {
    return (
      <ScheduleEventsBase sidebarContent={sidebarContent}>
        <Card title={t("schedule.events.add")}>
          <Card.Body>
            <Dimmer loading={true} active={true} />
          </Card.Body>
        </Card>
      </ScheduleEventsBase>
    )
  }

  if (error) {
    return (
      <ScheduleEventsBase sidebarContent={sidebarContent}>
        <Card title={t("schedule.events.add")}>
          <Card.Body>
            {t("schedule.events.error_loading")}
          </Card.Body>
        </Card>
      </ScheduleEventsBase>
    )
  }

  console.log("CREATE SCHEDULE EVENT INPUT DATA")
  console.log(data)
  const inputData = data

  return (
    <ScheduleEventsBase sidebarContent={sidebarContent}>
      <Card title={t("schedule.events.add")}>
        <Formik
          initialValues={{ 
            displayPublic: true,
            displayShop: true,
            name: "",
            description: "",
          }}
          // validationSchema={SUBSCRIPTION_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
              console.log('submit values:')
              console.log(values)

              createScheduleEvent({ variables: {
                input: {
                  displayPublic: values.displayPublic,
                  displayShop: values.displayShop,
                  autoSentInfoMail: values.autoSentInfoMail,
                  organizationLocation: values.organizationLocation,
                  organizationLevel: values.organizationLevel,
                  name: values.name,
                  tagline: values.tagline,
                  preview: values.preview,
                  description: values.description,
                  teacher: values.teacher,
                  teacher2: values.teacher2,
                  infoMailContent: values.infoMailContent,
                }
              }, refetchQueries: [
                  { query: GET_SCHEDULE_EVENTS_QUERY, variables: get_list_query_variables() }
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  history.push(returnUrl)
                  toast.success((t('schedule.events.toast_add_success')), {
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
          {({ isSubmitting, setFieldValue, setFieldTouched, errors, values }) => (
            <ScheduleEventForm
              inputData={inputData}
              isSubmitting={isSubmitting}
              setFieldValue={setFieldValue}
              setFieldTouched={setFieldTouched}
              errors={errors}
              values={values}
              returnUrl={returnUrl}
            />
          )}
      </Formik>
      </Card>

    </ScheduleEventsBase>
    // <SiteWrapper>
    //   <div className="my-3 my-md-5">
    //     <Container>
    //       <Page.Header title={t('organization.title')} />
    //       <Grid.Row>
    //         <Grid.Col md={9}>
    //         <Card>
    //           <Card.Header>
    //             <Card.Title>{t('organization.levels.title_add')}</Card.Title>
    //           </Card.Header>
    //           <Mutation mutation={ADD_LEVEL} onCompleted={() => history.push(return_url)}> 
    //               {(addLocation, { data }) => (
    //                   <Formik
    //                       initialValues={{ name: '', code: '' }}
    //                       validationSchema={LEVEL_SCHEMA}
    //                       onSubmit={(values, { setSubmitting }) => {
    //                           addLocation({ variables: {
    //                             input: {
    //                               name: values.name, 
    //                             }
    //                           }, refetchQueries: [
    //                               {query: GET_LEVELS_QUERY, variables: {"archived": false }}
    //                           ]})
    //                           .then(({ data }) => {
    //                               console.log('got data', data);
    //                               toast.success((t('organization.levels.toast_add_success')), {
    //                                   position: toast.POSITION.BOTTOM_RIGHT
    //                                 })
    //                             }).catch((error) => {
    //                               toast.error((t('general.toast_server_error')) + ': ' +  error, {
    //                                   position: toast.POSITION.BOTTOM_RIGHT
    //                                 })
    //                               console.log('there was an error sending the query', error)
    //                               setSubmitting(false)
    //                             })
    //                       }}
    //                       >
    //                       {({ isSubmitting, errors }) => (
    //                           <OrganizationLevelForm 
    //                             isSubmitting={isSubmitting}
    //                             errors={errors}
    //                             return_url={return_url}
    //                           />
    //                       )}
    //                   </Formik>
    //               )}
    //               </Mutation>
    //         </Card>
    //         </Grid.Col>
    //         <Grid.Col md={3}>
    //           <HasPermissionWrapper permission="add"
    //                                 resource="organizationlevel">
    //             <Button color="primary btn-block mb-6"
    //                     onClick={() => history.push(return_url)}>
    //               <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
    //             </Button>
    //           </HasPermissionWrapper>
    //           <OrganizationMenu active_link='levels'/>
    //         </Grid.Col>
    //       </Grid.Row>
    //     </Container>
    //   </div>
    // </SiteWrapper>
  )
}

export default withTranslation()(withRouter(ScheduleEventAdd))