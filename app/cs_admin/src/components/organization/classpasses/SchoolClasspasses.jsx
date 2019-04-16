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

import BooleanBadge from "../../ui/BooleanBadge"

import ContentCard from "../../general/ContentCard"
import CardHeaderSeparator from "../../general/CardHeaderSeparator"
import SchoolMenu from "../SchoolMenu"

import { GET_CLASSPASSES_QUERY } from "./queries"

const ARCHIVE_CLASSPASS = gql`
  mutation ArchiveSchoolClasspass($input: ArchiveSchoolClasspassInput!) {
    archiveSchoolClasspass(input: $input) {
      schoolClasspass {
        id
        archived
      }
    }
  }
`


const SchoolClasspasses = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("school.page_title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_CLASSPASSES_QUERY} variables={{ archived }}>
             {({ loading, error, data: {schoolClasspasses: classpasses}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('school.classpasses.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('school.classpasses.title')}>
                    <p>{t('school.classpasses.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  
                  <Link to="/school/classpasses/groups">
                    <Button color='secondary'  
                            size="sm"
                            icon="folder"
                            // onClick={() => {archived=false; refetch({archived});}}>
                            >
                      {t('general.groups')}
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
                if (!classpasses.edges.length) { return (
                  <ContentCard cardTitle={t('school.classpasses.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('school.classpasses.empty_list') : t("school.classpasses.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('school.classpasses.title')}
                               headerContent={headerOptions}
                               pageInfo={classpasses.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: classpasses.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.schoolClasspasses.edges
                                    const pageInfo = fetchMoreResult.schoolClasspasses.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new memberships at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          schoolMemberships: {
                                            __typename: previousResult.schoolClasspasses.__typename,
                                            edges: [ ...previousResult.schoolClasspasses.edges, ...newEdges ],
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
                              <Table.ColHeader>{t('public')}</Table.ColHeader>
                              <Table.ColHeader>{t('shop')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.classes')}</Table.ColHeader>
                              <Table.ColHeader>{t('price')}</Table.ColHeader>
                              <Table.ColHeader>{t('school.classpasses.validity')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {classpasses.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {node.name}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    <BooleanBadge value={node.displayPublic} />
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    <BooleanBadge value={node.displayShop} />
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {(node.unlimited) ? t('general.unlimited') : node.classes }
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {node.priceDisplay} <br />
                                    <span className="text-muted">{node.financeTaxRate.name}</span>
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {node.validity} <br />
                                    <span className="text-muted">
                                      {node.validityUnitDisplay}
                                    </span>
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(node.archived) ? 
                                      <span className='text-muted'>{t('unarchive_to_edit')}</span> :
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/school/classpasses/edit/" + node.id)}
                                              color="secondary">
                                        {t('edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_CLASSPASS} key={v4()}>
                                    {(archiveClasspasses, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked archived")
                                             let id = node.id
                                             archiveClasspasses({ variables: {
                                               input: {
                                                id,
                                                archived: !archived
                                               }
                                        }, refetchQueries: [
                                            {query: GET_CLASSPASSES_QUERY, variables: {"archived": archived }}
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
                                  resource="schoolclasspass">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/school/classpasses/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('school.classpasses.add')}
              </Button>
            </HasPermissionWrapper>
            <SchoolMenu active_link='schoolclasspasses'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(SchoolClasspasses))