export function getUrlFromReturnTo({returnTo, schedule_item_id, class_date, locationId}) {
  let return_url

  if (returnTo == "schedule_classes") {
    return_url = '/schedule/classes/class/attendance/' + schedule_item_id + "/" + class_date
  } else if (returnTo == "selfcheckin") {
    return_url = '/selfcheckin/checkin/' + locationId + "/" + schedule_item_id + "/" + class_date
  }
  
  return return_url
}