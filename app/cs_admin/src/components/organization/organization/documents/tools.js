
export function getSubtitle(t, documentType) {
  switch (documentType) {
    case "TERMS_AND_CONDITIONS":
      return t('general.terms_and_conditions')
    case "PRIVACY_POLICY":
      return t('general.privacy_policy')
    default:
      return "Invalid document type"
  }
}
  