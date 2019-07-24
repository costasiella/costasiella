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
import confirm_delete from "../../../../../tools/confirm_delete"

import ContentCard from "../../../../general/ContentCard"
import CardHeaderSeparator from "../../../../general/CardHeaderSeparator"
import OrganizationMenu from "../../../OrganizationMenu"

import { GET_APPOINTMENT_PRICES_QUERY } from "./queries"

const DELETE_APPOINTMENT_PRICE = gql`
  mutation DeleteOrganizationAppointmentPrice($input: DeleteOrganizationAppointmentPriceInput!) {
    deleteOrganizationAppointmentPrice(input: $input) {
      ok
    }
  }
`

const OrganizationAppointmentPrices = ({ t, history, match }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("organization.title")}>
          <div className="page-options d-flex">
            <Link to={"/organization/appointment_categories/" + match.params.category_id + "/appointments"}
                  className='btn btn-outline-secondary btn-sm'>
                <Icon prefix="fe" name="arrow-left" /> {t('general.back_to')} {t('general.appointment')}
            </Link>
          </div>
        </Page.Header>
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_APPOINTMENT_PRICES_QUERY} variables={{ organizationAppointment: match.params.appointment_id }}>
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

                const prices = data.organizationAppointmentPrices

                // Empty list
                if (!prices.edges.length) { return (
                  <ContentCard cardTitle={t('organization.appointment_prices.title')}>
                    <p>
                      {t('organization.appointment_prices.empty_list')}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('organization.appointment_prices.title')}
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
                        <strong>{t('general.prices_for')} {t('general.appointment')}</strong> {data.organizationAppointment.name}
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
                                {console.log(node)}
                                <Table.Col key={v4()}>
                                  {node.account.fullName}
                                </Table.Col>
                                <Table.Col key={v4()}>
                                  {node.priceDisplay}
                                </Table.Col>
                                <Table.Col className="text-right" key={v4()}>
                                  {(node.archived) ? 
                                    <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
                                    <span>
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/organization/appointment_categories/" + 
                                                match.params.category_id + "/appointments/prices/" + match.params.appointment_id + "/edit/" + node.id)}
                                              color="secondary">
                                        {t('general.edit')}
                                      </Button>
                                    </span>
                                  }
                                </Table.Col>
                                <Mutation mutation={DELETE_APPOINTMENT_PRICE} key={v4()}>
                                  {(deleteAppointmentPrice, { data }) => (
                                    <Table.Col className="text-right" key={v4()}>
                                      <button className="icon btn btn-link btn-sm" 
                                        title={t('general.delete')} 
                                        href=""
                                        onClick={() => {
                                          confirm_delete({
                                            t: t,
                                            msgConfirm: t("organization.appointment_prices.delete_confirm_msg"),
                                            msgDescription: <p>{node.account.fullName} {node.priceDisplay}</p>,
                                            msgSuccess: t('organization.appointment_prices.deleted'),
                                            deleteFunction: deleteAppointmentPrice,
                                            functionVariables: { variables: {
                                              input: {
                                                id: node.id
                                              }
                                            }, refetchQueries: [
                                              {query: GET_APPOINTMENT_PRICES_QUERY, variables: { organizationAppointment: match.params.appointment_id }} 
                                            ]}
                                          })
                                      }}>
                                        <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
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
                      onClick={() => history.push("/organization/appointment_categories/" + match.params.category_id + "/appointments/prices/" + match.params.appointment_id + "/add")}>
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