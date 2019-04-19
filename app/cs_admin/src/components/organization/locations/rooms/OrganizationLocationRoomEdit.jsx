// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_LOCATION_ROOMS_QUERY, GET_LOCATION_ROOM_QUERY } from './queries'
import { LOCATION_ROOM_SCHEMA } from './yupSchema'
import OrganizationLocationRoomForm from './OrganizationLocationRoomForm'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationMenu from "../../OrganizationMenu"


const UPDATE_LOCATION_ROOM = gql`
  mutation UpdateOrganizationLocationRoom($input: UpdateOrganizationLocationRoomInput!) {
    updateOrganizationLocationRoom(input: $input) {
      organizationLocationRoom {
        id
        organizationLocation {
          id
          name
        }
        name
        displayPublic
      }
    }
  }
`


class OrganizationLocationRoomEdit extends Component {
  constructor(props) {
    super(props)
    console.log("Organization location room edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const location_id = match.params.location_id
    const return_url = "/organization/locations/rooms/" + location_id

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.location_rooms.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_LOCATION_ROOM_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.organizationLocationRoom;
                    console.log('query data')
                    console.log(data)

                    return (
                      
                      <Mutation mutation={UPDATE_LOCATION_ROOM} onCompleted={() => history.push(return_url)}> 
                      {(updateLocation, { data }) => (
                          <Formik
                              initialValues={{ 
                                name: initialData.name, 
                                displayPublic: initialData.displayPublic 
                              }}
                              validationSchema={LOCATION_ROOM_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  updateLocation({ variables: {
                                    input: {
                                      id: match.params.id,
                                      name: values.name,
                                      displayPublic: values.displayPublic 
                                    }
                                  }, refetchQueries: [
                                    {query: GET_LOCATION_ROOMS_QUERY,
                                      variables: {"archived": false, "organizationLocation": match.params.location_id }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.location_rooms.toast_edit_success')), {
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
                              {({ isSubmitting, errors, values }) => (
                                <OrganizationLocationRoomForm
                                isSubmitting={isSubmitting}
                                errors={errors}
                                values={values}
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
                                      resource="organizationlocationroom">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <OrganizationMenu active_link='locations'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationLocationRoomEdit))