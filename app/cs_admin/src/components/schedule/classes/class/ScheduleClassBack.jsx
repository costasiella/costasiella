// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Button,
  Icon
} from "tabler-react"


const ScheduleClassBack = ({ t, classId }) => (
  <Link to={"/schedule/classes/"} >
    <Button color="link mr-2">
      <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
    </Button>
  </Link>
)

export default withTranslation()(withRouter(ScheduleClassBack))