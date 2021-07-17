// @flow

import * as React from "react"
import { useContext } from 'react'
import { withTranslation } from 'react-i18next'
import { NavLink, withRouter } from "react-router-dom"
import { useQuery } from "react-apollo"
import { ToastContainer, Slide } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import 'react-confirm-alert/src/react-confirm-alert.css'
import { Link } from 'react-router-dom'

import { GET_SHOP_FEATURES_QUERY } from "../components/settings/shop/features/queries"
import OrganizationContext from './context/OrganizationContext'
import CSLS from "../tools/cs_local_storage"
import { get_all_permissions, has_permission } from "../tools/user_tools"


import {
  Site,
  Nav,
  Grid,
  Button,
  // Page,
  RouterContextProvider,
} from "tabler-react";

import type { NotificationProps } from "tabler-react";

type Props = {|
  +children: React.Node,
|};

type State = {|
  notificationsObjects: Array<NotificationProps>,
|};

type subNavItem = {|
  +value: string,
  +to?: string,
  +icon?: string,
  +LinkComponent?: React.ElementType,
|};

type navItem = {|
  +value: string,
  +to?: string,
  +icon?: string,
  +active?: boolean,
  +LinkComponent?: React.ElementType,
  +subItems?: Array<subNavItem>,
  +useExact?: boolean,
|};


const getNavBarItems = (t, loading, error, data) => {
  const shopFeatures = data.systemFeatureShop

  let items: Array<navItem> = []
  // let permissions = get_all_permissions(user)

  if (loading) {
    items.push({
      value: t("general.loading_with_dots"),
      to: "/",
      icon: "",
      LinkComponent: withRouter(NavLink),
      useExact: true, 
    })

    return items
  }

  if (error) {
    items.push({
      value: t("general.error_sad_smiley"),
      to: "/",
      icon: "",
      LinkComponent: withRouter(NavLink),
      useExact: true, 
    })

    return items
  }

  items.push({
    value: t("shop.home.title"),
    to: "/",
    icon: "home",
    LinkComponent: withRouter(NavLink),
    useExact: true,
  })


  if (shopFeatures.subscriptions) {
    items.push({
      value: t("shop.subscriptions.title"),
      to: "/shop/subscriptions",
      icon: "edit",
      LinkComponent: withRouter(NavLink),
      useExact: true,
    })
  }

  if (shopFeatures.classpasses) {
    items.push({
      value: t("shop.classpasses.title"),
      to: "/shop/classpasses",
      icon: "credit-card",
      LinkComponent: withRouter(NavLink),
      useExact: true,
    })
  }

  if (shopFeatures.classes) {
    items.push({
      value: t("shop.classes.title"),
      to: "/shop/classes",
      icon: "book",
      LinkComponent: withRouter(NavLink),
      useExact: true,
    })
  }

  if (shopFeatures.events) {
    items.push({
      value: t("shop.events.title"),
      to: "/shop/events",
      icon: "calendar",
      LinkComponent: withRouter(NavLink),
      useExact: true,
    })
  }

  items.push({
    value: t("shop.contact.title"),
    to: "/shop/contact",
    icon: "message-square",
    LinkComponent: withRouter(NavLink),
    useExact: true,
  })

  // Check if refresh token is present and if so, hasn't expired
  const refreshTokenExp = localStorage.getItem(CSLS.AUTH_TOKEN_REFRESH_EXP)
  let accountTitle = t("shop.account.title")
  let accountLink = "/shop/account"
  if (new Date() / 1000 >= refreshTokenExp || refreshTokenExp == null ) {
    accountTitle = t("general.sign_in")
    accountLink = "/user/login"
  }

  items.push({
    value: accountTitle,
    to: accountLink,
    icon: "user",
    LinkComponent: withRouter(NavLink),
    useExact: true,
  })

  return items
}

function getHeaderImageUrl(organization) {
  let imageURL = "/d/static/logos/stock/logo_stock_backend.svg"

  if (organization) {
    if (organization.urlLogoShopHeader) {
      imageURL = organization.urlLogoShopHeader
    }
  }

  return imageURL
}

const now = new Date()

