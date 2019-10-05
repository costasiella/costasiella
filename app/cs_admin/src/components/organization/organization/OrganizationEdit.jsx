// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ORGANIZATION_QUERY } from './queries'
import { ORGANIZATION_SCHEMA } from './yupSchema'
import OrganizationForm from './OrganizationForm'


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

import OrganizationMenu from "../OrganizationMenu"


const UPDATE_ORGANIZATION = gql`
  mutation UpdateOrganization($input: UpdateOrganizationInput!) {
    updateOrganization(input: $input) {
      organization {
        id
        name
      }
    }
  }
`


class OrganizationEdit extends Component {
  constructor(props) {
    super(props)
    console.log("Organization edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t('organization.title')}>
              <div className="page-options d-flex">
                <Link to={`/organization/documents/${id}`}>
                  <Button 
                    icon="briefcase"
                    className="mr-2"
                    color="secondary"
                  >
                    {t('general.documents')}
                  </Button>
                </Link>
              </div>
            </Page.Header>
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.organization.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_ORGANIZATION_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.organization;
                    console.log('query data')
                    console.log(data)

                    return (
                      
                      <Mutation mutation={UPDATE_ORGANIZATION}> 
                      {(updateLevel, { data }) => (
                          <Formik
                              initialValues={{ 
                                name: initialData.name, 
                                address: initialData.address,
                                phone: initialData.phone,
                                email: initialData.email,
                                registration: initialData.registration,
                                taxRegistration: initialData.taxRegistration,
                              }}
                              validationSchema={ORGANIZATION_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  updateLevel({ variables: {
                                    input: {
                                      id: match.params.id,
                                      name: values.name,
                                      address: values.address,
                                      phone: values.phone,
                                      email: values.email,
                                      registration: values.registration,
                                      taxRegistration: values.taxRegistration,
                                    }
                                  }, refetchQueries: [
                                      // {query: GET_LEVELS_QUERY, variables: {"archived": false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('organization.organization.toast_edit_success')), {
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
                                <OrganizationForm 
                                  isSubmitting={isSubmitting}
                                  values={values}
                                  errors={errors}
                                  setFieldTouched={setFieldTouched}
                                  setFieldValue={setFieldValue}
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
                <h5>{t("general.menu")}</h5>
                <OrganizationMenu active_link='organization'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationEdit))