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
          className='btn btn-link btn-sm mr-2'>
        <Icon prefix="fe" name="chevrons-left" /> {t('general.back_to')} {t('schedule.events.title')}
    </Link>
  </div>
)

export default withTranslation()(ScheduleEventEditBack)