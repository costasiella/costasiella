// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'
import { ToastContainer, Slide } from 'react-toastify'

import {
  Container,
  Grid,
  Page
} from "tabler-react"


function CSStandalonePageWide({ t, urlLogo="", children}) {

  return (
    <Page>
      <div className="page-single">
        <Container>
          <Grid.Row>
            <div className="col mx-auto">            
              <div className="text-center mb-5">
                { (urlLogo) ? <img src={urlLogo} className="h-9" alt="logo" /> : "" }
              </div>
              {children}
              <ToastContainer 
                autoClose={5000} 
                transition={Slide}
              />
            </div>
          </Grid.Row>
        </Container>
      </div>
    </Page>
  )
}

export default withTranslation()(CSStandalonePageWide)



