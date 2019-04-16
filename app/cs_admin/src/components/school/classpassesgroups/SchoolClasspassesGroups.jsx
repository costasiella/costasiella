// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


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
import CardHeaderSeparator from "../../general/CardHeaderSeparator"
import SchoolMenu from "../SchoolMenu"

import { GET_CLASSPASS_GROUPS_QUERY } from "./queries"

const ARCHIVE_CLASSPASS_GROUP = gql`
  mutation ArchiveClasspassGroup($input: ArchiveSchoolClasspassGroupInput!) {
    archiveSchoolClasspassGroup(input: $input) {
      schoolClasspassGroup {
        id
        archived
      }
    }
  }
`


const SchoolClasspassesGroups = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("school.page_title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_CLASSPASS_GROUPS_QUERY} variables={{ archived }}>
             {({ loading, error, data: {schoolClasspassGroups: classpass_groups}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('school.classpass_groups.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('school.classpass_groups.title')}>
                    <p>{t('school.classpass_groups.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  <Link to="/school/classpasses">
                    <Button color='secondary'  
                            size="sm"
                            icon="credit-card"
                            // onClick={() => {archived=false; refetch({archived});}}>
                            >
                      {t('school.classpasses.title')}
                    </Button>
                  </Link>
                  <CardHeaderSeparator />
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
                if (!classpass_groups.edges.length) { return (
                  <ContentCard cardTitle={t('school.classpass_groups.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('school.classpass_groups.empty_list') : t("school.classpass_groups.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('school.classpass_groups.title')}
                               headerContent={headerOptions}
                               pageInfo={classpass_groups.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: classpass_groups.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.schoolClasspassGroups.edges
                                    const pageInfo = fetchMoreResult.schoolClasspassGroups.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new classpass_groups at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          schoolClasspassGroups: {
                                            __typename: previousResult.schoolClasspassGroups.__typename,
                                            edges: [ ...previousResult.schoolClasspassGroups.edges, ...newEdges ],
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
                              <Table.ColHeader>{t('name')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {classpass_groups.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {node.name}
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(node.archived) ? 
                                      <span className='text-muted'>{t('unarchive_to_edit')}</span> :
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/school/classpass_groups/edit/" + node.id)}
                                              color="secondary">
                                        {t('edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_CLASSPASS_GROUP} key={v4()}>
                                    {(archiveCostcenter, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked archived")
                                             let id = node.id
                                             archiveCostcenter({ variables: {
                                               input: {
                                                id,
                                                archived: !archived
                                               }
                                        }, refetchQueries: [
                                            {query: GET_CLASSPASS_GROUPS_QUERY, variables: {"archived": archived }}
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
                                  resource="schoolclasspassgroup">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/school/classpasses/groups/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('school.classpass_groups.add')}
              </Button>
            </HasPermissionWrapper>
            <SchoolMenu active_link=''/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
)

export default withTranslation()(withRouter(SchoolClasspassesGroups))