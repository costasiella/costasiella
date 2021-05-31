// @flow

import React, { Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Badge
} from "tabler-react";


class FinancePaymentBatchCategory extends Component {
  constructor(props) {
    super(props)
    console.log("finance payment batch category props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const categoryType = this.props.categoryType

    switch (categoryType) {
      case "COLLECTION":
        return <Badge color="success">{t('finance.payment_batch_categories.payment_batch_category_type.COLLECTION')}</Badge>
        break
      case "PAYMENT":
        return <Badge color="warning">{t('finance.payment_batch_categories.payment_batch_category_type.PAYMENT')}</Badge>
        break
      default:
        return t('finance.payment_batch_categories.payment_batch_category_type.NOT_FOUND') 
    }
  }
}


export default withTranslation()(withRouter(FinancePaymentBatchCategory))