// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import CSLS from "../../../tools/cs_local_storage"
import { get_list_query_variables } from './tools'


function defaultValueLocation() {
  let location = localStorage.getItem(CSLS.SCHEDULE_CLASSES_FILTER_LOCATION)
  if (location) {
    return location
  } else {
    return ""
  }
}


const ScheduleClassesFilter = ({ t, history, data, refetch }) => (
  <div>
    {/* Locations */}
    <select 
      className="form-control"
      defaultValue={defaultValueLocation()}
      onChange={ (event) => {
        localStorage.setItem(CSLS.SCHEDULE_CLASSES_FILTER_LOCATION, event.target.value)
        console.log('trigger refetch')
        refetch(get_list_query_variables())
      }}
    >
      <option value="" key={v4()}>{t("schedule.classes.filter_all_locations")}</option>
      {data.organizationLocations.edges.map(({ node }) =>
        <option value={node.id} key={v4()}>{node.name}</option>
      )}
    </select>
    {/* Classtypes */}
    <select 
      className="form-control"
      defaultValue={defaultValueLocation()}
      onChange={ (event) => {
        localStorage.setItem(CSLS.SCHEDULE_CLASSES_FILTER_LOCATION, event.target.value)
        console.log('trigger refetch')
        refetch(get_list_query_variables())
      }}
    >
      <option value="" key={v4()}>{t("schedule.classes.filter_all_locations")}</option>
      {data.organizationLocations.edges.map(({ node }) =>
        <option value={node.id} key={v4()}>{node.name}</option>
      )}
    </select>
    {/* Levels */}
    <select 
      className="form-control"
      defaultValue={defaultValueLocation()}
      onChange={ (event) => {
        localStorage.setItem(CSLS.SCHEDULE_CLASSES_FILTER_LOCATION, event.target.value)
        console.log('trigger refetch')
        refetch(get_list_query_variables())
      }}
    >
      <option value="" key={v4()}>{t("schedule.classes.filter_all_locations")}</option>
      {data.organizationLocations.edges.map(({ node }) =>
        <option value={node.id} key={v4()}>{node.name}</option>
      )}
    </select>
  </div>
);

export default withTranslation()(withRouter(ScheduleClassesFilter))