// @flow

import * as React from "react"
import { withTranslation } from 'react-i18next'
import { NavLink, withRouter } from "react-router-dom"
import { Query } from "react-apollo"
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
    to: "/",
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
    (has_permission(permissions, 'view', 'scheduleclass'))
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
    (has_permission(permissions, 'view', 'organizationmembership')) 
   ){
  items.push({
    value: t("organization.title"),
    to: "/organization",
    icon: "feather",
    LinkComponent: withRouter(NavLink),
  })
}


  return items

}

const now = new Date()

class SiteWrapperSelfCheckin extends React.Component<Props, State> {
  state = {}  

  render(): React.Node {
    return (
      <Query query={GET_USER} >
        {({ loading, error, data }) => {
          if (loading) return <p>{this.props.t('general.loading_with_dots')}</p>;
          if (error) return <p>{this.props.t('system.user.error_loading')}</p>; 
          
          console.log('user data in site wrapper')
          console.log(data)
      
          return <Site.Wrapper
            headerProps={{
                href: "/",
                alt: "Costasiella",
                imageURL: "/d/static/logos/stock/logo_stock_backend.svg", // Set logo url here
                // navItems: (
                //   <Nav.Item type="div" className="d-none d-md-flex">
                //     <Link to="/settings/general">
                //       <Button
                //         icon="settings"
                //         outline
                //         size="sm"
                //         color="primary"
                //       >
                //         {this.props.t('general.settings')}
                //       </Button>
                //     </Link>
                //   </Nav.Item>
                // ),
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
                  { icon: "lock", value: "Change password", to: "/#/user/password/change/" },
                  { isDivider: true },
                  { icon: "log-out", value: "Sign out", to: "/#/user/logout/" },
                ],
              },
              }}
              // navProps={{ itemsObjects: navBarItems }}
              // navProps={{ itemsObjects: getNavBarItems(this.props.t, data.user) }}
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
              {this.props.children}
              <ToastContainer 
                autoClose={5000} 
                transition={Slide}
              />
            </Site.Wrapper>
          }}
        </Query>
    );
  }
}

export default withTranslation()(SiteWrapperSelfCheckin)
