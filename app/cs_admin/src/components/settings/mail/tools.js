import React from "react"


export function getTemplateInfo(t, template_name) {
  let cardTitle
  let helpTexts


  switch(template_name) {
    case "class_info_mail":
      cardTitle = t("settings.mail.templates.class_info_mail.title")
      helpTexts = {
        subject: t("settings.mail.templates.class_info_mail.help_subject"),
        title: t("settings.mail.templates.class_info_mail.help_title"),
        description: t("settings.mail.templates.class_info_mail.help_description", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        content: t("settings.mail.templates.class_info_mail.help_content", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        comments: t("settings.mail.templates.class_info_mail.help_comments"), 
      }
      break
    case "event_info_mail":
      cardTitle = t("settings.mail.templates.event_info_mail.title")
      helpTexts = {
        subject: t("settings.mail.templates.event_info_mail.help_subject"),
        title: t("settings.mail.templates.event_info_mail.help_title"),
        description: t("settings.mail.templates.event_info_mail.help_description", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        content: t("settings.mail.templates.event_info_mail.help_content", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        comments: t("settings.mail.templates.event_info_mail.help_comments"), 
      }
      break
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
    case "recurring_payment_failed":
      cardTitle = t("settings.mail.templates.recurring_payment_failed.title")
      helpTexts = {
        subject: t("settings.mail.templates.recurring_payment_failed.help_subject"),
        title: t("settings.mail.templates.recurring_payment_failed.help_title"),
        description: t("settings.mail.templates.recurring_payment_failed.help_description", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        content: t("settings.mail.templates.recurring_payment_failed.help_content", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        comments: t("settings.mail.templates.recurring_payment_failed.help_comments"), 
      }
      break
      break
    case "system_footer":
      cardTitle = t("settings.mail.templates.system_footer.title")
      helpTexts = {
        subject: t("settings.mail.templates.system_footer.help_subject"),
        title: t("settings.mail.templates.system_footer.help_title"),
        description: t("settings.mail.templates.system_footer.help_description", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        content: t("settings.mail.templates.system_footer.help_content", {
          interpolation: { prefix: "%%", suffix: "%%" }
        }),
        comments: t("settings.mail.templates.system_footer.help_comments"), 
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

