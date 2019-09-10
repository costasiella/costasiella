// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'


function StatusIcon({color=""}) {
  let className

  switch (color) {
    case "success":
      className="bg-success"
      break
    case "warning":
      className="bg-warning"
      break
    case "danger":
      className="bg-danger"
      break
    case "primary":
      className="bg-primary"
      break
    default:
      className="bg-secondary"
  }

  return <span className={"status-icon " + className} />
}


export default withTranslation()(StatusIcon)