function SiteWrapperShop({t, match, history, children}) {
  const { loading, error, data } = useQuery(GET_SHOP_FEATURES_QUERY)
  const organization = useContext(OrganizationContext)
  console.log(organization)
  // const { error, loading, data, fetchMore } = useQuery(GET_USER)

  // if (loading) return <p>{t('general.loading_with_dots')}</p>;
  // if (error) return <p>{t('system.user.error_loading')}</p>; 

  console.log(data)

  const headerImageUrl = getHeaderImageUrl(organization)

  return (
    <Site.Wrapper
      headerProps={{
          href: "/",
          alt: "Costasiella",
          imageURL: headerImageUrl, // Set logo url here
          navItems: (
            <Nav.Item type="div" className="d-none d-md-flex">
              {(data.user) ? (data.user.teacher || data.user.employee) ? <Link to="/user/welcome">
                <Button
                  className="mr-2"
                  icon="link"
                  outline
                  size="sm"
                  color="primary"
                >
                  {t('goto.title')}
                </Button>
              </Link> : "" : ""}
            </Nav.Item>
          ),
          
          // notificationsTray: {
          //   notificationsObjects,
          //   markAllAsRead: () =>
          //     this.setState(
          //       () => ({
          //         notificationsObjects: this.state.notificationsObjects.map(
          //           v => ({ ...v, unread: false })
          //         ),
          //       }),
          //       () =>
          //         setTimeout(
          //           () =>
          //             this.setState({
          //               notificationsObjects: this.state.notificationsObjects.map(
          //                 v => ({ ...v, unread: true })
          //               ),
          //             }),
          //           5000
          //         )
          //     ),
          //   unread: unreadCount,
          // },
        //   accountDropdown: {
        //   avatarURL: "#",
        //   name: data.user.firstName + ' ' + data.user.lastName,
        //   description: "",
        //   options: [
        //     // { icon: "user", value: "Profile" },
        //     { icon: "lock", value: "Change password", to: "/#/user/password/change/" },
        //     { isDivider: true },
        //     { icon: "log-out", value: "Sign out", to: "/#/user/logout/" },
        //   ],
        // },
        }}
        // navProps={{ itemsObjects: navBarItems }}
        navProps={{ itemsObjects: getNavBarItems(t, loading, error, data) }}
        routerContextComponentType={withRouter(RouterContextProvider)}
        footerProps={{
          // links: [
          //   <a href="#">First Link</a>,
          //   <a href="#">Second Link</a>,
          //   <a href="#">Third Link</a>,
          //   <a href="#">Fourth Link</a>,
          //   <a href="#">Five Link</a>,
          //   <a href="#">Sixth Link</a>,
          //   <a href="#">Seventh Link</a>,
          //   <a href="#">Eigth Link</a>,
          // ],
          // note:
          //   "Premium and Open Source dashboard template with responsive and high quality UI. For Free!",
          copyright: (
            <React.Fragment>
              Copyleft © {now.getFullYear()}.
              <a
                href="https://www.costasiella.com"
                target="_blank"
                rel="noopener noreferrer"
              >
                {" "}
                Edwin van de Ven
              </a>{". "}
              All rights reserved.
            </React.Fragment>
          ),
          nav: (
            <React.Fragment>
              <Grid.Col auto={true}>
                {/* <List className="list-inline list-inline-dots mb-0">
                  <List.Item className="list-inline-item">
                    <a href="./docs/index.html">Documentation</a>
                  </List.Item>
                  <List.Item className="list-inline-item">
                    <a href="./faq.html">FAQ</a>
                  </List.Item>
                </List> */}
              </Grid.Col>
              <Grid.Col auto={true}>
                {/* <Button
                  href="https://github.com/tabler/tabler-react"
                  size="sm"
                  outline
                  color="primary"
                  RootComponent="a"
                >
                  Source code
                </Button> */}
              </Grid.Col>
            </React.Fragment>
          ),
        }}
      >
      {children}
      <ToastContainer 
        autoClose={5000} 
        transition={Slide}
      />
    </Site.Wrapper>    
  )
}


export default withTranslation()(SiteWrapperShop)
