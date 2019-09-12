// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


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
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../../general/ContentCard"
import OrganizationMenu from "../../OrganizationMenu"


function OrganizationDocuments({ t }) {
  const docTypes = [
    [ "TERMS_AND_CONDITATIONS", t("general.terms_and_conditions")],
    [ "PRIVACY_POLICY", t("general.privacy_policy")],
  ]


  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('organization.title')} />
          <Grid.Row>
            <Grid.Col md={9}>
              <Card>
                <Card.Title>{t('organization.documents.title')}</Card.Title>
                <Card.Body>
                  <Table>
                    <Table.Header>
                      <Table.Row key={v4()}>
                        <Table.ColHeader>{t('general.document')}</Table.ColHeader>
                        <Table.ColHeader></Table.ColHeader>
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {docTypes.map((docType) => (
                          <Table.Row key={v4()}>
                            <Table.Col key={v4()}>
                              {docType[1]}
                            </Table.Col>
                            <Table.Col className="text-right" key={v4()}>
                              <Link to={`"/organization/documents/${docType[0]}"`}>
                                <Button className='btn-sm' 
                                        color="secondary">
                                  {t('general.manage')} <Icon name="chevron-right" />
                                </Button>
                              </Link>
                            </Table.Col>
                          </Table.Row>
                        ))}
                    </Table.Body>
                  </Table>
                </Card.Body>
              </Card>        
            </Grid.Col>
            <Grid.Col md={3}>
              <OrganizationMenu active_link='organization'/>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(OrganizationDocuments))