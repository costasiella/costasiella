// @flow

import * as React from "react"
import { withTranslation } from 'react-i18next'
import { NavLink, withRouter } from "react-router-dom"
import { useQuery, Query } from "react-apollo"
import { ToastContainer, Slide } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import 'react-confirm-alert/src/react-confirm-alert.css'
import { Link } from 'react-router-dom'

import GET_USER from "../queries/system/get_user"
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


const getNavBarItems = (t, user) => {
  let items: Array<navItem> = []
  let permissions = get_all_permissions(user)

  items.push({
    value: t("home.title"),
    to: "/backend",
    icon: "home",
    LinkComponent: withRouter(NavLink),
    useExact: true,
  })

  // Relations
  if (
    (has_permission(permissions, 'view', 'account'))
  ){
    items.push({
      value: t("relations.title"),
      to: "/relations",
      icon: "users",
      LinkComponent: withRouter(NavLink),
    })
  }

  // Schedule
  if (
    (has_permission(permissions, 'view', 'scheduleclass')) ||
    (has_permission(permissions, 'view', 'scheduleevent'))
  ){
    items.push({
      value: t("schedule.title"),
      to: "/schedule",
      icon: "calendar",
      LinkComponent: withRouter(NavLink),
    })
  }

  // Finance
  if (
    (has_permission(permissions, 'view', 'financecostcenter')) ||
    (has_permission(permissions, 'view', 'financeglaccount')) ||
    (has_permission(permissions, 'view', 'financetaxrate')) 
  ){
    items.push({
      value: t("finance.title"),
      to: "/finance",
      icon: "dollar-sign",
      LinkComponent: withRouter(NavLink),
    })
  }

  // Organization
  if (
    (has_permission(permissions, 'view', 'organizationclasspass')) || 
    (has_permission(permissions, 'view', 'organizationclasstype')) ||
    (has_permission(permissions, 'view', 'organizationdiscovery')) ||
    (has_permission(permissions, 'view', 'organizationlocation')) ||
    (has_permission(permissions, 'view', 'organizationmembership')) ||  
    (has_permission(permissions, 'view', 'organization')) 
   ){
   items.push({
      value: t("organization.title"),
      to: "/organization",
      icon: "feather",
      LinkComponent: withRouter(NavLink),
    })
  }

  // Insight
  if (
    (has_permission(permissions, 'view', 'insight'))
   ){
    items.push({
      value: t("insight.title"),
      to: "/insight",
      icon: "bar-chart-2",
      LinkComponent: withRouter(NavLink),
    })
  }

  // Automation
  if (
    (has_permission(permissions, 'view', 'automation'))
   ){
    items.push({
      value: t("automation.title"),
      to: "/automation",
      icon: "loader",
      LinkComponent: withRouter(NavLink),
    })
  }

  // let goToSubItems = []
  // if (has_permission(permissions, 'view', 'selfcheckin')) {
  //   goToSubItems.push(
  //     { value: t("selfcheckin.home.title"), to: "/selfcheckin", LinkComponent: withRouter(NavLink) }
  //   )
  // }
  // goToSubItems.push(
  //   { value: t("shop.title"), to: "/shop", LinkComponent: withRouter(NavLink) }
  // )

  // // Go to
  // if (
  //   (has_permission(permissions, 'view', 'selfcheckin'))
  //  ){
  //   items.push({
  //     value: t("goto.title"),
  //     icon: "link",
  //     subItems: goToSubItems,
  //   })
  // }


  return items

}

const now = new Date()

function SiteWrapper({t, match, history, children}) {
  const { error, loading, data, fetchMore } = useQuery(GET_USER)

  if (loading) return <p>{t('general.loading_with_dots')}</p>;
  if (error) return <p>{t('system.user.error_loading')}</p>; 

  console.log(data)

  return (
    <Site.Wrapper
      headerProps={{
          href: "/",
          alt: "Costasiella",
          imageURL: "/d/static/logos/stock/logo_stock_backend.svg", // Set logo url here
          navItems: (
            <Nav.Item type="div" className="d-none d-md-flex">
              <Link to="/settings">
                <Button
                  className="mr-2"
                  icon="settings"
                  outline
                  size="sm"
                  color="primary"
                >
                  {t('general.settings')}
                </Button>
              </Link>
              <Link to="/user/welcome">
                <Button
                  className="mr-2"
                  icon="link"
                  outline
                  size="sm"
                  color="primary"
                >
                  {t('goto.title')}
                </Button>
              </Link>
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
          accountDropdown: {
          avatarURL: "#",
          name: data.user.firstName + ' ' + data.user.lastName,
          description: "",
          options: [
            // { icon: "user", value: "Profile" },
            { icon: "lock", value: t("user.change_password.title"), to: "/#/user/password/change/" },
            { isDivider: true },
            { icon: "user", value: t("shop.account.title"), to: "/#/shop/account/" },
            { isDivider: true },
            { icon: "log-out", value: t("user.logout.title"), to: "/#/user/logout/" },
          ],
        },
        }}
        // navProps={{ itemsObjects: navBarItems }}
        navProps={{ itemsObjects: getNavBarItems(t, data.user) }}
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

export default withTranslation()(SiteWrapper)
