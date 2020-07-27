import React from 'react'
import { withTranslation } from 'react-i18next'
import ButtonBack from "../ui/ButtonBack"


function SettingsBack({ t, returnUrl="/settings" }) { 
  return (
    <ButtonBack returnUrl={returnUrl} />
  )
}

export default withTranslation()(SettingsBack)