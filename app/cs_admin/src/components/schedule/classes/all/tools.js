import moment from 'moment'

export function class_edit_all_subtitle({t, location, locationRoom, classtype, starttime}) {
  return t('general.class') + ': ' + location + ' (' + locationRoom + ') - ' + classtype + ' @ ' + moment(starttime).format('LT')
}
