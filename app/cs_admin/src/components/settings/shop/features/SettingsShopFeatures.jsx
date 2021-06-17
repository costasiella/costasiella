// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SHOP_FEATURES_QUERY, UPDATE_SHOP_FEATURES } from './queries'
import { SHOP_FEATURES_SCHEMA } from './yupSchema'


import {
  Card,
  Dimmer,
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import SettingsBase from "../../SettingsBase"
import SettingsShopFeaturesForm from "./SettingsShopFeaturesForm"


function SettingsShopFeatures({ t, match, history }) {
  const headerSubTitle = t("settings.shop.features.title")
  const cardTitle = t("settings.shop.features.title")
  const sidebarActive = "general"

  const { loading, error, data } = useQuery(GET_SHOP_FEATURES_QUERY)
  const [ updateSettings ] = useMutation(UPDATE_SHOP_FEATURES)

  console.log('query data app settings')
  console.log(data)

  if (loading) {
    return (
      <SettingsBase 
          headerSubTitle={headerSubTitle}
          cardTitle={cardTitle}
          sidebarActive={sidebarActive}>  
        <Card.Body>
          <Dimmer active={true}
                  loader={true}>
          </Dimmer>
        </Card.Body>
      </SettingsBase>
    )
  }
  if (error) {
    return (
      <SettingsBase 
          headerSubTitle={headerSubTitle}
          cardTitle={cardTitle}
          sidebarActive={sidebarActive}>  
        <Card.Body>
          {t("settings.general.error_loading")}
        </Card.Body>
      </SettingsBase>
    )
  }

  const shopFeatures = data.systemFeatureShop
  
  return (
    <SettingsBase 
      headerSubTitle={headerSubTitle}
      cardTitle={cardTitle}
      sidebarActive={sidebarActive}
    >  
    <Formik
      initialValues={{ 
        memberships: shopFeatures.memberships,
        subscriptions: shopFeatures.subscriptions,
        classpasses: shopFeatures.classpasses,
        classes: shopFeatures.classes,
        events: shopFeatures.events,
      }}
      validationSchema={SHOP_FEATURES_SCHEMA}
      onSubmit={(values, { setSubmitting }, errors) => {
          console.log('submit values:')
          console.log(values)
          console.log(errors)

          updateSettings({ variables: {
            input: {
              memberships: values.memberships,
              subscriptions: values.subscriptions,
              classpasses: values.classpasses,
              classes: values.classes,
              events: values.events
            }
          }, refetchQueries: [
              {query: GET_SHOP_FEATURES_QUERY}
          ]})
          .then(({ data }) => {
              console.log('got data', data)
              toast.success((t('settings.general.toast_edit_success')), {
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
      {({ isSubmitting, errors, values }) => (
        <SettingsShopFeaturesForm
          isSubmitting={isSubmitting}
          errors={errors}
          values={values}
        >
          {console.log(errors)}
        </SettingsShopFeaturesForm>
      )}
      </Formik>
    </SettingsBase>
  )
}


export default withTranslation()(withRouter(SettingsShopFeatures))