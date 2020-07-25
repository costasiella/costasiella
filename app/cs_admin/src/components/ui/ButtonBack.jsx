import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from "react-router-dom"

import {
  Button
} from "tabler-react"

const ButtonBack = ({ t, returnUrl }) => (
  <Link to={returnUrl}>
    <Button
      color="secondary"
      icon="arrow-left">
        {t("general.back")}
    </Button>
  </Link>
)

export default withTranslation()(ButtonBack)
