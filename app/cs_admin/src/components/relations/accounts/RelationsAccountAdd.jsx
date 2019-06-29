// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'


import { GET_ACCOUNTS_QUERY } from './queries'
import { ACCOUNT_SCHEMA } from './yupSchema'


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

import { get_list_query_variables } from "./tools"
import RelationsAccountForm from "./RelationsAccountForm"
import RelationsMenu from '../RelationsMenu'


const ADD_ACCOUNT = gql`
  mutation CreateAccount($input:CreateAccountInput!) {
    createAccount(input: $input) {
      account {
        id
        firstName
        lastName
        email
      }
    }
  }
`

const return_url = "/relations/accounts"

const RelationsAccountAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('relations.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('relations.accounts.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_ACCOUNT} onCompleted={() => history.push(return_url)}> 
                {(addAccount, { data }) => (
                    <Formik
                        initialValues={{ name: '', code: '' }}
                        validationSchema={ACCOUNT_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addAccount({ variables: {
                              input: {
                                firstName: values.firstName,
                                lastName: values.lastName,
                                email: values.email
                              }
                            }, refetchQueries: [
                                {query: GET_ACCOUNTS_QUERY, variables: get_list_query_variables()}
                            ]})
                            .then(({ data }) => {
                                console.log('got data', data);
                                toast.success((t('relations.accounts.toast_add_success')), {
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
                            <RelationsAccountForm
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
                                  resource="account">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push(return_url)}>
                <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
              </Button>
            </HasPermissionWrapper>
            <RelationsMenu active_link='accounts'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
)

export default withTranslation()(withRouter(RelationsAccountAdd))