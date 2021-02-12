// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Button,
  Icon
} from "tabler-react"


function ScheduleEventActivityBack({ t, match }) {
  const eventId = match.params.event_id
  const returnUrl = `/schedule/events/edit/${eventId}/activities`

  return (
    <Link to={returnUrl}>
      <Button color="primary btn-block mb-6">
        <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
      </Button>
    </Link>
  )
}


export default withTranslation()(withRouter(ScheduleEventActivityBack))