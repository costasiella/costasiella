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

import BadgeBoolean from "../../ui/BadgeBoolean"

import ContentCard from "../../general/ContentCard"
import CardHeaderSeparator from "../../general/CardHeaderSeparator"
import OrganizationMenu from "../OrganizationMenu"

import { GET_CLASSPASSES_QUERY } from "./queries"

const ARCHIVE_CLASSPASS = gql`
  mutation ArchiveOrganizationClasspass($input: ArchiveOrganizationClasspassInput!) {
    archiveOrganizationClasspass(input: $input) {
      organizationClasspass {
        id
        archived
      }
    }
  }
`


const OrganizationClasspasses = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("organization.title")}>
         <div className="page-options d-flex">
            <Link to="/organization/classpasses/groups" 
                  className='btn btn-outline-secondary btn-sm'>
                <Icon prefix="fe" name="folder" /> {t('general.groups')}
            </Link>
          </div>
        </Page.Header>
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_CLASSPASSES_QUERY} variables={{ archived }}>
             {({ loading, error, data: {organizationClasspasses: classpasses}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('organization.classpasses.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('organization.classpasses.title')}>
                    <p>{t('organization.classpasses.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  {/* <Link to="/organization/classpasses/groups">
                    <Button color='secondary'  
                            size="sm"
                            icon="folder"
                            // onClick={() => {archived=false; refetch({archived});}}>
                            >
                      {t('general.groups')}
                    </Button>
                  </Link>
                  <CardHeaderSeparator /> */}
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
                if (!classpasses.edges.length) { return (
                  <ContentCard cardTitle={t('organization.classpasses.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('organization.classpasses.empty_list') : t("organization.classpasses.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('organization.classpasses.title')}
                               headerContent={headerOptions}
                               pageInfo={classpasses.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: classpasses.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.organizationClasspasses.edges
                                    const pageInfo = fetchMoreResult.organizationClasspasses.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new memberships at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          organizationMemberships: {
                                            __typename: previousResult.organizationClasspasses.__typename,
                                            edges: [ ...previousResult.organizationClasspasses.edges, ...newEdges ],
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
                              <Table.ColHeader>{t('organization.classpasses.trial_pass')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.classes')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.price')}</Table.ColHeader>
                              <Table.ColHeader>{t('general.validity')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {classpasses.edges.map(({ node }) => (
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
                                    <BadgeBoolean value={node.trialPass} />
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {(node.unlimited) ? t('general.unlimited') : node.classes }
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
                                              onClick={() => history.push("/organization/classpasses/edit/" + node.id)}
                                              color="secondary">
                                        {t('general.edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_CLASSPASS} key={v4()}>
                                    {(archiveClasspasses, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <button className="icon btn btn-link btn-sm" 
                                           title={t('general.archive')} 
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
                                  resource="organizationclasspass">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/classpasses/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('organization.classpasses.add')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='classpasses'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationClasspasses))