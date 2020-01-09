// @flow

import React, { useCallback, useState, useEffect } from 'react'
import gql from "graphql-tag"
import { useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { DragDropContext, Draggable, Droppable } from 'react-beautiful-dnd';
import { toast } from 'react-toastify'

import {
  Card,
  Dimmer, 
  Table
} from "tabler-react"

import UpdateProductName from "./UpdateProductName"
import UpdateDescription from "./UpdateDescription"
import UpdateQuantity from "./UpdateQuantity"
import UpdatePrice from "./UpdatePrice"
import UpdateFinanceTaxRate from "./UpdateFinanceTaxRate"
import FinanceInvoiceItemDelete from "./FinanceInvoiceItemDelete"
import FinanceInvoiceItemAdd from "./FinanceInvoiceItemAdd"
import { GET_INVOICE_QUERY } from '../queries'


export const UPDATE_INVOICE_ITEM = gql`
  mutation UpdateFinanceInvoiceItem($input: UpdateFinanceInvoiceItemInput!) {
    updateFinanceInvoiceItem(input: $input) {
      financeInvoiceItem {
        id
        productName
        description
        quantity
        price
        financeTaxRate {
          id
          name
        }
        total
        lineNumber
      }
    }
  }
`

function FinanceInvoiceEditItems ({ t, history, match, refetchInvoice, inputData }) {
  const [updateItem, { data }] = useMutation(UPDATE_INVOICE_ITEM)

  // const [ invoiceItems, setInvoiceItems ] = useState(inputData.financeInvoice.items.edges)
  // const [ allowReorder, setAllowReorder ] = useState(true)
  const [ updating, setUpdating ] = useState(false)

  // useEffect(() => {
  //   console.log("props updated")

  //   if (inputData.financeInvoice.items.edges !== invoiceItems) {
  //     setInvoiceItems(inputData.financeInvoice.items.edges)
  //     setAllowReorder(false)
  //   } else {
  //     setAllowReorder(true)
  //   }

  //   let unmounted = false
  //   if(!unmounted) {
  //     // cancel update state
  //   }
  //   return () => unmounted = true;
  // }, [])
  // }, [inputData.financeInvoice.items.edges, invoiceItems])

  // useEffect(() => {
  //   console.log("render items!")
  //   console.log(invoiceItems)
  //   // Update invoice items when one has been added or removed
  //   setInvoiceItems(inputData.financeInvoice.items.edges) 
  //   console.log("after effect items!")
  //   console.log(invoiceItems)
  // })
  // }, [inputData.financeInvoice.items.edges])


  // useEffect(() => {
  //   console.log("Called on setInvoiceItems")
  //   // setInvoiceItems(inputData.financeInvoice.items.edges) 
  // }, [setInvoiceItems] )

  // console.log("main component items...")
  // console.log(invoiceItems)

  const onDragEnd = useCallback((result) => {
    // the only one that is required
    console.log('onDragEnd triggered...')
    console.log(result)
    const { draggableId, destination, source, reason } = result
    console.log(source)
    console.log(destination)
    console.log(reason)

    // TODO: notify backend of sorting change
    // dragableID = nodeID 
    // Indexes are 0 indexed
    // source.index = old index
    // destination.index = new index

    // Nothing to do, nowhere to go...
    console.log("drop cancelled...")
    if (!destination || reason === 'CANCEL') {
      return
    }

    // Moved back to the same spot
    console.log("dropped to the same spot")
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return
    }

    // console.log("invoice items in onDragEnd")
    // console.log(invoiceItems)

    // const new_order = invoiceItems
    // const item = invoiceItems[source.index]
    // console.log("dnd item:")
    // console.log(item)
    // // remove dnd'd item from array
    // new_order.splice(source.index, 1)
    // // add dnd'd item to new position in array
    // new_order.splice(destination.index, 0, item)
    // setInvoiceItems(new_order) 

    updateLineNumber({
      node_id: draggableId,
      line_number: destination.index
    })

  }, []);


  const updateLineNumber = ({ node_id, line_number }) => {
    setUpdating(true)
    updateItem({ 
      variables: { 
        input: {
          id: node_id,
          lineNumber: line_number
        } 
      },
      refetchQueries: [
        { query: GET_INVOICE_QUERY, variables: { id: inputData.financeInvoice.id }}
      ]
    }).then(({ data }) => {
      console.log('got data', data)
      toast.success((t('finance.invoice.saved_item_sorting')), {
          position: toast.POSITION.BOTTOM_RIGHT
      })
      setTimeout(() => setUpdating(false), 125)
    }).catch((error) => {
      toast.error((t('general.toast_server_error')) + ': ' +  error, {
          position: toast.POSITION.BOTTOM_RIGHT
      })
      console.log('there was an error sending the query', error)
      setTimeout(() => setUpdating(false), 125)
    })
  }

  return (
    <DragDropContext onDragEnd={onDragEnd} >
      <Card statusColor="blue">
        <Card.Header>
          <Card.Title>{t('general.items')}</Card.Title>
          <Card.Options>
            <FinanceInvoiceItemAdd />
          </Card.Options>
        </Card.Header>
        <Card.Body>
          {/* {(allowReorder) ? "reordering allowed" : "no reordering allowed"} */}
          <Dimmer active={updating} loader={updating}>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.ColHeader>{t("general.product")}</Table.ColHeader>
                  <Table.ColHeader>{t("general.description")}</Table.ColHeader>
                  <Table.ColHeader>{t("general.quantity_short_and_price")}</Table.ColHeader>
                  <Table.ColHeader>{t("general.tax")}</Table.ColHeader>
                  <Table.ColHeader>{t("general.total")}</Table.ColHeader>
                  <Table.ColHeader></Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Droppable droppableId="invoice_items">
                {(provided, snapshot) => (
                    <tbody 
                      ref={provided.innerRef} 
                      {...provided.droppableProps} 
                    >
                      {inputData.financeInvoice.items.edges.map(({ node }, idx) => (
                        <Draggable 
                          draggableId={node.id}
                          index={idx}
                          key={node.id}
                        >
                          {(provided, snapshot) => (
                              <tr 
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                {...provided.dragHandleProps}
                              >
                                <Table.Col>
                                  <UpdateProductName initialValues={node} />
                                </Table.Col>
                                <Table.Col>
                                  <UpdateDescription initialValues={node} />
                                </Table.Col>
                                <Table.Col>
                                  <UpdateQuantity initialValues={node} />
                                  <UpdatePrice initialValues={node} />
                                </Table.Col>
                                <Table.Col>
                                  <UpdateFinanceTaxRate initialValues={node} inputData={inputData} />
                                </Table.Col>
                                <Table.Col>
                                  <span className="pull-right">{node.totalDisplay}</span>
                                </Table.Col>
                                <Table.Col>
                                  <FinanceInvoiceItemDelete node={node} />
                                </Table.Col>
                              </tr>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </tbody>
                )}
              </Droppable>
            </Table>
          </Dimmer>
        </Card.Body>
      </Card>
    </DragDropContext>
  )
}


export default withTranslation()(withRouter(FinanceInvoiceEditItems))