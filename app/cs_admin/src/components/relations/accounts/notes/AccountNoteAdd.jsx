// @flow

import React from 'react'
import { useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { Formik } from 'formik'
import { toast } from 'react-toastify'

import CSLS from "../../../../tools/cs_local_storage"

import { 
  GET_ACCOUNT_NOTES_QUERY, 
  CREATE_ACCOUNT_NOTE,
} from './queries'
// import { ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM_SCHEMA } from './yupSchema'
import AccountNoteForm from './AccountNoteForm'

import {
  Card,
} from "tabler-react";

import HasPermissionWrapper from "../../../HasPermissionWrapper"
import AccountNotesBase from "./AccountNotesBase"

import { get_list_query_variables } from "./tools"


function AccountNoteAdd({ t, history, match }) {
  // Set some initial value for noteType, if not found
  let noteType = localStorage.getItem(CSLS.RELATIONS_ACCOUNT_NOTES_NOTE_TYPE)
  if (!noteType) {
    localStorage.setItem(CSLS.RELATIONS_ACCOUNT_NOTES_NOTE_TYPE, "BACKOFFICE") 
  }

  const accountId = match.params.account_id
  const returnUrl = `/relations/accounts/${accountId}/notes`
  const cardTitle = t('relations.account.notes.title_add')

  const [addNote] = useMutation(
    CREATE_ACCOUNT_NOTE
  )

  return (
    <AccountNotesBase showBack={true}>
      <Card title={cardTitle}>
        <Formik
          initialValues={{ 
            injury: false,
            note: ""
          }}
          // validationSchema={ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM_SCHEMA}
          onSubmit={(values, { setSubmitting }, errors) => {
              console.log('submit values:')
              console.log(values)
              console.log(errors)

              addNote({ variables: {
                input: {
                  account: accountId, 
                  noteType: noteType,
                  injury: values.injury,
                  note: values.note
                }
              }, refetchQueries: [
                  {query: GET_ACCOUNT_NOTES_QUERY, variables: get_list_query_variables(accountId)}
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  history.push(returnUrl)
                  toast.success((t('relations.account.notes.toast_add_success')), {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                }).catch((error) => {
                  toast.error((t('general.toast_server_error')) + ': ' +  error, {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                  console.log('there was an error sending the query', error)
                  setSubmitting(false)
                })
          }}
          >
          {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
            <AccountNoteForm
              isSubmitting={isSubmitting}
              errors={errors}
              values={values}
              setFieldTouched={setFieldTouched}
              setFieldValue={setFieldValue}
              returnUrl={returnUrl}
            >
              {console.log(errors)}
            </AccountNoteForm>
          )}
        </Formik>
      </Card>
    </AccountNotesBase>
  )
}

export default withTranslation()(withRouter(AccountNoteAdd))
