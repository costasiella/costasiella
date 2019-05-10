// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNTS_QUERY, GET_ACCOUNT_QUERY } from './queries'
import { ACCOUNT_SCHEMA } from './yupSchema'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import RelationsAccountProfileForm from "./RelationsAccountProfileForm"

// import OrganizationMenu from "../OrganizationMenu"


const UPDATE_ACCOUNT = gql`
  mutation UpdateAccount($input:UpdateAccountInput!) {
    updateAccount(input: $input) {
      account {
        id
        firstName
        lastName
        email
      }
    }
  }
`


class RelationsAccountProfile extends Component {
  constructor(props) {
    super(props)
    console.log("Organization profile props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/relations/accounts"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Query query={GET_ACCOUNT_QUERY} variables={{ id }} >
              {({ loading, error, data, refetch }) => {
                  // Loading
                  if (loading) return <p>{t('general.loading_with_dots')}</p>
                  // Error
                  if (error) {
                    console.log(error)
                    return <p>{t('general.error_sad_smiley')}</p>
                  }
                  
                  const initialData = data.account;
                  console.log('query data')
                  console.log(data)

                  return (
                    <div>
                      <Page.Header title={initialData.firstName + " " + initialData.lastName} />
                      <Grid.Row>
                        <Grid.Col md={9}>
                        <Card>
                          <Card.Header>
                            <Card.Title>{t('organization.accounts.profile')}</Card.Title>
                            {console.log(match.params.id)}
                          </Card.Header>
                        <Mutation mutation={UPDATE_ACCOUNT} onCompleted={() => history.push(return_url)}> 
                         {(updateAccount, { data }) => (
                          <Formik
                            initialValues={{ 
                              firstName: initialData.firstName, 
                              lastName: initialData.lastName, 
                              email: initialData.email 
                            }}
                            validationSchema={ACCOUNT_SCHEMA}
                            onSubmit={(values, { setSubmitting }) => {
                                console.log('submit values:')
                                console.log(values)

                                updateAccount({ variables: {
                                  input: {
                                    id: match.params.id,
                                    firstName: values.firstName,
                                    lastName: values.lastName,
                                    email: values.email
                                  }
                                }, refetchQueries: [
                                    {query: GET_ACCOUNTS_QUERY, variables: {"archived": false }}
                                ]})
                                .then(({ data }) => {
                                    console.log('got data', data)
                                    toast.success((t('organization.accounts.toast_edit_success')), {
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
                              <RelationsAccountProfileForm
                                isSubmitting={isSubmitting}
                                errors={errors}
                                values={values}
                                return_url={return_url}
                              />
                                // <FoForm>
                                //     <Card.Body>    
                                //         <Form.Group label={t('general.name')} >
                                //           <Field type="text" 
                                //                 name="name" 
                                //                 className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                //                 autoComplete="off" />
                                //           <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                //         </Form.Group>
                                //     </Card.Body>
                                //     <Card.Footer>
                                //         <Button 
                                //           className="pull-right"
                                //           color="primary"
                                //           disabled={isSubmitting}
                                //           type="submit"
                                //         >
                                //           {t('general.submit')}
                                //         </Button>
                                //         <Button
                                //           type="button" 
                                //           color="link" 
                                //           onClick={() => history.push(return_url)}
                                //         >
                                //             {t('general.cancel')}
                                //         </Button>
                                //     </Card.Footer>
                                // </FoForm>
                            )}
                          </Formik>
                        )}
                      </Mutation>
                    </Card>
                    </Grid.Col>                                    
                    <Grid.Col md={3}>
                      <HasPermissionWrapper permission="change"
                                            resource="organizationdiscovery">
                        <Button color="primary btn-block mb-6"
                                onClick={() => history.push(return_url)}>
                          <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                        </Button>
                      </HasPermissionWrapper>
                      {/* <OrganizationMenu active_link='discoveries'/> */}
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


export default withTranslation()(withRouter(RelationsAccountProfile))