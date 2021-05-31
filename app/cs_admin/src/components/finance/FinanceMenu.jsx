// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"

let invoices_active
let orders_active
let costcenters_active
let glaccounts_active
let taxrates_active
let payment_methods_active
let payment_batch_collections_active
let payment_batch_payments_active
let payment_batch_categories_active

const FinanceMenu = ({ t, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'invoices') ? invoices_active = true: invoices_active = false}
        {(active_link === 'orders') ? orders_active = true: orders_active = false}
        {(active_link === 'costcenters') ? costcenters_active = true: costcenters_active = false}
        {(active_link === 'glaccounts') ? glaccounts_active = true: glaccounts_active = false}
        {(active_link === 'taxrates') ? taxrates_active = true: taxrates_active = false}
        {(active_link === 'payment_methods') ? payment_methods_active = true: payment_methods_active = false}
        {(active_link === 'payment_batch_collections') ? payment_batch_collections_active = true: payment_batch_collections_active = false}
        {(active_link === 'payment_batch_payments') ? payment_batch_payments_active = true: payment_batch_payments_active = false}
        {(active_link === 'payment_batch_categories') ? payment_batch_categories_active = true: payment_batch_categories_active = false}
        

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/finance/invoices"
            icon="file-text"
            active={invoices_active}
            >
            {t('finance.invoices.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/finance/orders"
            icon="file-plus"
            active={orders_active}
            >
            {t('finance.orders.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/finance/glaccounts"
            icon="book"
            active={glaccounts_active}
            >
            {t('finance.glaccounts.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/finance/costcenters"
            icon="compass"
            active={costcenters_active}
            >
            {t('finance.costcenters.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/finance/taxrates"
            icon="briefcase"
            active={taxrates_active}
            >
            {t('finance.taxrates.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/finance/paymentmethods"
            icon="credit-card"
            active={payment_methods_active}
            >
            {t('finance.payment_methods.title')}
        </List.GroupItem>
        <HasPermissionWrapper permission="view"
                              resource="financepaymentbatch">
          <List.GroupItem
              key={v4()}
              className="d-flex align-items-center"
              to="#/finance/paymentbatches/collection"
              icon="download"
              active={payment_batch_collections_active}
              >
              {t('finance.payment_batch_collections.title')}
          </List.GroupItem>
        </HasPermissionWrapper>
        <HasPermissionWrapper permission="view"
                              resource="financepaymentbatch">
          <List.GroupItem
              key={v4()}
              className="d-flex align-items-center"
              to="#/finance/paymentbatches/payment"
              icon="upload"
              active={payment_batch_payments_active}
              >
              {t('finance.payment_batch_payments.title')}
          </List.GroupItem>
        </HasPermissionWrapper>
        <HasPermissionWrapper permission="view"
                              resource="financepaymentbatchcategory">
          <List.GroupItem
              key={v4()}
              className="d-flex align-items-center"
              to="#/finance/paymentbatchcategories"
              icon="list"
              active={payment_batch_categories_active}
              >
              {t('finance.payment_batch_categories.title')}
          </List.GroupItem>
        </HasPermissionWrapper>
    </List.Group>
);

export default withTranslation()(FinanceMenu)