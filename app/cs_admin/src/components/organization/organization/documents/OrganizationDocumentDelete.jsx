import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { DELETE_DOCUMENT, GET_DOCUMENTS_QUERY } from "../queries"
import confirmDelete from "../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"


function OrganizationDocumentDelete({t, match, node}) {
  const [deleteOrganizationDocument, { data }] = useMutation(DELETE_DOCUMENT)

  return (
    <button className="icon btn btn-link btn-sm" 
      title={t('general.delete')} 
      href=""
      onClick={() => {
        confirmDelete({
          t: t,
          msgConfirm: t("organization.documents.delete_confirm_msg"),
          msgDescription: <p>{node.version}</p>,
          msgSuccess: t('organization.documents.deleted'),
          deleteFunction: deleteOrganizationDocument,
          functionVariables: { 
            variables: {
              input: { id: node.id }
            }, 
            refetchQueries: [
              {query: GET_DOCUMENTS_QUERY, variables: { documentType: node.documentType} },
            ]
          }
        })
    }}>
      <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
    </button>
  )
}


export default withTranslation()(withRouter(OrganizationDocumentDelete))
