// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"

let costcenters_active
let glaccounts_active
let taxrates_active

const FinanceMenu = ({ t, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'costcenters') ? costcenters_active = true: costcenters_active = false}
        {(active_link === 'glaccounts') ? glaccounts_active = true: glaccounts_active = false}
        {(active_link === 'taxrates') ? taxrates_active = true: taxrates_active = false}
        

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/finance/glaccounts"
            icon="book"
            active={glaccounts_active}
            >
            {t('finance.menu.glaccounts')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/finance/costcenters"
            icon="compass"
            active={costcenters_active}
            >
            {t('finance.menu.costcenters')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/finance/taxrates"
            icon="briefcase"
            active={taxrates_active}
            >
            {t('finance.menu.taxrates')}
        </List.GroupItem>
    </List.Group>
);

export default withTranslation()(FinanceMenu)