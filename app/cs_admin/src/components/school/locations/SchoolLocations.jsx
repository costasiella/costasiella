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
import SchoolMenu from "../SchoolMenu"

import { GET_LOCATIONS_QUERY } from "./queries"

const ARCHIVE_LOCATION = gql`
    mutation ArchiveSchoolLocation($id: ID!, $archived: Boolean!) {
        archiveSchoolLocation(id: $id, archived: $archived) {
          schoolLocation {
            id
            archived
          }
        }
    }
`


// const onClickArchive = (t, id) => {
//   const options = {
//     title: t('please_confirm'),
//     message: t('school.locations.confirm_archive'),
//     buttons: [
//       {
//         label: t('yes'),
//         onClick: () => alert('Click Yes'),
//         class: 'btn btn-primary'
//       },
//       {
//         label: t('no'),
//         onClick: () => alert('Click No')
//       }
//     ],
//     childrenElement: () => <div />,
//     // customUI: ({ title, message, onClose }) => <div>Custom UI</div>,
//     willUnmount: () => {}
//   }

//   confirmAlert(options)
// }

const SchoolLocations = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title="School" />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_LOCATIONS_QUERY} variables={{ archived }}>
             {({ loading, error, data: {schoolLocations: locations}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('school.locations.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('school.locations.title')}>
                    <p>{t('school.locations.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  <Button color={(!archived) ? 'primary': 'secondary'}  
                          size="sm"
                          onClick={() => {archived=false; refetch({archived});}}>
                    {t('current')}
                  </Button>
                  <Button color={(archived) ? 'primary': 'secondary'} 
                          size="sm" 
                          className="ml-2" 
                          onClick={() => {archived=true; refetch({archived});}}>
                    {t('archive')}
                  </Button>
                </Card.Options>
                
                // Empty list
                if (!locations.edges.length) { return (
                  <ContentCard cardTitle={t('school.locations.title')}
                               header_content={headerOptions}>
                    <p>
                    {(!archived) ? t('school.locations.empty_list') : t("school.locations.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('school.locations.title')}
                               header_content={headerOptions}
                               pageInfo={locations.pageInfo}
                               onLoadMore={() => {

                                console.log('values oln:')
                                console.log(locations)
                                console.log(locations.pageInfo.endCursor)
                                fetchMore({
                                  variables: {
                                    after: locations.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    console.log('previousResult')
                                    console.log(previousResult)
                                    console.log('fetchMoreResult')
                                    console.log(fetchMoreResult)

                                    const newEdges = fetchMoreResult.schoolLocations.edges
                                    const pageInfo = fetchMoreResult.schoolLocations.pageInfo

                                    console.log('new edges')
                                    console.log(newEdges)
                                    console.log('new pi')
                                    console.log(pageInfo)
                      
                                    return newEdges.length
                                      ? {
                                          // Put the new locations at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          schoolLocations: {
                                            __typename: previousResult.schoolLocations.__typename,
                                            edges: [ ...previousResult.schoolLocations.edges, ...newEdges ],
                                            pageInfo
                                          }
                                        }
                                      : previousResult
                                  }
                                })
                              }} 
                               
                               >
                    <Table>
                          <Table.Header>
                            <Table.Row key={v4()}>
                              <Table.ColHeader>{t('name')}</Table.ColHeader>
                              <Table.ColHeader>{t('public')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {locations.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {node.name}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {(node.displayPublic) ? 
                                      <Badge color="success">{t('yes')}</Badge>: 
                                      <Badge color="danger">{t('no')}</Badge>}
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(node.archived) ? 
                                      <span className='text-muted'>{t('unarchive_to_edit')}</span> :
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/school/locations/edit/" + node.id)}
                                              color="secondary">
                                        {t('edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_LOCATION} key={v4()}>
                                    {(archiveLocation, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked archived")
                                             let id = node.id
                                             archiveLocation({ variables: {
                                              id,
                                              archived: !archived
                                        }, refetchQueries: [
                                            {query: GET_LOCATIONS_QUERY, variables: {"archived": archived }}
                                        ]}).then(({ data }) => {
                                          console.log('got data', data);
                                          toast.success(
                                            (archived) ? t('unarchived'): t('archived'), {
                                              position: toast.POSITION.BOTTOM_RIGHT
                                            })
                                        }).catch((error) => {
                                          toast.error((t('toast_server_error')) + ': ' +  error, {
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
                                  resource="schoollocation">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/school/locations/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('school.locations.add')}
              </Button>
            </HasPermissionWrapper>
            <SchoolMenu active_link='schoollocations'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(SchoolLocations))