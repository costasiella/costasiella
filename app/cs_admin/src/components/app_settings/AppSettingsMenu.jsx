// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"

let general_active


const AppSettingsMenu = ({ t, active_link }) => (
  <div>
    <h5>{t('general.menu')}</h5>
    <List.Group transparent={true}>
      {(active_link === 'general') ? general_active = true: general_active = false}        

      <HasPermissionWrapper     
        permission="view"
        resource="appsettings"
      >
        <List.GroupItem
          key={v4()}
          className="d-flex align-items-center"
          to="#/app_settings/general"
          icon="sliders"
          active={general_active}
          >
          {t('app_settings.general')}
        </List.GroupItem>
      </HasPermissionWrapper>
    </List.Group>
  </div>
)

export default withTranslation()(AppSettingsMenu)