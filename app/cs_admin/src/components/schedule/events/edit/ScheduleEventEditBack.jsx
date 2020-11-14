// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import {
  Icon,
} from "tabler-react";

const ScheduleEventEditBack = ({ t }) => (
  <div className="page-options d-flex">
    <Link to="/schedule/events" 
          className='btn btn-outline-secondary btn-sm'>
        <Icon prefix="fe" name="arrow-left" /> {t('general.back_to')} {t('schedule.events.title')}
    </Link>
  </div>
)

export default withTranslation()(ScheduleEventEditBack)