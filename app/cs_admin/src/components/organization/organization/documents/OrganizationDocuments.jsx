// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import OrganizationMenu from "../../OrganizationMenu"


function OrganizationDocuments({ t, match }) {
  const organizationId = match.params.organization_id
  const docTypes = [
    [ "TERMS_AND_CONDITIONS", t("general.terms_and_conditions")],
    [ "PRIVACY_POLICY", t("general.privacy_policy")],
  ]


  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('organization.title')}>
            <div className="page-options d-flex">
              <Link to={`/organization/edit/${organizationId}`}>
                <Button 
                  icon="arrow-left"
                  className="mr-2"
                  outline
                  color="secondary"
                >
                  {t('general.back_to')} {t('organization.title')}
                </Button>
              </Link>
            </div>
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('organization.documents.title')}</Card.Title>
                </Card.Header>
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
                              <Link to={`/organization/documents/${organizationId}/${docType[0]}`}>
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