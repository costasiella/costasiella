// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'

import { GET_SCHEDULE_EVENTS_QUERY, GET_SCHEDULE_EVENT_QUERY } from './queries'
import { LEVEL_SCHEMA } from './yupSchema'
import OrganizationLevelForm from './OrganizationLevelForm'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import ScheduleEventsBase from "./ScheduleEventsBase"


const UPDATE_SCHEDULE_EVENT = gql`
  mutation UpdateScheduleEvent($input: UpdateScheduleEventInput!) {
    updateScheduleEvent(input: $input) {
      scheduleEvent {
        id
        name
      }
    }
  }
`

function ScheduleEventEdit({t, match, history}) {
  const id = match.params.id
  const returnUrl = "/schedule/events"

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_QUERY, {
    variables: { id: id }
  })
  const [ updateScheduleEvent ] = useMutation(UPDATE_SCHEDULE_EVENT)

  const sidebarContent = <Link to={returnUrl}>
      <Button color="primary btn-block mb-6">
        <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
      </Button>
    </Link>

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


}


class ScheduleEventEdit extends Component {
  constructor(props) {
    super(props)
    console.log("Organization level edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/organization/levels"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.levels.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_LEVEL_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.organizationLevel;
                    console.log('query data')
                    console.log(data)

                    return (
                      
                      <Mutation mutation={UPDATE_LEVEL} onCompleted={() => history.push(return_url)}> 
                      {(updateLevel, { data }) => (
                          <Formik
                              initialValues={{ 
                                name: initialData.name, 
                              }}
                              validationSchema={LEVEL_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  updateLevel({ variables: {
                                    input: {
                                      id: match.params.id,
                                      name: values.name,
                                    }
                                  }, refetchQueries: [
                                      {query: GET_LEVELS_QUERY, variables: {"archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.levels.toast_edit_success')), {
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
                              {({ isSubmitting, errors }) => (
                                <OrganizationLevelForm 
                                  isSubmitting={isSubmitting}
                                  errors={errors}
                                  return_url={return_url}
                                />
                              )}
                          </Formik>
                      )}
                      </Mutation>
                      )}}
                </Query>
              </Card>
              </Grid.Col>
              <Grid.Col md={3}>
                <HasPermissionWrapper permission="change"
                                      resource="organizationlevel">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <OrganizationMenu active_link='levels'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(ScheduleEventEdit))