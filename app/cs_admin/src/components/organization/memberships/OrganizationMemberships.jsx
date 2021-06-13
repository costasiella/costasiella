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

import BadgeBoolean from "../../ui/BadgeBoolean"
import Validity from "../../ui/Validity"

import ContentCard from "../../general/ContentCard"
import OrganizationMenu from "../OrganizationMenu"

import { GET_MEMBERSHIPS_QUERY } from "./queries"

const ARCHIVE_MEMBERSHIP = gql`
  mutation ArchiveOrganizationMembership($input: ArchiveOrganizationMembershipInput!) {
    archiveOrganizationMembership(input: $input) {
      organizationMembership {
        id
        archived
      }
    }
  }
`


const OrganizationMemberships = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("organization.title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_MEMBERSHIPS_QUERY} variables={{ archived }}>
             {({ loading, error, data: {organizationMemberships: memberships}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('organization.memberships.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('organization.memberships.title')}>
                    <p>{t('organization.memberships.error_loading')}</p>
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
                if (!memberships.edges.length) { return (
                  <ContentCard cardTitle={t('organization.memberships.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('organization.memberships.empty_list') : t("organization.memberships.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('organization.memberships.title')}
                               headerContent={headerOptions}
                               pageInfo={memberships.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: memberships.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.organizationMemberships.edges
                                    const pageInfo = fetchMoreResult.organizationMemberships.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new memberships at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          organizationMemberships: {
                                            __typename: previousResult.organizationMemberships.__typename,
                                            edges: [ ...previousResult.organizationMemberships.edges, ...newEdges ],
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
                              <Table.ColHeader>{t('general.shop')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.price')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.validity')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {memberships.edges.map(({ node }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {node.name}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    <BadgeBoolean value={node.displayPublic} />
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    <BadgeBoolean value={node.displayShop} />
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {node.priceDisplay} <br />
                                    {(node.financeTaxRate) ? 
                                      <span className="text-muted">{node.financeTaxRate.name}</span>
                                      : ""
                                    }
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {node.validity} <br />
                                    <span className="text-muted">
                                      {node.validityUnitDisplay}
                                    </span>
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(node.archived) ? 
                                      <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/organization/memberships/edit/" + node.id)}
                                              color="secondary">
                                        {t('general.edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_MEMBERSHIP} key={v4()}>
                                    {(archiveMembership, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('general.archive')} 
                                           href=""
                                           onClick={() => {
                                             console.log("clicked archived")
                                             let id = node.id
                                             archiveMembership({ variables: {
                                               input: {
                                                id,
                                                archived: !archived
                                               }
                                        }, refetchQueries: [
                                            {query: GET_MEMBERSHIPS_QUERY, variables: {"archived": archived }}
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
                                  resource="organizationmembership">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/memberships/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('organization.memberships.add')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='memberships'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationMemberships))