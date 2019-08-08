let timer
const itemSubmitTimeout = 2000


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

