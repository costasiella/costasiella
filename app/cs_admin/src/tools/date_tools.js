export function dateToLocalISO(date) {
    if (date instanceof Date) {
        return date.getFullYear() + '-' + 
               ("0" + (date.getMonth() + 1)).slice(-2) + '-' +
               ("0" + date.getDate()).slice(-2)
    } else {
        return date
    }
}


export function dateToLocalISOTime(date) {
    if (date instanceof Date) {
        return date.getHours() + ':' + 
               date.getMinutes()
    } else {
        return date
    }
}