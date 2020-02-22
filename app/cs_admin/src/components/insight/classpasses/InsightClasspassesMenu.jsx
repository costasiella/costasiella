// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../../HasPermissionWrapper"


let sold_active


const InsightClasspassesMenu = ({ t, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'sold') ? sold_active = true: sold_active = false}
        
        <HasPermissionWrapper 
            permission="view"
            resource="insightclasspassessold">
          <List.GroupItem
              key={v4()}
              className="d-flex align-items-center"
              to="#/insight/classpasses/sold"
              icon="credit-card"
              active={sold_active}
              >
              {t('insight.classpass.sold.title')}
          </List.GroupItem>
        </HasPermissionWrapper>
    </List.Group>
);

export default withTranslation()(InsightClasspassesMenu)