// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Button,
  Icon
} from "tabler-react"


const ShopClassBookBack = ({ t }) => (
  <Link to={"/shop/classes"} >
    <Button color="primary btn-block mb-6">
      <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
    </Button>
  </Link>
)

export default withTranslation()(withRouter(ShopClassBookBack))