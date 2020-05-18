import React from 'react'
import { withTranslation } from 'react-i18next'
import { toast } from 'react-toastify'
import { confirmAlert } from 'react-confirm-alert'
import v4 from 'uuid'

import {
  Icon,
} from "tabler-react";

export function cancelOrder({t, msgConfirm, msgDescription, msgSuccess, cancelFunction, functionVariables}) {
  return (
    confirmAlert({
      customUI: ({ onClose }) => {
        return (
          <div key={v4()} className='custom-ui'>
            <h1>{t('shop.account.orders.confirm_cancel')}</h1>
            {msgConfirm}
            {msgDescription}
            <button className="btn btn-link pull-right" onClick={onClose}>{t('shop.account.orders.confirm_cancel_no')}</button>
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
              {t('shop.account.orders.confirm_cancel_yes')}
            </button>
          </div>
        )
      }
    })
  )
}
