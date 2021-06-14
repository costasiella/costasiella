// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { v4 } from "uuid"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { toast } from 'react-toastify'

import { GET_CLASSPASS_GROUP_PASSES_QUERY } from './queries'


import {
  Alert,
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Table,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationMenu from "../OrganizationMenu"


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

const DELETE_CARD_FROM_GROUP = gql`
  mutation DeleteCardFromGroup($input: DeleteOrganizationClasspassGroupClasspassInput!) {
    deleteOrganizationClasspassGroupClasspass(input:$input) {
      ok
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
                  </Card.Header>
                  <Query query={GET_CLASSPASS_GROUP_PASSES_QUERY} variables={{ id }} >
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

                      let group_passes = {}
                      if (group.organizationClasspasses.edges) {
                        group.organizationClasspasses.edges.map(({ node}) => (
                          group_passes[node.id] = true
                        ))
                      }

                      console.log("group_passes")
                      console.log(group_passes)

                      return (

                        (!passes.edges) ? "" : 
                          <Card.Body>
                            <Alert type="primary">
                              <strong>{t('general.group')}</strong> {group.name}
                            </Alert>
                            <Table>
                              <Table.Header>
                                <Table.Row key={v4()}>
                                  <Table.ColHeader>{t('')}</Table.ColHeader>
                                  <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                                  <Table.ColHeader>{t('')}</Table.ColHeader>
                                </Table.Row>
                              </Table.Header>
                              <Table.Body>
                                  {passes.edges.map(({ node }) => (
                                    <Table.Row key={v4()}>
                                      <Table.Col key={v4()}>
                                        {(node.id in group_passes) ? 
                                          <Icon name="check-circle" className="text-green" /> : <Icon name="x-circle" className="text-red" />
                                        }
                                      </Table.Col>
                                      <Table.Col key={v4()}>
                                        {node.name}
                                      </Table.Col>
                                      {console.log((node.id in group_passes))}
                                      {(!(node.id in group_passes)) ?
                                        // Add
                                        <Mutation mutation={ADD_CARD_TO_GROUP} key={v4()}>
                                          {(AddCardToGroup, { data }) => (
                                            <Table.Col className="text-right text-green" key={v4()}>
                                              <Button color="link"
                                                size="sm"
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
                                                <Icon prefix="fe" name="plus-circle" /> { ' ' }
                                                {t('general.add_to_group')} 
                                              </Button>
                                            </Table.Col>
                                          )}
                                        </Mutation> :
                                        // Delete
                                        <Mutation mutation={DELETE_CARD_FROM_GROUP} key={v4()}>
                                          {(DeleteCardFromGroup, { data }) => (
                                            <Table.Col className="text-right text-red" key={v4()}>
                                              <Button color="link"
                                                size="sm"
                                                title={t('general.delete_from_group')} 
                                                href=""
                                                onClick={() => {
                                                  console.log("clicked delete")
                                                  console.log(node.id)
                                                  let pass_id = node.id
                                                  let group_id = this.props.match.params.id
                                                  DeleteCardFromGroup({ variables: {
                                                    input: {
                                                      organizationClasspass: pass_id,
                                                      organizationClasspassGroup: group_id
                                                    }
                                              }, refetchQueries: [
                                                  {query: GET_CLASSPASS_GROUP_PASSES_QUERY, variables: {"id": group_id, "archived": false }}
                                              ]}).then(({ data }) => {
                                                console.log('got data', data);
                                                toast.success(t('general.deleted_from_group'), {
                                                  position: toast.POSITION.BOTTOM_RIGHT
                                                })
                                              }).catch((error) => {
                                                toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                                    position: toast.POSITION.BOTTOM_RIGHT
                                                  })
                                                console.log('there was an error sending the query', error);
                                              })
                                              }}>
                                                <Icon prefix="fe" name="minus-circle" /> { ' ' }
                                                {t('general.delete_from_group')}
                                              </Button>
                                            </Table.Col>
                                          )}
                                        </Mutation> 
                                        }
                                    </Table.Row>
                                  ))}
                              </Table.Body>
                            </Table>
                          </Card.Body>
                              
                     
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