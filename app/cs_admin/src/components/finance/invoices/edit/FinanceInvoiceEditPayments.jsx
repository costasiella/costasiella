// @flow

import React from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo"
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { v4 } from 'uuid'


import {
  Icon, 
  Table
} from "tabler-react"



const FinanceInvoiceEditPayments = ({ t, history, match, refetchInvoice, inputData }) => (
  <div>
      <Table>
        <Table.Header>
          <Table.Row>
            <Table.ColHeader>{t("general.date")}</Table.ColHeader>
            <Table.ColHeader>{t("general.amount")}</Table.ColHeader>
            <Table.ColHeader>{t("general.payment_method")}</Table.ColHeader>
            <Table.ColHeader>{t("general.note")}</Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {inputData.financeInvoice.payments.edges.map(({ node }) => (
            <Table.Row key={"payment_" + node.id}>
              <Table.Col>
                { node.date }
              </Table.Col>
              <Table.Col>
                { node.amountDisplay }
              </Table.Col>
              <Table.Col>
                { (node.financePaymentMethod) ? node.financePaymentMethod.name : "" }
              </Table.Col>
              <Table.Col>
                { node.note }
              </Table.Col>
              <Table.Col>
                <Link to={ "/finance/invoices/" + inputData.financeInvoice.id + "/payment/edit/" + node.id } 
                      className='btn btn-secondary btn-sm mr-2'
                >
                  <Icon prefix="fe" name="edit" />
                </Link>

                Edit | Del
                {/* <FinanceInvoiceItemDelete node={node} /> */}
              </Table.Col>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
  </div>
)

export default withTranslation()(withRouter(FinanceInvoiceEditPayments))