import React from 'react'
import { withTranslation } from 'react-i18next'

import {
    Card,
  } from "tabler-react";

const SchoolLocationsCard = ({ t, header_content, children}) => (
    <Card>
      <Card.Header>
        <Card.Title>{t('school.locations.title')}</Card.Title>
        {header_content}
      </Card.Header>
      <Card.Body>
        {children}
      </Card.Body>
    </Card>
  )
  
  export default withTranslation()(SchoolLocationsCard)