
import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import {
  Icon,
} from "tabler-react";

const InsightBackHome = ({ t }) => (
  <div className="page-options d-flex">
    <Link to="/insight" 
          className='btn btn-secondary mr-4'>
        <Icon prefix="fe" name="arrow-left" /> {t('general.back_to')} {t('insight.title')}
    </Link>
  </div>
)

export default withTranslation()(InsightBackHome)