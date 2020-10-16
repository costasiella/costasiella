import React from 'react'
import { withTranslation } from 'react-i18next'
import ButtonBack from "../ui/ButtonBack"


function AutomationBack({ t, returnUrl="/automation" }) { 
  return (
    <ButtonBack returnUrl={returnUrl} />
  )
}

export default withTranslation()(AutomationBack)