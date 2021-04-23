// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_BUSINESSES_QUERY, GET_BUSINESS_QUERY, UPDATE_BUSINESS } from './queries'
// import { ACCOUNT_SCHEMA } from './yupSchema'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { dateToLocalISO } from '../../../tools/date_tools'

import { get_list_query_variables } from "./tools"
import RelationsB2BEditBase from './RelationsB2BEditBase'
// import RelationsAccountsBack from "./RelationsAccountsBack"
import RelationsB2BEditForm from "./RelationsB2BEditForm"

// import OrganizationMenu from "../OrganizationMenu"
// import ProfileMenu from "./ProfileMenu"

function RelationsB2BEdit({ t, match, history}) {
  const businessId = match.params.business_id
  const [updateBusiness] = useMutation(UPDATE_BUSINESS)
  const { loading, error, data, refetch } = useQuery(GET_BUSINESS_QUERY, {
    variables: {
      id: businessId
    }
  })

  // Loading
  if (loading) return <RelationsB2BEditBase>
      <Card.Body>{t('general.loading_with_dots')}</Card.Body>
    </RelationsB2BEditBase>
  // Error
  if (error) {
    console.log(error)
    return <RelationsB2BEditBase>
      <Card.Body>{t('general.error_sad_smiley')}</Card.Body>
    </RelationsB2BEditBase>
  }

  const initialData = data.business
  console.log(initialData)

  return (
    <RelationsB2BEditBase cardTitle={t('relations.b2b.title_edit')}>
      <Formik
        initialValues={{ 
          name: initialData.name,
          phone: initialData.phone,
          phone2: initialData.phone2,
          address: initialData.address,
          postcode: initialData.postcode,
          city: initialData.city,
          country: initialData.country,
          emailBilling: initialData.emailBilling,
          emailContact: initialData.emailContact,
          registration: initialData.registration,
          taxRegistration: initialData.taxRegistration
        }}
        // validationSchema={ACCOUNT_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
            console.log('submit values:')
            console.log(values)

            let input_vars = {
              id: businessId,
              name: values.name,
              phone: values.phone,
              phone2: values.phone2,
              address: values.address,
              postcode: values.postcode,
              city: values.city,
              country: values.country,
              emailBilling: values.emailBilling,
              emailContact: values.emailContact,
              registration: values.registration,
              taxRegistration: values.taxRegistration
            }

            updateBusiness({ variables: {
              input: input_vars
            }, refetchQueries: [
                // Refetch list
                {query: GET_BUSINESSES_QUERY, variables: get_list_query_variables()},
                // Refresh local cached results for this account
                {query: GET_BUSINESS_QUERY, variables: {"id": businessId}}
            ]})
            .then(({ data }) => {
                console.log('got data', data)
                toast.success((t('relations.b2b.toast_edit_success')), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                setSubmitting(false)
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
          <RelationsB2BEditForm
            isSubmitting={isSubmitting}
            setFieldTouched={setFieldTouched}
            setFieldValue={setFieldValue}
            errors={errors}
            values={values}
          />
        )}
      </Formik>
    </RelationsB2BEditBase>
  )
}


export default withTranslation()(withRouter(RelationsB2BEdit))