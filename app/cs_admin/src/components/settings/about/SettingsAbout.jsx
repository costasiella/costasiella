// @flow

import React from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { GET_SYSTEM_SETTINGS_QUERY } from '../queries'

import {
  Dimmer,
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";

// import FinancePaymentMethodForm from './AppSettingsGeneralForm'
import SettingsBase from "../SettingsBase"


function SettingsAbout({ t, match, history }) {
  const headerSubTitle = t('settings.about.title')
  const cardTitle = t("settings.about.about.title")

  const { 
    loading: loadingVersion, 
    error: errorVersion, 
    data: dataVersion 
  } = useQuery(GET_SYSTEM_SETTINGS_QUERY, {
    variables: {
      setting: "system_version"
    }
  })
  const { 
    loading: loadingPatch, 
    error: errorPatch, 
    data: dataPatch 
  } = useQuery(GET_SYSTEM_SETTINGS_QUERY, {
    variables: {
      setting: "system_version_patch"
    }
  })

  if ((loadingVersion) || (loadingPatch)) {
    return (
      <SettingsBase 
          headerSubTitle={headerSubTitle}
          cardTitle={cardTitle} >  
        <Card.Body>
          <Dimmer active={true}
                  loader={true}>
          </Dimmer>
        </Card.Body>
      </SettingsBase>
    )
  }
  if ((errorVersion) || errorPatch) {
    return (
      <SettingsBase 
          headerSubTitle={headerSubTitle}
          cardTitle={cardTitle} >  
        <Card.Body>
          {t("settings.general.error_loading")}
        </Card.Body>
      </SettingsBase>
    )
  }

  console.log('query data app settings')
  console.log(dataVersion)
  console.log(dataPatch)

  let version = 0
  let patch = 0
  if (dataVersion.systemSettings.edges.length){
    version = dataVersion.systemSettings.edges[0].node.value
  } 
  if (dataPatch.systemSettings.edges.length){
    patch = dataPatch.systemSettings.edges[0].node.value
  } 
    


  return (
    <SettingsBase 
      headerSubTitle={headerSubTitle}
      cardTitle={cardTitle}
    >
      <Card.Body>
        <h2>
          {t("settings.about.about.this_is_costasiella")} {`${version}.${patch}`}
        </h2>
      </Card.Body>
    </SettingsBase>
  )
}


export default withTranslation()(withRouter(SettingsAbout))