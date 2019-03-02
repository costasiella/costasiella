import i18n from "i18next"
import { initReactI18next } from "react-i18next"
// import Backend from 'i18next-xhr-backend'
import LanguageDetector from 'i18next-browser-languagedetector'

// the translations
// (tip move them in a JSON file and import them)
// const resources = {
//   en: {
//     translations: {
//         school: "School"
//     }
//   }
// }

import en_US_common from "./i18n/en_US/common"
const resources = {
    en_US: {
        common: en_US_common
    },
}

console.log(resources)


i18n
  // load translation using xhr -> see /public/locales
  // learn more: https://github.com/i18next/i18next-xhr-backend
  //   .use(Backend)
  // detect user language
  // learn more: https://github.com/i18next/i18next-browser-languageDetector
  .use(LanguageDetector)
  // pass the i18n instance to react-i18next.
  .use(initReactI18next)
  // init i18next
  // for all options read: https://www.i18next.com/overview/configuration-options
  .init({
    resources,
    lng: "en_US",
    fallbackLng: "en_US",
    ns: ["common"],
    defaultNS: "common",
    debug: true,

    // keySeparator: false, // we do not use keys in form messages.welcome
    keySeparator: '.', // we use keys in form messages.welcome

    interpolation: {
      escapeValue: false, // react already safes from xss
    }
  })

  export default i18n