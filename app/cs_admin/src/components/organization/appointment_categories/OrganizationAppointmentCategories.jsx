// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Badge,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../general/ContentCard"
import OrganizationMenu from "../OrganizationMenu"

import { GET_APPOINTMENT_CATEGORIES_QUERY } from "./queries"

const ARCHIVE_APPOINTMENT_CATEGORY = gql`
  mutation ArchiveOrganizationAppointmentCategory($input: ArchiveOrganizationAppointmentCategoryInput!) {
    archiveOrganizationAppointmentCategory(input: $input) {
      organizationAppointmentCategory {
        id
        archived
      }
    }
  }
`

const OrganizationAppointmentCategories = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('organization.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_APPOINTMENT_CATEGORIES_QUERY} variables={{ archived }}>
             {({ loading, error, data: {organizationAppointmentCategories: appointment_categories}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('organization.appointment_categories.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('organization.appointment_categories.title')}>
                    <p>{t('organization.appointment_categories.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  <Button color={(!archived) ? 'primary': 'secondary'}  
                          size="sm"
                          onClick={() => {archived=false; refetch({archived});}}>
                    {t('general.current')}
                  </Button>
                  <Button color={(archived) ? 'primary': 'secondary'} 
                          size="sm" 
                          className="ml-2" 
                          onClick={() => {archived=true; refetch({archived});}}>
                    {t('general.archive')}
                  </Button>
                </Card.Options>
                
                // Empty list
                if (!appointment_categories.edges.length) { return (
                  <ContentCard cardTitle={t('organization.appointment_categories.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('organization.appointment_categories.empty_list') : t("organization.appointment_categories.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('organization.appointment_categories.title')}
                               headerContent={headerOptions}
                               pageInfo={appointment_categories.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: appointment_categories.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.organizationAppointmentCategories.edges
                                    const pageInfo = fetchMoreResult.organizationAppointmentCategories.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new appointment_categories at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          organizationAppointmentCategories: {
                                            __typename: previousResult.organizationAppointmentCategories.__typename,
                                            edges: [ ...previousResult.organizationAppointmentCategories.edges, ...newEdges ],
                                            pageInfo
                                          }
                                        }
                                      : previousResult
                                  }
                                })
                              }} >
                    <Table>
                          <Table.Header>
                            <Table.Row key={v4()}>
                              <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.public')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {appointment_categories.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {node.name}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {(node.displayPublic) ? 
                                      <Badge color="success">{t('general.yes')}</Badge>: 
                                      <Badge color="danger">{t('general.no')}</Badge>}
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(node.archived) ? 
                                      <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                      <div>
                                        <Button className='btn-sm' 
                                                onClick={() => history.push("/organization/appointment_categories/edit/" + node.id)}
                                                color="secondary">
                                          {t('general.edit')}
                                        </Button>
                                        <Button className='btn-sm' 
                                                onClick={() => history.push("/organization/appointment_categories/" + node.id + "/appointments/")}
                                                color="secondary">
                                          {t('organization.appointments.title')}
                                        </Button>
                                      </div>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_APPOINTMENT_CATEGORY} key={v4()}>
                                    {(archiveLocation, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('general.archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked archived")
                                             let id = node.id
                                             archiveLocation({ variables: {
                                               input: {
                                                id,
                                                archived: !archived
                                               }
                                        }, refetchQueries: [
                                            {query: GET_APPOINTMENT_CATEGORIES_QUERY, variables: {"archived": archived }}
                                        ]}).then(({ data }) => {
                                          console.log('got data', data);
                                          toast.success(
                                            (archived) ? t('general.unarchived'): t('general.archived'), {
                                              position: toast.POSITION.BOTTOM_RIGHT
                                            })
                                        }).catch((error) => {
                                          toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                              position: toast.POSITION.BOTTOM_RIGHT
                                            })
                                          console.log('there was an error sending the query', error);
                                        })
                                        }}>
                                          <Icon prefix="fa" name="inbox" />
                                        </button>
                                      </Table.Col>
                                    )}
                                  </Mutation>
                                </Table.Row>
                              ))}
                          </Table.Body>
                        </Table>
                  </ContentCard>
                )}}
             }
            </Query>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="organizationappointmentcategory">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/appointment_categories/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('organization.appointment_categories.add')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='appointments'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationAppointmentCategories))