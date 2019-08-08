let timer
const itemSubmitTimeout = 750


export function handleTextInputChange(e, handleChange, submitForm) {
    clearTimeout(timer)
    handleChange(e)
    timer = setTimeout(() => {
      submitForm()
    }, itemSubmitTimeout)
  }
  
export function handleTextInputBlur(e, handleChange, submitForm) {
    // Always submit straight away onBlur
    clearTimeout(timer)
    handleChange(e)
    setTimeout(() => { submitForm() }, 225)
}

// export function handleSelectChange(e, fieldName, ) {
//     clearTimeout(timer)
//     setFieldValue(fieldName, e.target.value)
//     setFieldTouched(fieldName, true)
//     timer = setTimeout(() => {submitForm()}, itemSubmitTimeout)
// }
