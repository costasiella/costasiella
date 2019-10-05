// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'

const DocumentType = ({ t, documentType }) => {
  switch (documentType) {
    case "TERMS_AND_CONDITIONS":  
      return t('general.terms_and_conditions')
      break
    case "PRIVACY_POLICY":
      return t('general.privacy_policy')
      break
    default:
      return t('general.unknown_document_type')
  }
}

export default withTranslation()(DocumentType)



