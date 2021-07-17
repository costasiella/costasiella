// @flow

import React from 'react'
import { useQuery } from '@apollo/react-hooks'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { GET_BACKEND_ANNOUNCEMENTS_QUERY } from "./queries"

import HomeHomeBase from './HomeHomeBase';


function HomeHome({ t, match }) {
  const { loading, error, data } = useQuery(GET_BACKEND_ANNOUNCEMENTS_QUERY);

  if (loading) return (
    <HomeHomeBase>
      {t("general.loading_with_dots")}
    </HomeHomeBase>
  )
  if (error) return (
    <HomeHomeBase>
      {t("shop.home.announcements.error_loading")}
    </HomeHomeBase>
  )

  console.log("%%%%%%%%%%%%%%%%%%%%%")
  console.log(data)

  const announcements = data.organizationAnnouncements

  return (
    <HomeHomeBase>
      <Grid.Row>
        {(announcements.edges.length) ? announcements.edges.map(({ node }) => (
          <Grid.Col md={6}>
            <Card title={node.title}>
              <Card.Body>
                <div dangerouslySetInnerHTML={{ __html:node.content }}></div>
              </Card.Body>
            </Card> 
          </Grid.Col>
        )) : ""
        }
      </Grid.Row>
    </HomeHomeBase>
  )
}


// class HomeHome extends Component {
//   constructor(props) {
//     super(props)
//     console.log("Home home props:")
//     console.log(props)
//   }


//   render() {
//     const t = this.props.t
//     const match = this.props.match
//     const history = this.props.history
//     const id = match.params.id

//     return (
//       <SiteWrapper>
//         <div className="my-3 my-md-5">
//           <Container>
//             <Page.Header title={t("home.title")} />
//             <Grid.Row>
//               <Grid.Col md={9}>
//               <Card>
//                 <Card.Header>
//                   <Card.Title>{t('home.title')}</Card.Title>
//                 </Card.Header>
//                 <Card.Body>
//                     Hello world!
//                 </Card.Body>
//               </Card>
//               </Grid.Col>
//             </Grid.Row>
//           </Container>
//         </div>
//     </SiteWrapper>
//     )}
//   }


export default withTranslation()(withRouter(HomeHome))