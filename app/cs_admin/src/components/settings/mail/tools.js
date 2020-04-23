import React from "react"


export function getTemplateInfo(t, template_name) {
  let cardTitle
  let helpText


  switch(template_name) {
    case "order_received":
      cardTitle = t("settings.mail.templates.order_received.title")
      helpText = t("settings.mail.templates.order_received.help_text")    
      break
    default:
      cardTitle = t("settings.mail.templates.not_found.title")
      helpText = t("settings.mail.templates.not_found.help_text")
  }


  return {
    "cardTitle": cardTitle,
    "helpText": helpText,
  }
}

