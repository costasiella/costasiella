// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"


import { GET_INPUT_VALUES_QUERY } from './queries'
// import { LEVEL_SCHEMA } from './yupSchema'
import ScheduleEventForm from './ScheduleEventForm'
import ScheduleEventsBase from './ScheduleEventsBase'


const ADD_EVENT = gql`
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
  const sidebarContent = <Link to="/schedule/events">
      <Button color="primary btn-block mb-6"
              onClick={() => history.push(return_url)}>
        <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
      </Button>
    </Link>

  return (
    <ScheduleEventsBase sidebarContent={sidebarContent}>
      hello world
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