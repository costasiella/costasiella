import React from "react"
import { Link } from 'react-router-dom'
import { withTranslation } from 'react-i18next'

import {
  Button,
  Icon, 
} from "tabler-react";

import HasPermissionWrapper from "../../../../HasPermissionWrapper"

function ButtonAdd({t, classId}) {
  return (
    <HasPermissionWrapper permission="add" resource="scheduleitemprice">
      <Link to={"/schedule/classes/all/prices/" + classId + "/add" } >
        <Button color="primary btn-block mb-6">
          <Icon prefix="fe" name="plus-circle" /> {t('schedule.classes.prices.add')}
        </Button>
      </Link>
    </HasPermissionWrapper>
  )
} 

export default withTranslation()(ButtonAdd)