// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Badge,
} from "tabler-react";

// Status reference
// https://docs.celeryproject.org/en/stable/userguide/tasks.html

function AutomationTaskResultStatus({t, history, match, status}) {
  switch(status) {
    case "PENDING":
      return <Badge color="secondary">{t("automation.tasks.result_statuses.pending")}</Badge>
      break
    case "STARTED":
      return <Badge color="primary">{t("automation.tasks.result_statuses.started")}</Badge>
      break
    case "SUCCESS":
      return <Badge color="success">{t("automation.tasks.result_statuses.success")}</Badge>
      break
    case "FAILURE":
      return <Badge color="danger">{t("automation.tasks.result_statuses.failure")}</Badge>
      break
    case "RETRY":
      return <Badge color="warning">{t("automation.tasks.result_statuses.retry")}</Badge>
      break
    case "REVOKED":
      return <Badge color="warning">{t("automation.tasks.result_statuses.revoked")}</Badge>
      break
    default:
      return "status unknown"
  }
}

export default withTranslation()(withRouter(AutomationTaskResultStatus))