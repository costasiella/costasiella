import moment from 'moment'

export function class_edit_all_subtitle({location, locationRoom, classtype, starttime}) {
  return location + ' (' + locationRoom + ') - ' + classtype + ' @ ' + moment(starttime).format('LT')
}
