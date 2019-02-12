import React from 'react'
import { Query } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"


// @flow

import {
  Page,
  Grid,
  Badge,
  Button,
  Card,
  Container,
  List,
  Form,
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"

const GET_LOCATIONS = gql`
  {
    schoolLocations {
        id
        name
    }
  }
`


const SchoolLocations = () => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title="School"
                     subTitle="Locations"/>

        <Grid.Row>
          <Grid.Col md={3}>
            <div>
                <List.Group transparent={true}>
                  <List.GroupItem
                    className="d-flex align-items-center"
                    to="#/school/locations"
                    icon="home"
                    active
                  >
                    Locations
                  </List.GroupItem>
                </List.Group>
              </div>
          </Grid.Col>
          <Grid.Col md={9}>
          <Card>
            {/* <Card.Header>
              <Card.Title>Locations</Card.Title>
            </Card.Header> */}
            <Card.Body>
              <Query query={GET_LOCATIONS}>
                {({ loading, error, data }) => {
                  if (loading) return <p>Loading...</p>
                  if (error) return <p>Error loading school locations :(</p>
                  if (!data.schoolLocations.length) {
                    return "no locations found."
                  } else {
                    return (
                      <Table>
                        <Table.Header>
                          <Table.Row key={v4()}>
                            <Table.ColHeader>Name</Table.ColHeader>
                          </Table.Row>
                        </Table.Header>
                        <Table.Body>
                           {data.schoolLocations.map(({ id, name }) => (
                              <Table.Row key={v4()}>
                                <Table.Col key={v4()}>
                                  {name}
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
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default SchoolLocations