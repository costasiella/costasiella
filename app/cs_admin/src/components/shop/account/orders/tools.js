export function get_order_card_status_color(status) {
    switch(status) {
        case ("RECEIVED" || "AWAITING_PAYMENT"): 
          return "blue"
          break
        case ("PAID" || "DDELIVERED"):
          return "green"
          break
        case "CANCELLED":
          return "orange"
          break
        default:
          return ""
      }
}