import moment from 'moment'

export function class_subtitle({t, location, locationRoom, classtype, timeStart, date}) {
  return t('general.class') + ': ' + 
         location + ' (' + locationRoom + ') - ' + 
         classtype + ' @ ' + 
         moment(date).format('LL') + ' ' + moment(timeStart).format('LT')
}

