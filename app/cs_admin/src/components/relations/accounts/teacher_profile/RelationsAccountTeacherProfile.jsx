// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_TEACHER_PROFILE_QUERY } from './queries'
import { ACCOUNT_TEACHER_PROFILE_SCHEMA } from './yupSchema'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react"
import SiteWrapper from "../../../SiteWrapper"
import ProfileCardSmall from "../../../ui/ProfileCardSmall"

import RelationsAccountsBack from "../RelationsAccountsBack"
import RelationsAccountProfileForm from "./RelationsAccountTeacherProfileForm"

import ProfileMenu from "../ProfileMenu"


const UPDATE_ACCOUNT_TEACHER_PROFILE = gql`
  mutation UpdateAccountTeacherProfile($input:UpdateAccountTeacherProfileInput!) {
    updateAccountTeacherProfile(input: $input) {
      accountTeacherProfile {
        id
      }
    }
  }
`


class RelationsAccountTeacherProfile extends Component {
  constructor(props) {
    super(props)
    console.log("Organization profile props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const account_id = match.params.account_id
    console.log(account_id)

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Query query={GET_ACCOUNT_TEACHER_PROFILE_QUERY} variables={{ id: account_id }} >
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
                  
                  const account = data.account
                  const initialData = data.accountTeacherProfiles.edges[0].node
                  console.log(initialData)


                  return (
                    <div>
                      <Page.Header title={account.firstName + " " + account.lastName}>
                        <RelationsAccountsBack />
                      </Page.Header>
                      <Grid.Row>
                        <Grid.Col md={9}>
                        <Card>
                          <Card.Header>
                            <Card.Title>{t('relations.account.teacher_profile.title')}</Card.Title>
                            {console.log(match.params.account_id)}
                          </Card.Header>
                        <Mutation mutation={UPDATE_ACCOUNT_TEACHER_PROFILE}> 
                         {(updateAccountTeacherProfile, { data }) => (
                          <Formik
                            initialValues={{ 
                              classes: initialData.classes, 
                              appointments: initialData.appointments, 
                              events: initialData.events, 
                              role: initialData.role, 
                              education: initialData.education, 
                              bio: initialData.bio,
                              urlBio: initialData.urlBio,
                              urlWebsite: initialData.urlWebsite,
                            }}
                            validationSchema={ACCOUNT_TEACHER_PROFILE_SCHEMA}
                            onSubmit={(values, { setSubmitting }) => {
                                console.log('submit values:')
                                console.log(values)

                                updateAccountTeacherProfile({ variables: {
                                  input: {
                                    account: initialData.account.id,
                                    classes: values.classes, 
                                    appointments: values.appointments, 
                                    events: values.events, 
                                    role: values.role, 
                                    education: values.education, 
                                    bio: values.bio,
                                    urlBio: values.urlBio,
                                    urlWebsite: values.urlWebsite,
                                  }
                                }, refetchQueries: [
                                    // Refresh local cached results for this account teacher profile
                                    {query: GET_ACCOUNT_TEACHER_PROFILE_QUERY, variables: {id: account_id}}
                                ]})
                                .then(({ data }) => {
                                    console.log('got data', data)
                                    toast.success((t('relations.account.teacher_profile.toast_edit_success')), {
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
                              <RelationsAccountProfileForm
                                isSubmitting={isSubmitting}
                                setFieldTouched={setFieldTouched}
                                setFieldValue={setFieldValue}
                                errors={errors}
                                values={values}
                              />
                            )}
                          </Formik>
                        )}
                      </Mutation>
                    </Card>
                    </Grid.Col>                                    
                    <Grid.Col md={3}>
                      <ProfileCardSmall user={account}/>
                      <ProfileMenu 
                        active_link='teacher_profile'
                        account_id={account_id}
                      /> 
                    </Grid.Col>
                  </Grid.Row>
                </div>
              )}}
            </Query>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(RelationsAccountTeacherProfile))