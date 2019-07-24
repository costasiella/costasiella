// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Alert,
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
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../../general/ContentCard"
import CardHeaderSeparator from "../../../general/CardHeaderSeparator"
import OrganizationMenu from "../../OrganizationMenu"

import { GET_LOCATION_ROOMS_QUERY } from "./queries"

const ARCHIVE_LOCATION_ROOM = gql`
  mutation ArchiveOrganizationLocationRoom($input: ArchiveOrganizationLocationRoomInput!) {
    archiveOrganizationLocationRoom(input: $input) {
      organizationLocationRoom {
        id
        archived
      }
    }
  }
`

const OrganizationLocationsRooms = ({ t, history, match, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("organization.title")}>
          <div className="page-options d-flex">
            <Link to="/organization/locations" 
                  className='btn btn-outline-secondary btn-sm'>
                <Icon prefix="fe" name="arrow-left" /> {t('general.back_to')} {t('organization.locations.title')}
            </Link>
          </div>
        </Page.Header>
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_LOCATION_ROOMS_QUERY} variables={{ archived, organizationLocation: match.params.location_id }}>
             {({ loading, error, data: {organizationLocationRooms: location_rooms, organizationLocation: location}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('organization.location_rooms.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('organization.location_rooms.title')}>
                    <p>{t('organization.location_rooms.error_loading')}</p>
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
                if (!location_rooms.edges.length) { return (
                  <ContentCard cardTitle={t('organization.location_rooms.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('organization.location_rooms.empty_list') : t("organization.location_rooms.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('organization.location_rooms.title')}
                               headerContent={headerOptions}
                               pageInfo={location_rooms.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: location_rooms.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.organizationLocationsRooms.edges
                                    const pageInfo = fetchMoreResult.organizationLocationsRooms.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new locations at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          organizationLocationsRooms: {
                                            __typename: previousResult.organizationLocationsRooms.__typename,
                                            edges: [ ...previousResult.organizationLocationsRooms.edges, ...newEdges ],
                                            pageInfo
                                          }
                                        }
                                      : previousResult
                                  }
                                })
                              }} >
                    <div>
                      <Alert type="primary">
                        <strong>{t('general.location')}</strong> {location.name}
                      </Alert>

                      <Table>
                        <Table.Header>
                          <Table.Row key={v4()}>
                            <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                            <Table.ColHeader>{t('general.public')}</Table.ColHeader>
                          </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {location_rooms.edges.map(({ node }) => (
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
                                    <Button className='btn-sm' 
                                            onClick={() => history.push("/organization/locations/rooms/edit/" + match.params.location_id + '/' + node.id)}
                                            color="secondary">
                                      {t('general.edit')}
                                    </Button>
                                  }
                                </Table.Col>
                                <Mutation mutation={ARCHIVE_LOCATION_ROOM} key={v4()}>
                                  {(archiveLocationsRoom, { data }) => (
                                    <Table.Col className="text-right" key={v4()}>
                                      <button className="icon btn btn-link btn-sm" 
                                          title={t('general.archive')} 
                                          href=""
                                          onClick={() => {
                                            console.log("clicked archived")
                                            let id = node.id
                                            archiveLocationsRoom({ variables: {
                                              input: {
                                              id,
                                              archived: !archived
                                              }
                                      }, refetchQueries: [
                                          { 
                                            query: GET_LOCATION_ROOMS_QUERY, 
                                            variables: {"archived": archived, organizationLocation: match.params.location_id }
                                          }
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
                      </div>
                  </ContentCard>
                )}}
             }
            </Query>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="organizationlocationroom">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/locations/rooms/add/" + match.params.location_id)}>
                <Icon prefix="fe" name="plus-circle" /> {t('organization.location_rooms.add')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='locations'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationLocationsRooms))