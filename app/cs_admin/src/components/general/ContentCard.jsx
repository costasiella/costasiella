import React from 'react'
import { withTranslation } from 'react-i18next'

import {
    Button,
    Card,
  } from "tabler-react"

const ContentCard = ({ t, cardTitle, headerContent, page, pageInfo, onLoadPrevious, onLoadNext, children}) => (
    <Card>
      <Card.Header>
        <Card.Title>{cardTitle}</Card.Title>
        {headerContent}
      </Card.Header>
      <Card.Body>
        {children}
      </Card.Body>
      <Card.Footer>
        <div className="pull-right">{t("page")} {page}</div>
        {console.log('pageInfo in CC')}
        {console.log(pageInfo)}
        {
          (!pageInfo) ? "" :
            <div>
              <Button onClick={onLoadPrevious} disabled={!pageInfo.hasPreviousPage}>
                What came before...?
              </Button>
              <Button onClick={onLoadNext} disabled={!pageInfo.hasNextPage}>
                What's next...?
              </Button>
            </div>
        }

      </Card.Footer>
    </Card>
  )
  
  export default withTranslation()(ContentCard)