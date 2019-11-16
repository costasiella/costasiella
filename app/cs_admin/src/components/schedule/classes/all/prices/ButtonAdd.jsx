import React from "react"

import HasPermissionWrapper from "../../../../HasPermissionWrapper"

const ButtonAdd = <HasPermissionWrapper permission="add" resource="scheduleitemprice">
  <Link to={"/schedule/classes/all/prices/" + classId + "/add" } >
    <Button color="primary btn-block mb-6">
      <Icon prefix="fe" name="plus-circle" /> {t('schedule.classes.prices.add')}
    </Button>
  </Link>
</HasPermissionWrapper>

export default ButtonAdd