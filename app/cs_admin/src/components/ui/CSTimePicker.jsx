import React from 'react'
import DatePicker from "react-datepicker"
import { withTranslation } from 'react-i18next'

const CSTimePicker = ({t, selected, onChange=f=>f, onBlur=f=>f, className="form-control", clearable=true, placeholderText=""}) =>
    <DatePicker 
        todayButton={t('general.today')}
        dateFormat={t('system.datepicker_timeformat')}
        selected={selected}
        placeholderText={(placeholderText) ? placeholderText : t('datepicker.placeholder_time')}
        isClearable={clearable}
        showTimeSelect
        showTimeSelectOnly
        timeIntervals={15}
        className={className}
        dropdownMode="select"
        onChange={(date) => onChange(date)}
        onBlur={() => onBlur()}
    />

export default withTranslation()(CSTimePicker)