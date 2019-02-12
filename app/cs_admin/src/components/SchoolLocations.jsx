import React from 'react'
import { Query } from "react-apollo";
import gql from "graphql-tag";

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
} from "tabler-react";
import SiteWrapper from "./SiteWrapper"

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
        <Page.Title className="mb-5">School</Page.Title>
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
            <Card.Header>
              <Card.Title>Locations</Card.Title>
            </Card.Header>
            <Card.Body>
              <Query query={GET_LOCATIONS}>
                {({ loading, error, data }) => {
                  if (loading) return <p>Loading...</p>
                  if (error) return <p>Error loading school locations :(</p>
                  return data.schoolLocations.map(({ id, name }) => (
                    <div key={id}>
                      <p>{id}: {name}</p>
                    </div>
                  ))
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