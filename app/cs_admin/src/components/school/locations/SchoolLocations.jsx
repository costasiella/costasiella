import React from 'react'
import { Query } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


// @flow

import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Badge,
  Button,
  Card,
  Container,
  List,
  Form,
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import SchoolMenu from "../SchoolMenu"

export const GET_LOCATIONS_QUERY = gql`
  {
    schoolLocations {
        id
        name
        displayPublic
    }
  }
`


const SchoolLocations = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title="School" />
        <Grid.Row>
          <Grid.Col md={9}>
          <Card>
            <Card.Header>
              <Card.Title>{t('school.locations.title')}</Card.Title>
            </Card.Header>
            <Card.Body>
              <Query query={GET_LOCATIONS_QUERY}>
                {({ loading, error, data, refetch }) => {
                  // Loading
                  if (loading) return (
                    <Dimmer active={true}
                            loader={true} />
                  )
                  // Error
                  if (error) return <p>{t('school.locations.error_loading')}</p>
                  // Empty list
                  if (!data.schoolLocations) {
                    return t('school.locations.empty_list')
                  } else {
                    // Life's good! :)
                    return (
                      <Table>
                        <Table.Header>
                          <Table.Row key={v4()}>
                            <Table.ColHeader>{t('name')}</Table.ColHeader>
                            <Table.ColHeader>{t('public')}</Table.ColHeader>
                          </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {console.log(data.schoolLocations)}
                            {data.schoolLocations.map(({ id, name, displayPublic }) => (
                              <Table.Row key={v4()}>
                                <Table.Col key={v4()}>
                                  {name}
                                </Table.Col>
                                <Table.Col key={v4()}>
                                  {(displayPublic) ? 
                                    <Badge color="success">{t('yes')}</Badge>: 
                                    <Badge color="danger">{t('no')}</Badge>}
                                </Table.Col>
                              </Table.Row>
                            ))}
                        </Table.Body>
                      </Table>
                    )
                  }
                }}
              </Query>
            </Card.Body>
          </Card>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="schoollocation">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/school/locations/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('school.locations.add')}
              </Button>
            </HasPermissionWrapper>
            <SchoolMenu active_link='schoollocation'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(SchoolLocations))