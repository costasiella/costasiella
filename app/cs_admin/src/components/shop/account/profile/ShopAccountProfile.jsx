// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import {
  Card,
  Page,
  Grid,
  Container
} from "tabler-react";
import SiteWrapperShop from "../../../SiteWrapperShop"
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"
import { UPDATE_PROFILE } from "./queries"

import ShopAccountProfileBase from "./ShopAccountProfileBase"
import ShopAccountProfileForm from "./ShopAccountProfileForm"

import { dateToLocalISO } from '../../../../tools/date_tools'

import { ACCOUNT_SCHEMA } from "./yupSchema"


function ShopAccountProfile({t, match, history}) {
  const { loading, error, data } = useQuery(GET_USER_PROFILE)
  const [ updateProfile ] = useMutation(UPDATE_PROFILE)

  if (loading) return (
    <ShopAccountProfileBase>
      {t("general.loading_with_dots")}
    </ShopAccountProfileBase>
  )
  if (error) return (
    <ShopAccountProfileBase>
      {t("shop.account.profile.error_loading_data")}
    </ShopAccountProfileBase>
  )

  console.log("User data: ###")
  console.log(data)
  const user = data.user

  let dateOfBirth = null
  if (user.dateOfBirth) {
    dateOfBirth = new Date(user.dateOfBirth)
  }

  return (
    <ShopAccountProfileBase accountName={user.fullName}>
      <Grid.Row>
        <Grid.Col md={12}>
          <Formik
            initialValues={{ 
              firstName: user.firstName, 
              lastName: user.lastName, 
              email: user.email,
              dateOfBirth: dateOfBirth,
              gender: user.gender,
              emergency: user.emergency,
              phone: user.phone,
              mobile: user.mobile,
              address: user.address,
              postcode: user.postcode,
              city: user.city,
              country: user.country
            }}
            validationSchema={ACCOUNT_SCHEMA}
            onSubmit={(values, { setSubmitting }) => {
                console.log('submit values:')
                console.log(values)

                let input_vars = {
                  id: user.accountId,
                  firstName: values.firstName,
                  lastName: values.lastName,
                  email: values.email,
                  gender: values.gender,
                  emergency: values.emergency,
                  phone: values.phone,
                  mobile: values.mobile,
                  address: values.address,
                  postcode: values.postcode,
                  city: values.city,
                  country: values.country
                }

                if (values.dateOfBirth) {
                  input_vars['dateOfBirth'] = dateToLocalISO(values.dateOfBirth)
                } 

                updateProfile({ variables: {
                  input: input_vars
                }, refetchQueries: [
                    // // Refetch list
                    // {query: GET_ACCOUNTS_QUERY, variables: get_list_query_variables()},
                    // // Refresh local cached results for this account
                    // {query: GET_ACCOUNT_QUERY, variables: {"id": match.params.account_id}}
                ]})
                .then(({ data }) => {
                    console.log('got data', data)
                    toast.success((t('shop.account.profile.toast_edit_success')), {
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
              <ShopAccountProfileForm
                isSubmitting={isSubmitting}
                setFieldTouched={setFieldTouched}
                setFieldValue={setFieldValue}
                errors={errors}
                values={values}
                returnUrl={"/shop/account"}
              />
            )}
          </Formik>
        </Grid.Col>
      </Grid.Row>
    </ShopAccountProfileBase>
  )
}


export default withTranslation()(withRouter(ShopAccountProfile))