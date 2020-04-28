import React from "react"


export function getTemplateInfo(t, template_name) {
  let cardTitle
  let helpTexts


  switch(template_name) {
    case "order_received":
      cardTitle = t("settings.mail.templates.order_received.title")
      helpTexts = {
        subject: t("settings.mail.templates.order_received.help_subject"),
        title: t("settings.mail.templates.order_received.help_title"),
        description: t("settings.mail.templates.order_received.help_description", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        content: t("settings.mail.templates.order_received.help_content", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        comments: t("settings.mail.templates.order_received.help_comments"), 
      }
      break
    default:
      cardTitle = t("settings.mail.templates.not_found.title")
      helpTexts = {
        subject: t("settings.mail.templates.not_found.help_subject"),
        title: t("settings.mail.templates.not_found.help_title"),
        description: t("settings.mail.templates.not_found.help_description"),
        content: t("settings.mail.templates.not_found.help_content"),
        comments: t("settings.mail.templates.not_found.help_comments"),
      }
  }


  return {
    "cardTitle": cardTitle,
    "helpTexts": helpTexts,
  }
}

