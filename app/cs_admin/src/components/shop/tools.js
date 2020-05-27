import React from 'react'

export function DisplayClassInfo({t, classDate, classData, dateFormat, timeFormat }) {
    return (
      <div>
        <b>
          {moment(classDate).format(dateFormat)} {' '}
          {moment(TimeStringToJSDateOBJ(dataClass.scheduleClass.timeStart)).format(timeFormat)} {' - '}
          {moment(TimeStringToJSDateOBJ(dataClass.scheduleClass.timeEnd)).format(timeFormat)} <br />  
        </b>
        {dataClass.scheduleClass.organizationClasstype.name + " " + t("general.at") + ' ' + 
          dataClass.scheduleClass.organizationLocationRoom.organizationLocation.name}
      </div>
    )
}