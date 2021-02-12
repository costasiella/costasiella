// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import {
  Button,
} from "tabler-react";


function ButtonAddSecondaryMenu({t, match, history, linkTo}) {
  return (
    <Link to={linkTo}>
      <Button
        color="primary"
        size="sm"
        icon="plus-circle"
      >
        {t("general.add")}
      </Button>
    </Link>
  )
}

export default withTranslation()(withRouter(ButtonAddSecondaryMenu))
