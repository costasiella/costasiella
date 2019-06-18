import React from 'react'
import DatePicker from "react-datepicker"
import { withTranslation } from 'react-i18next'

const CSDatePicker = ({t, selected, onChange=f=>f, onBlur=f=>f, className="form-control", isClearable=true, placeholderText=""}) =>
    <DatePicker 
        todayButton={t('general.today')}
        dateFormat={t('system.datepicker_dateformat')}
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

export default withTranslation()(CSDatePicker)