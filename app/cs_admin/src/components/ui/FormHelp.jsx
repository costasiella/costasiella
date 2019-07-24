import React from 'react'
import { withTranslation } from 'react-i18next'
import { v4 } from 'uuid'

// import {
//   Badge
// } from "tabler-react"

const FormHelp = ({ t, message }) => (
    <span className="form-help" 
          data-toggle="popover" 
          data-placement="top" 
          data-content={message} 
          data-original-title="" 
          title={message} 
          aria-describedby={'popover23432'}>
        ?
    </span>
)

export default withTranslation()(FormHelp)