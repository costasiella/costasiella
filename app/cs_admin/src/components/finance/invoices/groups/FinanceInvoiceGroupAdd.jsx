// @flow

import React from 'react'
import { Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_INVOICE_GROUPS_QUERY } from './queries'
import { INVOICE_GROUP_SCHEMA } from './yupSchema'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import FinanceMenu from '../../FinanceMenu'
import FinanceInvoiceGroupForm from './FinanceInvoiceGroupForm'


const ADD_INVOICE_GROUP = gql`
  mutation CreateFinanceInvoiceGroup($input:CreateFinanceInvoiceGroupInput!) {
    createFinanceInvoiceGroup(input: $input) {
      financeInvoiceGroup{
        id
        archived
        displayPublic
        name
        nextId
        dueAfterDays
        prefix
        prefixYear
        autoResetPrefixYear
        terms
        footer
        code
      }
    }
  }
`

const return_url = "/finance/invoices/groups"

const FinanceInvoiceGroupAdd = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t('finance.title')} />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('finance.invoice_groups.title_add')}</Card.Title>
            </Card.Header>
            <Mutation mutation={ADD_INVOICE_GROUP} onCompleted={() => history.push(return_url)}> 
                {(addInvoiceGroup, { data }) => (
                    <Formik
                        initialValues={{ 
                          name: '', 
                          displayPublic: true,
                          dueAfterDays: 30,
                          prefix: 'INV',
                          prefixYear: true,
                          autoResetPrefixYear: true,
                          terms: '',
                          footer: '',
                          code: '' 
                        }}
                        validationSchema={INVOICE_GROUP_SCHEMA}
                        onSubmit={(values, { setSubmitting }) => {
                            addInvoiceGroup({ variables: {
                              input: {
                                name: values.name, 
                                displayPublic: values.displayPublic,
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
                                console.log('got data', data);
                                toast.success((t('finance.invoice_groups.toast_add_success')), {
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
                        {({ isSubmitting, values, errors, setFieldValue, setFieldTouched }) => (
                          <FinanceInvoiceGroupForm 
                            isSubmitting={isSubmitting}
                            errors={errors}
                            values={values}
                            return_url={return_url}
                            setFieldTouched={setFieldTouched}
                            setFieldValue={setFieldValue}
                          />
                        )}
                    </Formik>
                )}
                </Mutation>
          </Card>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
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
)

export default withTranslation()(withRouter(FinanceInvoiceGroupAdd))