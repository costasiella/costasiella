import React from 'react'
import DatePicker from "react-datepicker"
import { withTranslation } from 'react-i18next'

const CSDatePicker = ({t, selected, onChange=f=>f, onBlur=f=>f}) =>
    <DatePicker 
        todayButton={t('general.today')}
        dateFormat={t('system.date_format_datepicker')}
        selected={selected}
        placeholderText={t('datepicker.placeholder')}
        isClearable={true}
        className="form-control"
        showMonthDropdown
        showYearDropdown
        dropdownMode="select"
        onChange={(date) => onChange(date)}
        onBlur={() => onBlur()}
    />

export default withTranslation()(CSDatePicker)