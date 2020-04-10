// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery, useMutation } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import {
  Card,
  Grid,
  Icon,
  List
} from "tabler-react";
import ShopClasspassBase from "./ShopClasspassBase"
import ShopCheckoutForm from "../ShopCheckoutForm"
import ShopClasspassesPricingCard from "./ShopClasspassPricingCard"

import { GET_CLASSPASS_QUERY } from "./queries"
import { CREATE_ORDER } from "../queries"


function ShopClasspass({ t, match, history }) {
  const title = t("shop.home.title")
  const id = match.params.id
  const { loading, error, data } = useQuery(GET_CLASSPASS_QUERY, {
    variables: { id: id }
  })

  const [createOrder, { data: createOrderData }] = useMutation(CREATE_ORDER)


  if (loading) return (
    <ShopClasspassBase title={title} >
      {t("general.loading_with_dots")}
    </ShopClasspassBase>
  )
  if (error) return (
    <ShopClasspassBase title={title}>
      {t("shop.classpass.error_loading")}
    </ShopClasspassBase>
  )

  console.log(data)
  const classpass = data.organizationClasspass
  console.log(classpass)

  return (
    <ShopClasspassBase title={title}>
        <Grid.Row>
          <Grid.Col md={4}>
            <ShopClasspassesPricingCard classpass={classpass} active={true} />
          </Grid.Col>
          <Grid.Col md={4}>
            <Card title={t("shop.classpass.additional_information")}>
              <Card.Body>
                {/* TODO: Display terms & privacy policy */}
                <div dangerouslySetInnerHTML={{__html:classpass.description}}></div>
              </Card.Body>
            </Card>
          </Grid.Col>
          <Grid.Col md={4}>
            <Card title={t("shop.checkout")}>
              <Card.Body>
                <Formik
                  initialValues={{ message: "" }}
                  // validationSchema={CLASSTYPE_SCHEMA}
                  onSubmit={(values, { setSubmitting }) => {
                      createOrder({ variables: {
                        input: {
                          message: values.message,
                          // organizationClasspass: match.params.id
                        },
                        // file: values.image
                      }, refetchQueries: [
                          // {query: GET_CLASSTYPES_QUERY, variables: {"archived": false }}
                      ]})
                      .then(({ data }) => {
                          console.log('got data', data)
                          console.log('good...  now redirect to the payment page')
                          // toast.success((t('shop..toast_add_success')), {
                          //     position: toast.POSITION.BOTTOM_RIGHT
                          //   })
                        }).catch((error) => {
                          toast.error((t('general.toast_server_error')) + ': ' +  error, {
                              position: toast.POSITION.BOTTOM_RIGHT
                            })
                          console.log('there was an error sending the query', error)
                          setSubmitting(false)
                        })
                  }}
                  >
                  {({ isSubmitting, errors, values }) => (
                    <ShopCheckoutForm 
                      isSubmitting={isSubmitting}
                      errors={errors}
                      values={values}
                    />
                  )}
                </Formik>

                {/* When a user is not logged in, show a login button to redirect to the login page */}
              </Card.Body>
            </Card>
          </Grid.Col>
        </Grid.Row>
    </ShopClasspassBase>
  )
}


export default withTranslation()(withRouter(ShopClasspass))


{/* <Grid.Col sm={6} lg={3}>
<PricingCard active>
  <PricingCard.Category>{"Premium"}</PricingCard.Category>
  <PricingCard.Price>{"$49"} </PricingCard.Price>
  <PricingCard.AttributeList>
    <PricingCard.AttributeItem>
      <strong>10 </strong>
      {"Users"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available>
      {"Sharing Tools"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available>
      {"Design Tools"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available={false}>
      {"Private Messages"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available={false}>
      {"Twitter API"}
    </PricingCard.AttributeItem>
  </PricingCard.AttributeList>
  <PricingCard.Button active>{"Choose plan"} </PricingCard.Button>
</PricingCard>
</Grid.Col> */}