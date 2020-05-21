export function get_order_card_status_color(status) {
    switch(status) {
        case ("RECEIVED"): 
          return "blue"
          break
        case ("AWAITING_PAYMENT"): 
          return "blue"
          break
        case ("PAID"):
          return "green"
          break
        case ("DELIVERED"):
          return "green"
          break
        case "CANCELLED":
          return "orange"
          break
        default:
          return ""
      }
}