// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import {
  Container,
  Icon,
  Page
} from "tabler-react";
import SiteWrapperShop from "../../../SiteWrapperShop"


function ShopAccountClassInfoBase({ t, match, history, children, accountName="" }) {
  return (
      <SiteWrapperShop>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header 
              title={t("shop.account.title")} 
              subTitle={ accountName }
            >
              <div className="page-options d-flex">
                <Link to={"/shop/account/classes"}
                      className='btn btn-secondary'>
                  <Icon prefix="fe" name="arrow-left" /> {t('general.back')} 
                </Link>
              </div>
            </Page.Header>
            { children }
          </Container>
        </div>
      </SiteWrapperShop>
  )
}

export default withTranslation()(withRouter(ShopAccountClassInfoBase))