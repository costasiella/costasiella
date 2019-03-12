import React from 'react'

import {
    Card,
  } from "tabler-react"

const ContentCard = ({ t, cardTitle, headerContent, children}) => (
    <Card>
      <Card.Header>
        <Card.Title>{cardTitle}</Card.Title>
        {headerContent}
      </Card.Header>
      <Card.Body>
        {children}
      </Card.Body>
    </Card>
  )
  
  export default ContentCard