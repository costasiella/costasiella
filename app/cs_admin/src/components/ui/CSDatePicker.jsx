import React, { useContext } from 'react'
import DatePicker from "react-datepicker"
import { withTranslation } from 'react-i18next'

import AppSettingsContext from "../context/AppSettingsContext"


function CSDatePicker ({t, selected, onChange=f=>f, onBlur=f=>f, className="form-control", isClearable=true, placeholderText=""}) {
  const appSettings = useContext(AppSettingsContext)
  const sysDateFormat = appSettings.dateFormat
  let dateFormat

  switch (sysDateFormat) {
    case "MM-DD-YYYY":
      dateFormat = "MM-dd-yyyy"
      break
    case "DD-MM-YYYY":
      dateFormat = "dd-MM-yyyy"
      break
    default:
      dateFormat = "yyyy-MM-dd"
  }


  return (
    <DatePicker 
        todayButton={t('general.today')}
        dateFormat={dateFormat}
        selected={selected}
        placeholderText={(placeholderText) ? placeholderText : t('datepicker.placeholder')}
        isClearable={isClearable}
        className={className}
        showMonthDropdown
        showYearDropdown
        dropdownMode="select"
        onChange={(date) => onChange(date)}
        onBlur={() => onBlur()}
    />
  )
}

export default withTranslation()(CSDatePicker)