// @flow

import React, { Fragment } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Card
} from "tabler-react";


const FinanceInvoiceEditOrganization = ({ t, history, organization }) => (
  <Card statusColor="blue">
    <Card.Header>
      <Card.Title>{t('general.from')}</Card.Title>
    </Card.Header>
    <Card.Body>
      <div className="bold">
        {organization.name}
      </div>
      {(organization.address) ?
        <div dangerouslySetInnerHTML={{ __html: organization.address}} />
        : ""
      }      
      <div>
        {organization.phone}
      </div>
      <div>
        {organization.email}
      </div>
      <div>
        {organization.registration}
      </div>
      <div>
        {organization.taxRegistration}
      </div>
    </Card.Body>
  </Card>
)

export default withTranslation()(withRouter(FinanceInvoiceEditOrganization))