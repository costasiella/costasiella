

function cancelOrder({t, msgConfirm, msgDescription, msgSuccess, cancelFunction, functionVariables}) {

  return (
    confirmAlert({
      customUI: ({ onClose }) => {
        return (
          <div key={v4()} className='custom-ui'>
            <h1>{t('shop.account.orders.confirm_cancel')}</h1>
            {msgConfirm}
            {msgDescription}
            <button className="btn btn-link pull-right" onClick={onClose}>{t('general.confirm_cancel_no')}</button>
            <button
              className="btn btn-warning btn-sm outline"
              onClick={() => {
                cancelFunction(functionVariables)
                  .then(({ data }) => {
                    console.log('got data', data);
                    toast.success(
                      msgSuccess, {
                        position: toast.POSITION.BOTTOM_RIGHT
                      })
                  }).catch((error) => {
                    toast.error((t('general.toast_server_error')) + ': ' +  error, {
                        position: toast.POSITION.BOTTOM_RIGHT
                      })
                    console.log('there was an error sending the query', error);
                  })
                onClose()
              }}
            >
              <Icon name="slash" /> {t('general.confirm_cancel_yes')}
            </button>
          </div>
        )
      }
    })
  )
}