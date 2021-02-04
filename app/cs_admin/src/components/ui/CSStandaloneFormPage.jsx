// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'
import { ToastContainer } from 'react-toastify'

import {
  Container,
  Grid,
  Page
} from "tabler-react"


function CSStandalonePage({ t, urlLogo="", children}) {

  return (
    <Page>
      <div className="page-single">
        <Container>
          <Grid.Row>
            <div className="col col-login mx-auto">            
              <div className="text-center mb-5">
                <img src={urlLogo} className="h-9" alt="logo" />
              </div>
              {children}
              <ToastContainer autoClose={5000}/>
            </div>
          </Grid.Row>
        </Container>
      </div>
    </Page>
  )
}

export default withTranslation()(CSStandalonePage)



