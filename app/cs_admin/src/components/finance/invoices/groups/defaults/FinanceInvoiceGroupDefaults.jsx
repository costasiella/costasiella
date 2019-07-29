// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { Formik } from 'formik'
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
  Table,
  Text
} from "tabler-react";
import SiteWrapper from "../../../../SiteWrapper"
import HasPermissionWrapper from "../../../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../../../general/ContentCard"
import FinanceMenu from "../../../FinanceMenu"
import FinanceInvoiceGroupDefaultForm from './FinanceInvoiceGroupDefaultForm'

import { INVOICE_GROUP_DEFAULT_SCHEMA } from "./yupSchema"
import { GET_INVOICE_GROUPS_QUERY } from "../queries"
import { GET_INVOICE_GROUPS_DEFAULTS_QUERY } from "./queries"


const UPDATE_INVOICE_GROUP_DEFAULT = gql`
  mutation UpdateFinanceInvoiceGroupDefault($input: UpdateFinanceInvoiceGroupDefaultInput!) {
    updateFinanceInvoiceGroupDefault(input: $input) {
      financeInvoiceGroupDefault {
        id
        itemType
        financeInvoiceGroup {
          id
          name
        }
      }
    }
  }
`


const fetch_default_type_name = (t, itemType) => {
  switch(itemType) {
    case "MEMBERSHIPS":
      return t('finance.invoice_groups_defaults.MEMBERSHIPS')
      break
    case "SUBSCRIPTIONS":
      return t('finance.invoice_groups_defaults.SUBSCRIPTIONS')
      break
    case "CLASSPASSES":
      return t('finance.invoice_groups_defaults.CLASSPASSES')
      break
    case "DROPINCLASSES":
      return t('finance.invoice_groups_defaults.DROPINCLASSES')
      break
    case "TRIALCLASSES":
      return t('finance.invoice_groups_defaults.TRIALCLASSES')
      break
    case "EVENT_TICKETS":
      return t('finance.invoice_groups_defaults.EVENT_TICKETS')
      break
    case "SHOP_SALES":
      return t('finance.invoice_groups_defaults.SHOP_SALES')
      break
    case "TEACHER_PAYMENTS":
      return t('finance.invoice_groups_defaults.TEACHER_PAYMENTS')
      break
    case "EMPLOYEE_EXPENSES":
      return t('finance.invoice_groups_defaults.EMPLOYEE_EXPENSES')
      break
    default:
      return t('finance.invoice_groups_defaults.TYPE_NOT_FOUND')
  }
}



const FinanceInvoiceGroupsDefaults = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("finance.title")}>
          <div className="page-options d-flex">
            <Link to="/finance/invoices/groups" 
                  className='btn btn-outline-secondary btn-sm'>
                <Icon prefix="fe" name="arrow-left" /> {t('general.back_to')} {t('finance.invoice_groups.title')}
            </Link>
          </div>
        </Page.Header>
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_INVOICE_GROUPS_DEFAULTS_QUERY} variables={{}}>
             {({ loading, error, data: {financeInvoiceGroupDefaults: invoice_group_defaults}, refetch, fetchMore }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('finance.invoice_groups_defaults.title')}>
                    <Dimmer active={true}
                            loader={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('finance.invoice_groups_defaults.title')}>
                    <p>{t('finance.invoice_groups_defaults.error_loading')}</p>
                  </ContentCard>
                )
                
                // Empty list
                if (!invoice_group_defaults.edges.length) { return (
                  <ContentCard cardTitle={t('finance.invoice_groups_defaults.title')}>
                    <p>
                      {t('finance.invoice_groups_defaults.empty_list')}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('finance.invoice_groups_defaults.title')}
                               pageInfo={invoice_group_defaults.pageInfo}
                               onLoadMore={() => {
                                fetchMore({
                                  variables: {
                                    after: invoice_group_defaults.pageInfo.endCursor
                                  },
                                  updateQuery: (previousResult, { fetchMoreResult }) => {
                                    const newEdges = fetchMoreResult.financeInvoiceGroups.edges
                                    const pageInfo = fetchMoreResult.financeInvoiceGroups.pageInfo

                                    return newEdges.length
                                      ? {
                                          // Put the new invoice_groups_defaults at the end of the list and update `pageInfo`
                                          // so we have the new `endCursor` and `hasNextPage` values
                                          financeInvoiceGroups: {
                                            __typename: previousResult.financeInvoiceGroups.__typename,
                                            edges: [ ...previousResult.financeInvoiceGroups.edges, ...newEdges ],
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
                          <Table.ColHeader>{t('finance.invoice_groups_defaults.item_type')}</Table.ColHeader>
                          <Table.ColHeader>{t('finance.invoice_groups_defaults.invoice_group')}</Table.ColHeader>
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                          {invoice_group_defaults.edges.map(({ node }) => (
                            <Table.Row key={v4()}>
                              <Table.Col key={v4()}>
                                { fetch_default_type_name(t, node.itemType) }
                              </Table.Col>
                              <Table.Col>
                                <Query query={GET_INVOICE_GROUPS_QUERY} variables={{archived: false}}>
                                  {({ loading, error, data, refetch, fetchMore }) => {
                                    // Loading
                                    if (loading) return ( "Loading...")
                                    // Error
                                    if (error) return ( "error loading" )

                                    const inputData = data

                                    return (
                                      <Mutation mutation={UPDATE_INVOICE_GROUP_DEFAULT} key={v4()}>
                                        {(updateDefault, { data }) => (
                                          <Formik
                                            initialValues={{ 
                                              financeInvoiceGroup:node.financeInvoiceGroup.id
                                            }}
                                            validationSchema={INVOICE_GROUP_DEFAULT_SCHEMA}
                                            onSubmit={(values, { setSubmitting }) => {
                                                console.log('submit values:')
                                                console.log(values)

                                                updateDefault({ variables: {
                                                  input: {
                                                    id: node.id,
                                                    financeInvoiceGroup: values.financeInvoiceGroup
                                                  }
                                                }, refetchQueries: [
                                                    // {query: GET_INVOICE_GROUPS_QUERY, variables: {"archived": false }}
                                                ]})
                                                .then(({ data }) => {
                                                    console.log('got data', data)
                                                    toast.success((t('finance.invoice_groups.toast_edit_success')), {
                                                        position: toast.POSITION.BOTTOM_RIGHT
                                                      })
                                                  }).catch((error) => {
                                                    toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                                        position: toast.POSITION.BOTTOM_RIGHT
                                                      })
                                                    console.log('there was an error sending the query', error)
                                                    setSubmitting(false)
                                                  })
                                            }}
                                            >
                                            {({ isSubmitting, errors, values, setFieldTouched, setFieldValue, submitForm }) => (
                                              <FinanceInvoiceGroupDefaultForm
                                                inputData={inputData}
                                                isSubmitting={isSubmitting}
                                                errors={errors}
                                                values={values}
                                                setFieldTouched={setFieldTouched}
                                                setFieldValue={setFieldValue}
                                                submitForm={submitForm}
                                              />
                                            )}
                                        </Formik>
                                        )}
                                      </Mutation>
                                    )}}
                                  </Query>
                                </Table.Col>
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
            <h5>{t("general.menu")}</h5>
            <FinanceMenu active_link='invoices'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(FinanceInvoiceGroupsDefaults))