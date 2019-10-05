// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'

import {
  Button
} from "tabler-react";

const FileDownloadTableButton = ({ t, mediaUrl, className="" }) => {
  return <Button 
           color={"secondary " + className}
           size="sm"
           icon="download-cloud"
           target="_blank"
           RootComponent="a" 
           href={mediaUrl}
          >
           {t('general.download')}
          </Button>
}

export default withTranslation()(FileDownloadTableButton)



