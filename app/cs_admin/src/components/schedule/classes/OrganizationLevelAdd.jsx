// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_LEVELS_QUERY } from './queries'
import { LEVEL_SCHEMA } from './yupSchema'
import OrganizationLevelForm from './OrganizationLevelForm'


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

import OrganizationMenu from '../OrganizationMenu'


const ADD_LEVEL = gql`
  mutation CreateOrganizationLevel($input:CreateOrganizationLevelInput!) {
    createOrganizationLevel(input: $input) {
      organizationLevel{
        id
        archived
        name
      }
    }
  }
`

const return_url = "/organization/levels"

const OrganizationLevelAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('organization.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('organization.levels.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_LEVEL} onCompleted={() => history.push(return_url)}> 
                {(addLocation, { data }) => (
                    <Formik
                        initialValues={{ name: '', code: '' }}
                        validationSchema={LEVEL_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addLocation({ variables: {
                              input: {
                                name: values.name, 
                              }
                            }, refetchQueries: [
                                {query: GET_LEVELS_QUERY, variables: {"archived": false }}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('organization.levels.toast_add_success')), {
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
          </Card>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
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
)

export default withTranslation()(withRouter(OrganizationLevelAdd))