// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_INVOICE_GROUPS_QUERY, GET_INVOICE_GROUP_QUERY } from './queries'
import { INVOICE_GROUP_SCHEMA } from './yupSchema'



import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import FinanceMenu from "../../FinanceMenu"
import FinanceInvoiceGroupForm from './FinanceInvoiceGroupForm'


const UPDATE_INVOICE_GROUP = gql`
  mutation UpdateFinanceInvoiceGroup($input: UpdateFinanceInvoiceGroupInput!) {
    updateFinanceInvoiceGroup(input: $input) {
      financeInvoiceGroup {
        id
        name
        code
      }
    }
  }
`


class FinanceInvoiceGroupEdit extends Component {
  constructor(props) {
    super(props)
    console.log("finance invoice_group edit props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/finance/invoices/groups"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t('finance.invoice_groups.title')} />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('finance.invoice_groups.title_edit')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_INVOICE_GROUP_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                    return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.financeInvoiceGroup;
                    console.log('query data')
                    console.log(data)

                    return (
                      
                      <Mutation mutation={UPDATE_INVOICE_GROUP} onCompleted={() => history.push(return_url)}> 
                        {(updateInvoiceGroup, { data }) => (
                          <Formik
                              initialValues={{ 
                                name: initialData.name, 
                                displayPublic: initialData.displayPublic,
                                dueAfterDays: initialData.dueAfterDays,
                                nextId: initialData.nextId,
                                prefix: initialData.prefix,
                                prefixYear: initialData.prefixYear,
                                autoResetPrefixYear: initialData.autoResetPrefixYear,
                                terms: initialData.terms,
                                footer: initialData.footer,
                                code: initialData.code
                              }}
                              validationSchema={INVOICE_GROUP_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  updateInvoiceGroup({ variables: {
                                    input: {
                                      id: match.params.id,
                                      name: values.name, 
                                      displayPublic: values.displayPublic,
                                      nextId: values.nextId,
                                      dueAfterDays: values.dueAfterDays,
                                      prefix: values.prefix,
                                      prefixYear: values.prefixYear,
                                      autoResetPrefixYear: values.autoResetPrefixYear,
                                      terms: values.terms,
                                      footer: values.footer,
                                      code: values.code
                                    }
                                  }, refetchQueries: [
                                      {query: GET_INVOICE_GROUPS_QUERY, variables: {"archived": false }}
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
                              {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
                                <FinanceInvoiceGroupForm
                                  isSubmitting={isSubmitting}
                                  errors={errors}
                                  values={values}
                                  return_url={return_url}
                                  setFieldTouched={setFieldTouched}
                                  setFieldValue={setFieldValue}
                                  edit={true}
                                />
                              )}
                          </Formik>
                        )}
                      </Mutation>
                      )}}
                </Query>
              </Card>
              </Grid.Col>
              <Grid.Col md={3}>
                <HasPermissionWrapper permission="change"
                                      resource="financeinvoicegroup">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <FinanceMenu active_link='invoices'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(FinanceInvoiceGroupEdit))