// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'

// position: top or bottom
// tabs: [[name, title, link], ...]
// active: active tab name

function CardTabs({ t, position="top", tabs, active}) {
  let class_tabs_position = "card-tabs-top"
  switch(position) {
    case "top":
      break
    case "bottom":
      class_tabs_position = "card-tabs-top"
      break
    default:
      break
  }   

  return (
    <div className={`card-tabs ${class_tabs_position}`}>
      {
        tabs.map(({name, title, link}) => (
          <Link key={v4()} to={link} className={`card-tabs-item ${(name === active) ? "active": ""}`}>
            <h3 className="card-title"> {title} </h3>
          </Link>
        ))
      }
    </div>
  )
}

export default withTranslation()(CardTabs)



