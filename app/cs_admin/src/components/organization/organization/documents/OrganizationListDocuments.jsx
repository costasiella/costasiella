// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"


import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Badge,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import ISODateString from "../../../ui/ISODateString"
import FileDownloadTableButton from "../../../ui/FileDownloadTableButton"
import ContentCard from "../../../general/ContentCard"
import OrganizationMenu from "../../OrganizationMenu"
import OrganizationDocumentsBase from "./OrganizationDocumentsBase"
import OrganizationDocumentsDelete from "./OrganizationDocumentDelete"

import { GET_DOCUMENTS_QUERY, DELETE_DOCUMENT } from "./queries"


function OrganizationListDocuments({ t, match, history }) {
  const organizationId = match.params.organization_id
  const documentType = match.params.document_type
  const back = <Link to={`/organization/documents/${organizationId}`}>
    <Button 
      icon="arrow-left"
      className="mr-2"
      outline
      color="secondary"
    >
      {t('general.back_to')} {t('organization.documents.title')}
    </Button>
  </Link>
  const sidebarButton = <HasPermissionWrapper 
    permission="add"
    resource="organizationdocument">
      <Link to={`/organization/documents/${organizationId}/${documentType}/add`} >
        <Button color="primary btn-block mb-6" >
          <Icon prefix="fe" name="plus-circle" /> {t('organization.documents.add')}
        </Button>
      </Link>
  </HasPermissionWrapper>

  const { loading, error, data, fetchMore } = useQuery(GET_DOCUMENTS_QUERY, {
    variables: { documentType: documentType }
  })

  if (loading) {
    return (
      <OrganizationDocumentsBase headerLinks={back}>
        {t('general.loading_with_dots')}
      </OrganizationDocumentsBase>
    )
  }

  if (error) {
    return (
      <OrganizationDocumentsBase headerLinks={back}>
        {t('organization.documents.error_loading')}
      </OrganizationDocumentsBase>
    )
  }
  

  return (
    <OrganizationDocumentsBase headerLinks={back} sidebarButton={sidebarButton}>
      <ContentCard 
        cardTitle={t('organization.documents.title')}
        pageInfo={data.organizationDocuments.pageInfo}
        onLoadMore={() => {
          fetchMore({
            variables: {
              after: data.organizationDocuments.pageInfo.endCursor
            },
            updateQuery: (previousResult, { fetchMoreResult }) => {
              const newEdges = fetchMoreResult.organizationDocuments.edges
              const pageInfo = fetchMoreResult.organizationDocuments.pageInfo

              return newEdges.length
                ? {
                    // Put the fetched documents at the end of the list and update `pageInfo`
                    // so we have the new `endCursor` and `hasNextPage` values
                    organizationDocuments: {
                      __typename: previousResult.organizationDocuments.__typename,
                      edges: [ ...previousResult.organizationDocuments.edges, ...newEdges ],
                      pageInfo
                    }
                  }
                : previousResult
            }
          })
        }}
      >
        <Table>
              <Table.Header>
                <Table.Row key={v4()}>
                  <Table.ColHeader>{t('general.date')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.version')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.download')}</Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                  {data.organizationDocuments.edges.map(({ node }) => (
                    <Table.Row key={v4()}>
                      <Table.Col key={v4()}>
                        <ISODateString ISODateStr={node.dateStart} />
                        {(node.dateEnd) ? <span> - <ISODateString ISODateStr={node.dateEnd} /></span> : ""}
                      </Table.Col>
                      <Table.Col key={v4()}>
                        {node.version}
                      </Table.Col>
                      <Table.Col key={v4()}>
                        <FileDownloadTableButton mediaUrl={node.urlDocument} />
                      </Table.Col>
                      <Table.Col className="text-right" key={v4()}>
                        <Link to={`/organization/documents/${organizationId}/${documentType}/edit/${node.id}`} >
                          <Button className='btn-sm' 
                                  color="secondary">
                            {t('general.edit')}
                          </Button>
                        </Link>
                        <OrganizationDocumentsDelete node={node} />
                      </Table.Col>
                    </Table.Row>
                  ))}
              </Table.Body>
            </Table>
      </ContentCard>
    </OrganizationDocumentsBase>
  )

}

export default withTranslation()(withRouter(OrganizationListDocuments))