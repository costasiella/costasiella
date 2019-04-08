// @flow

import { Component } from 'react'
import { withTranslation } from 'react-i18next'


class Validity extends Component {
    render() {
      const t = this.props.t
      const validity = this.props.validity

      switch(validity) {
        case "DAYS":
            return t('validity.days')
            break
        case "WEEKS":
            return t('validity.weeks')
            break
        case "MONTHS":
            return t('validity.months')
            break
        case "YEARS":
            return t('validity.years')
            break
        default:
            return ""
            break
        }
    }
}
  
export default withTranslation()(Validity)
