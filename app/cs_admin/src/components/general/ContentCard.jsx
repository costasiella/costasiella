import React from 'react'

import {
    Button,
    Card,
  } from "tabler-react"

const ContentCard = ({ t, cardTitle, headerContent, onLoadMore, children}) => (
    <Card>
      <Card.Header>
        <Card.Title>{cardTitle}</Card.Title>
        {headerContent}
      </Card.Header>
      <Card.Body>
        {children}
      </Card.Body>
      <Card.Footer>
        <Button onClick={onLoadMore}>
          Gimme more...
        </Button>
      </Card.Footer>
    </Card>
  )
  
  export default ContentCard