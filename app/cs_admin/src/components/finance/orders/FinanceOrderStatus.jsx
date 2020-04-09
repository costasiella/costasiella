// @flow

import React, { Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Badge
} from "tabler-react";


class FinanceOrderStatus extends Component {
  constructor(props) {
    super(props)
    console.log("finance order status props:")
    console.log(props)
  }

  // ('RECEIVED', _("Received")),
  // ('AWAITING_PAYMENT', _("Awaiting payment")),
  // ('PAID', _("Paid")),
  // ('DELIVERED', _("Delivered")),
  // ('CANCELLED', _("Cancelled")),

  render() {
    const t = this.props.t
    const history = this.props.history
    const status = this.props.status

    switch (status) {
      case "RECEIVED":
        return <Badge color="secondary">{t('finance.orders.status.RECEIVED')}</Badge>
        break
      case "AWAITING_PAYMENT":
        return <Badge color="primary">{t('finance.orders.status.AWAITING_PAYMENT')}</Badge>
        break
      case "PAID":
        return <Badge color="success">{t('finance.orders.status.PAID')}</Badge>
        break
      case "DELIVERED":
        return <Badge color="success">{t('finance.orders.status.DELIVERED')}</Badge>
        break
      case "CANCELLED":
        return <Badge color="warning">{t('finance.orders.status.CANCELLED')}</Badge>
        break
      default:
        return t('finance.orders.status.NOT_FOUND') 
    }
  }
}


export default withTranslation()(withRouter(FinanceOrderStatus))