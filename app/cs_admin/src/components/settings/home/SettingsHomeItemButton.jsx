// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from 'react-router'
import { Link } from 'react-router-dom'

import {
  Button,
  Icon,
} from "tabler-react";

function SettingsHomeItemButton({ t, link, linkTitle=null }) {
  return (
    <Link to={link} >
      <Button 
        outline
        block
        color="primary"
      >
        {linkTitle ? linkTitle: t("settings.home.link_edit")} <Icon name="chevron-right" />
      </Button>
    </Link>
  )
}

export default withTranslation()(withRouter(SettingsHomeItemButton))