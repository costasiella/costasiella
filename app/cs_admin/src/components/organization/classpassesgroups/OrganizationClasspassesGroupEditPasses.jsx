// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { v4 } from "uuid"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_CLASSPASS_GROUP_PASSES_QUERY } from './queries'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
  Table,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationMenu from "../OrganizationMenu"

//TODO: Add and delete group pass mutations
const ADD_CARD_TO_GROUP = gql`
  mutation AddCardToGroup($input: CreateOrganizationClasspassGroupClasspassInput!) {
    createOrganizationClasspassGroupClasspass(input:$input) {
      organizationClasspassGroupClasspass {
        id
        organizationClasspass {
          id
          name
        }
        organizationClasspassGroup {
          id
          name
        }
      }
    }
  }
`


class OrganizationClasspassGroupEditPasses extends Component {
  constructor(props) {
    super(props)
    console.log("Organization classpassgroup edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id 
    const return_url = "/organization/classpasses/groups"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="Organization" />
            <Grid.Row>
              <Grid.Col md={9}>
                <Card>
                  <Card.Header>
                    <Card.Title>{t('organization.classpass_group_classpasses.title_edit')}</Card.Title>
                    {console.log(match.params.id)}
                  </Card.Header>
                  <Query query={GET_CLASSPASS_GROUP_PASSES_QUERY} variables={{ id, archived: false }} >
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
                      const passes = data.organizationClasspasses
                      const group = data.organizationClasspassGroup

                      let group_passes = []
                      if (group.organizationClasspasses.edges) {
                        group.organizationClasspasses.edges.map(({ node}) => (
                          group_passes.push(node.id)
                        ))
                      }

                      console.log("group_passes")
                      console.log(group_passes)

                      return (

                        (!passes.edges) ? "" : 
                          <Card.Body>
                            <Table>
                              <Table.Header>
                                <Table.Row key={v4()}>
                                  <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                                </Table.Row>
                              </Table.Header>
                              <Table.Body>
                                  {passes.edges.map(({ node }) => (
                                    <Table.Row key={v4()}>
                                      <Table.Col key={v4()}>
                                        {node.name}
                                      </Table.Col>
                                      {(!node.id in group_passes) ?
                                        <Mutation mutation={ADD_CARD_TO_GROUP} key={v4()}>
                                          {(AddCardToGroup, { data }) => (
                                            <Table.Col className="text-right" key={v4()}>
                                              <button className="icon btn btn-link btn-sm" 
                                                title={t('general.add_to_group')} 
                                                href=""
                                                onClick={() => {
                                                  console.log("clicked add")
                                                  let pass_id = node.id
                                                  let group_id = this.props.match.params.id
                                                  AddCardToGroup({ variables: {
                                                    input: {
                                                      organizationClasspass: pass_id,
                                                      organizationClasspassGroup: group_id
                                                    }
                                              }, refetchQueries: [
                                                  {query: GET_CLASSPASS_GROUP_PASSES_QUERY, variables: {"id": group_id, "archived": false }}
                                              ]}).then(({ data }) => {
                                                console.log('got data', data);
                                                toast.success(t('general.added_to_group'), {
                                                  position: toast.POSITION.BOTTOM_RIGHT
                                                })
                                              }).catch((error) => {
                                                toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                                    position: toast.POSITION.BOTTOM_RIGHT
                                                  })
                                                console.log('there was an error sending the query', error);
                                              })
                                              }}>
                                                <Icon prefix="fa" name="plus-circle" />
                                              </button>
                                            </Table.Col>
                                          )}
                                        </Mutation> :
                                        "delete" 
                                        }
                                    </Table.Row>
                                  ))}
                              </Table.Body>
                            </Table>
                          </Card.Body>
                              
                        
                        // <Mutation mutation={UPDATE_CLASSPASS_GROUP} onCompleted={() => history.push(return_url)}> 
                        // {(updateClasspassGroup, { data }) => (
                        //     <Formik
                        //         initialValues={{ 
                        //           name: initialData.name, 
                        //         }}
                        //         validationSchema={CLASSPASS_GROUP_SCHEMA}
                        //         onSubmit={(values, { setSubmitting }) => {
                        //             console.log('submit values:')
                        //             console.log(values)

                        //             updateClasspassGroup({ variables: {
                        //               input: {
                        //                 id: match.params.id,
                        //                 name: values.name,
                        //               }
                        //             }, refetchQueries: [
                        //                 {query: GET_CLASSPASS_GROUPS_QUERY, variables: {"archived": false }}
                        //             ]})
                        //             .then(({ data }) => {
                        //                 console.log('got data', data)
                        //                 toast.success((t('organization.classpass_groups.toast_edit_success')), {
                        //                     position: toast.POSITION.BOTTOM_RIGHT
                        //                   })
                        //               }).catch((error) => {
                        //                 toast.error((t('general.toast_server_error')) + ': ' +  error, {
                        //                     position: toast.POSITION.BOTTOM_RIGHT
                        //                   })
                        //                 console.log('there was an error sending the query', error)
                        //                 setSubmitting(false)
                        //               })
                        //         }}
                        //         >
                        //         {({ isSubmitting, errors, values }) => (
                        //             <FoForm>
                        //                 <Card.Body>    
                        //                     <Form.Group label={t('general.name')} >
                        //                       <Field type="text" 
                        //                             name="name" 
                        //                             className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                        //                             autoComplete="off" />
                        //                       <ErrorMessage name="name" component="span" className="invalid-feedback" />
                        //                     </Form.Group>
                        //                 </Card.Body>
                        //                 <Card.Footer>
                        //                     <Button 
                        //                       className="pull-right"
                        //                       color="primary"
                        //                       disabled={isSubmitting}
                        //                       type="submit"
                        //                     >
                        //                       {t('general.submit')}
                        //                     </Button>
                        //                     <Button
                        //                       type="button" 
                        //                       color="link" 
                        //                       onClick={() => history.push(return_url)}
                        //                     >
                        //                         {t('general.cancel')}
                        //                     </Button>
                        //                 </Card.Footer>
                        //             </FoForm>
                        //         )}
                        //     </Formik>
                        // )}
                        // </Mutation>
                        )}}
                  </Query>
                </Card>
              </Grid.Col>
              <Grid.Col md={3}>
                <HasPermissionWrapper permission="change"
                                      resource="organizationclasspassgroup">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <OrganizationMenu active_link=''/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationClasspassGroupEditPasses))