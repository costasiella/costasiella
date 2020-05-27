import React from 'react'
import moment from 'moment'
import { TimeStringToJSDateOBJ } from '../../tools/date_tools'


export function DisplayClassInfo({t, classDate, classData, dateFormat, timeFormat }) {
    return (
      <div>
        <b>
          {moment(classDate).format(dateFormat)} {' '}
          {moment(TimeStringToJSDateOBJ(classData.scheduleClass.timeStart)).format(timeFormat)} {' - '}
          {moment(TimeStringToJSDateOBJ(classData.scheduleClass.timeEnd)).format(timeFormat)} <br />  
        </b>
        {classData.scheduleClass.organizationClasstype.name + " " + t("general.at") + ' ' + 
          classData.scheduleClass.organizationLocationRoom.organizationLocation.name}
      </div>
    )
}