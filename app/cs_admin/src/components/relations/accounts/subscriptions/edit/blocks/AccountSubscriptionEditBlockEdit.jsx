// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_BLOCKS_QUERY, GET_ACCOUNT_SUBSCRIPTION_BLOCK_QUERY } from "./queries"
import { ACCOUNT_SUBSCRIPTION_BLOCK_SCHEMA } from './yupSchema'
import { dateToLocalISO } from '../../../../../../tools/date_tools'

import AccountSubscriptionEditBlockBase from "./AccountSubscriptionEditBlockBase"
import AccountSubscriptionEditBlockForm from "./AccountSubscriptionEditBlockForm"


const UPDATE_ACCOUNT_SUBSCRIPTION_BLOCK = gql`
  mutation UpdateAccountSubscriptionBlock($input:UpdateAccountSubscriptionBlockInput!) {
    updateAccountSubscriptionBlock(input: $input) {
      accountSubscriptionBlock {
        id
      }
    }
  }
`


function AccountSubscriptionEditBlockEdit({ t, history, match }) {
  const id = match.params.id
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/blocks/`

  const { loading, error, data, } = useQuery(GET_ACCOUNT_SUBSCRIPTION_BLOCK_QUERY, {
    variables: {
      id: id
    }
  })

  const [updateSubscriptionBlock] = useMutation(UPDATE_ACCOUNT_SUBSCRIPTION_BLOCK, {
    onCompleted: () => history.push(returnUrl),
  })

  if (loading) return (
    <AccountSubscriptionEditBlockBase>
        <p>{t('general.loading_with_dots')}</p>
    </AccountSubscriptionEditBlockBase>
  )
  // Error
  if (error) {
    return (
      <AccountSubscriptionEditBlockBase>
          { console.log(error) }
          <p>{t('general.error_sad_smiley')}</p>
      </AccountSubscriptionEditBlockBase>
    )
  }

  console.log('query data')
  console.log(data)
  const inputData = data
  const accountSubscriptionBlock = data.accountSubscriptionBlock



  return (
    <AccountSubscriptionEditBlockBase>
      <Formik
        initialValues={{ 
          dateStart: new Date(accountSubscriptionBlock.dateStart),
          dateEnd: new Date(accountSubscriptionBlock.dateEnd),
          description: accountSubscriptionBlock.description
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_BLOCK_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          updateSubscriptionBlock({ variables: {
            input: {
              id: id,
              dateStart: dateToLocalISO(values.dateStart),
              dateEnd: dateToLocalISO(values.dateEnd),
              description: values.description
            }
          }, refetchQueries: [
              {query: GET_ACCOUNT_SUBSCRIPTION_BLOCKS_QUERY, variables: {
                accountSubscription: subscriptionId
              }},
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              toast.success((t('relations.account.subscriptions.blocks.toast_edit_success')), {
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
          <AccountSubscriptionEditBlockForm
            isSubmitting={isSubmitting}
            setFieldTouched={setFieldTouched}
            setFieldValue={setFieldValue}
            errors={errors}
            values={values}
            returnUrl={returnUrl}
            formTitle="update"
          />
        )}
      </Formik>
    </AccountSubscriptionEditBlockBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditBlockEdit))