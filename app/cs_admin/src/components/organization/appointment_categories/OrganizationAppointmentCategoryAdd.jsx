// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'


import { GET_APPOINTMENT_CATEGORIES_QUERY } from './queries'
import { APPOINTMENT_CATEGORY_SCHEMA } from './yupSchema'


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

import OrganizationAppointmentCategoryForm from "./OrganizationAppointmentCategoryForm"
import OrganizationMenu from "../OrganizationMenu"


const ADD_ORGANIZATION_APPOINTMENT_CATEGORY = gql`
  mutation CreateOrganizationAppointmentCategory($input: CreateOrganizationAppointmentCategoryInput!) {
    createOrganizationAppointmentCategory(input: $input) {
      organizationAppointmentCategory {
        id
        archived
        displayPublic
        name
      }
    }
  }
`

const return_url = "/organization/appointment_categories"

const OrganizationAppointmentCategoryAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('organization.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('organization.appointment_categories.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_ORGANIZATION_APPOINTMENT_CATEGORY} onCompleted={() => history.push(return_url)}> 
                {(addAppointmentCategory, { data }) => (
                    <Formik
                        initialValues={{ name: '', displayPublic: true }}
                        validationSchema={APPOINTMENT_CATEGORY_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addAppointmentCategory({ variables: {
                              input: {
                                name: values.name, 
                                displayPublic: values.displayPublic
                              }
                            }, refetchQueries: [
                                {query: GET_APPOINTMENT_CATEGORIES_QUERY, variables: {"archived": false }}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('organization.appointment_categories.toast_add_success')), {
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
                          <OrganizationAppointmentCategoryForm
                            isSubmitting={isSubmitting}
                            errors={errors}
                            values={values}
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
                                  resource="organizationappointmentcategory">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='appointment_categories'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationAppointmentCategoryAdd))