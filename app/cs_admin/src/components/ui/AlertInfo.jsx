// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'

import {
  Alert
} from "tabler-react"

const AlertInfo = ({ t, title, message }) => (
  <Alert type="primary">
      <strong>{title}</strong> {message}
  </Alert> 
)

export default withTranslation()(AlertInfo)



