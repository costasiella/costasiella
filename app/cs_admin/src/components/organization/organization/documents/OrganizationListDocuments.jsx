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

import { GET_DOCUMENTS_QUERY } from "./queries"


function OrganizationListDocuments({ t, match, history }) {
  const organizationId = match.params.organization_id
  const documentType = match.params.document_type

  const { loading, error, data, fetchMore } = useQuery(GET_DOCUMENTS_QUERY, {
    variables: { documentType: documentType }
  })

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('organization.title')}>
            <div className="page-options d-flex">
              <Link to={`/organization/documents/${organizationId}`}>
                <Button 
                  icon="arrow-left"
                  className="mr-2"
                  outline
                  color="secondary"
                >
                  {t('general.back_to')} {t('organization.documents.title')}
                </Button>
              </Link>
            </div>
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              <ContentCard 
                cardTitle={t('organization.documents.title')}
                pageInfo={data.organizationDocuments.pageInfo}
                onLoadMore={() => {
                  fetchMore({
                    variables: {
                      after: data.organizationDocuments.pageInfo.endCursor
                    },
                    updateQuery: (previousResult, { fetchMoreResult }) => {
                      const newEdges = fetchMoreResult.organizationDocuments.edges
                      const pageInfo = fetchMoreResult.organizationDocuments.pageInfo

                      return newEdges.length
                        ? {
                            // Put the new levels at the end of the list and update `pageInfo`
                            // so we have the new `endCursor` and `hasNextPage` values
                            organizationDocuments: {
                              __typename: previousResult.organizationDocuments.__typename,
                              edges: [ ...previousResult.organizationDocuments.edges, ...newEdges ],
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
                          <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                          {levels.edges.map(({ node }) => (
                            <Table.Row key={v4()}>
                              <Table.Col key={v4()}>
                                {node.name}
                              </Table.Col>
                              <Table.Col className="text-right" key={v4()}>
                                {(node.archived) ? 
                                  <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                  <Button className='btn-sm' 
                                          onClick={() => history.push("/organization/levels/edit/" + node.id)}
                                          color="secondary">
                                    {t('general.edit')}
                                  </Button>
                                }
                              </Table.Col>
                              <Mutation mutation={ARCHIVE_LEVEL} key={v4()}>
                                {(archiveCostcenter, { data }) => (
                                  <Table.Col className="text-right" key={v4()}>
                                    <button className="icon btn btn-link btn-sm" 
                                      title={t('general.archive')} 
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
                                        {query: GET_LEVELS_QUERY, variables: {"archived": archived }}
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
            </Grid.Col>
            <Grid.Col md={3}>
              <HasPermissionWrapper permission="add"
                                    resource="organizationlevel">
                <Button color="primary btn-block mb-6"
                        onClick={() => history.push("/organization/levels/add")}>
                  <Icon prefix="fe" name="plus-circle" /> {t('organization.levels.add')}
                </Button>
              </HasPermissionWrapper>
              <OrganizationMenu active_link='levels'/>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )

}

export default withTranslation()(withRouter(OrganizationListDocuments))