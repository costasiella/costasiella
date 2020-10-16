// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_BLOCKS_QUERY } from "./queries"
import { ACCOUNT_SUBSCRIPTION_BLOCK_SCHEMA } from './yupSchema'
import { dateToLocalISO } from '../../../../../../tools/date_tools'

import AccountSubscriptionEditBlockBase from "./AccountSubscriptionEditBlockBase"
import AccountSubscriptionEditBlockForm from "./AccountSubscriptionEditBlockForm"


const ADD_ACCOUNT_SUBSCRIPTION_BLOCK = gql`
  mutation CreateAccountSubscriptionBlock($input:CreateAccountSubscriptionBlockInput!) {
    createAccountSubscriptionBlock(input: $input) {
      accountSubscriptionBlock {
        id
      }
    }
  }
`


function AccountSubscriptionEditBlockAdd({ t, history, match }) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/blocks/`


  const [addSubscriptionBlock] = useMutation(ADD_ACCOUNT_SUBSCRIPTION_BLOCK, {
    onCompleted: () => history.push(returnUrl),
  })

  return (
    <AccountSubscriptionEditBlockBase>
      <Formik
        initialValues={{ 
          dateStart: new Date() ,
          description: ""
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_BLOCK_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addSubscriptionBlock({ variables: {
            input: {
              accountSubscription: subscriptionId,
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
              toast.success((t('relations.account.subscriptions.blocks.toast_add_success')), {
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
            formTitle="create"
          />
        )}
      </Formik>
    </AccountSubscriptionEditBlockBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditBlockAdd))