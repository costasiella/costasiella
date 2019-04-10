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

import BooleanBadge from "../../ui/BooleanBadge"

import ContentCard from "../../general/ContentCard"
import SchoolMenu from "../SchoolMenu"

import { GET_CLASSCARDS_QUERY } from "./queries"

const ARCHIVE_CLASSCARD = gql`
  mutation ArchiveSchoolClasscard($input: ArchiveSchoolClasscardInput!) {
    archiveSchoolClasscard(input: $input) {
      schoolClasscard {
        id
        archived
      }
    }
  }
`


const SchoolClasscards = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("school.page_title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_CLASSCARDS_QUERY} variables={{ archived }}>
             {({ loading, error, data: {schoolClasscards: classcards}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('school.classcards.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('school.classcards.title')}>
                    <p>{t('school.classcards.error_loading')}</p>
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
                if (!memberships.edges.length) { return (
                  <ContentCard cardTitle={t('school.classcards.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('school.classcards.empty_list') : t("school.classcards.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('school.classcards.title')}
                               headerContent={headerOptions}
                               pageInfo={classcards.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: classcards.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.schoolClasscards.edges
                                    const pageInfo = fetchMoreResult.schoolClasscards.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new memberships at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          schoolMemberships: {
                                            __typename: previousResult.schoolClasscards.__typename,
                                            edges: [ ...previousResult.schoolClasscards.edges, ...newEdges ],
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
                              <Table.ColHeader>{t('price')}</Table.ColHeader>
                              <Table.ColHeader>{t('school.classcards.validity')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {memberships.edges.map(({ node }) => (
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
                                              onClick={() => history.push("/school/classcards/edit/" + node.id)}
                                              color="secondary">
                                        {t('edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_CLASSCARD} key={v4()}>
                                    {(archiveClasscard, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked archived")
                                             let id = node.id
                                             archiveClasscard({ variables: {
                                               input: {
                                                id,
                                                archived: !archived
                                               }
                                        }, refetchQueries: [
                                            {query: GET_CLASSCARDS_QUERY, variables: {"archived": archived }}
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
                                  resource="schoolclasscard">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/school/classcards/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('school.classcards.add')}
              </Button>
            </HasPermissionWrapper>
            <SchoolMenu active_link='schoolclasscards'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(SchoolClasscards))