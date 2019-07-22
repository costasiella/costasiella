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
import SiteWrapper from "../../../../SiteWrapper"
import HasPermissionWrapper from "../../../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../../../general/ContentCard"
import CardHeaderSeparator from "../../../../general/CardHeaderSeparator"
import OrganizationMenu from "../../../OrganizationMenu"

import { GET_APPOINTMENT_PRICES_QUERY } from "./queries"

const ARCHIVE_APPOINTMENT_PRICE = gql`
  mutation ArchiveOrganizationAppointment($input: ArchiveOrganizationAppointmentInput!) {
    archiveOrganizationAppointment(input: $input) {
      organizationAppointment {
        id
        archived
      }
    }
  }
`

const OrganizationAppointmentPrices = ({ t, history, match }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("organization.title")}>
          <div className="page-options d-flex">
            <Link to="/organization/appointment_categories" 
                  className='btn btn-outline-secondary btn-sm'>
                <Icon prefix="fe" name="arrow-left" /> {t('general.back_to')} {t('organization.appointment_categories.title')}
            </Link>
          </div>
        </Page.Header>
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_APPOINTMENT_PRICES_QUERY} variables={{ archived, organizationAppointment: match.params.appointment_id }}>
             {({ loading, error, data, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('organization.appointment_prices.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('organization.appointment_prices.title')}>
                    <p>{t('organization.appointment_prices.error_loading')}</p>
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

                const prices = data.organizationAppointmentPrices

                // Empty list
                if (!prices.edges.length) { return (
                  <ContentCard cardTitle={t('organization.appointment_prices.title')}
                               headerContent={headerOptions}>
                    <p>
                    {(!archived) ? t('organization.appointment_prices.empty_list') : t("organization.appointment_prices.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('organization.appointment_prices.title')}
                               headerContent={headerOptions}
                               pageInfo={prices.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: prices.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.organizationAppointmentPrices.edges
                                    const pageInfo = fetchMoreResult.organizationAppointmentPrices.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new locations at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          organizationAppointmentPrices: {
                                            __typename: previousResult.organizationAppointmentPrices.__typename,
                                            edges: [ ...previousResult.organizationAppointmentPrices.edges, ...newEdges ],
                                            pageInfo
                                          }
                                        }
                                      : previousResult
                                  }
                                })
                              }} >
                    <div>
                      <Alert type="primary">
                        <strong>{t('general.appointment')}</strong> {data.organizationAppointment.name}
                      </Alert>

                      <Table>
                        <Table.Header>
                          <Table.Row key={v4()}>
                            <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                            <Table.ColHeader>{t('general.price')}</Table.ColHeader>
                          </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {prices.edges.map(({ node }) => (
                              <Table.Row key={v4()}>
                                <Table.Col key={v4()}>
                                  {node.account.fullName}
                                </Table.Col>
                                <Table.Col key={v4()}>
                                  {(node.displayPublic) ? 
                                    <Badge color="success">{t('general.yes')}</Badge>: 
                                    <Badge color="danger">{t('general.no')}</Badge>}
                                </Table.Col>
                                <Table.Col className="text-right" key={v4()}>
                                  {(node.archived) ? 
                                    <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                    <span>
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/organization/appointment_categories/appointments/prices/" + match.params.category_id + '/' + node.id)}
                                              color="secondary">
                                        {t('general.edit')}
                                      </Button>
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/organization/appointment_categories/appointments/prices/" + match.params.category_id + '/' + node.id)}
                                              color="secondary">
                                        {t('organization.appointment_prices.teacher_prices')}
                                      </Button>
                                    </span>
                                  }
                                </Table.Col>
                                <Mutation mutation={ARCHIVE_APPOINTMENT_PRICE} key={v4()}>
                                  {(archiveAppointmentPrice, { data }) => (
                                    <Table.Col className="text-right" key={v4()}>
                                      <button className="icon btn btn-link btn-sm" 
                                          title={t('general.archive')} 
                                          href=""
                                          onClick={() => {
                                            console.log("clicked archived")
                                            let id = node.id
                                            archiveAppointmentPrice({ variables: {
                                              input: {
                                              id,
                                              archived: !archived
                                              }
                                      }, refetchQueries: [
                                          { 
                                            query: GET_APPOINTMENT_PRICES_QUERY, 
                                            variables: {organizationAppointment: match.params.appointment_id }
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
                                  resource="organizationappointment">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/organization/appointment_categories/appointments/add/" + match.params.category_id)}>
                <Icon prefix="fe" name="plus-circle" /> {t('organization.appointment_prices.add')}
              </Button>
            </HasPermissionWrapper>
            <OrganizationMenu active_link='appointments'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(OrganizationAppointmentPrices))