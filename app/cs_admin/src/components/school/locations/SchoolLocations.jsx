import React from 'react'
import { Query } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


// @flow

import {
  Page,
  Grid,
  Icon,
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

const GET_LOCATIONS = gql`
  {
    schoolLocations {
        id
        name
        displayPublic
    }
  }
`


const SchoolLocations = ({ t }) => (
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
              <Query query={GET_LOCATIONS}>
                {({ loading, error, data }) => {
                  if (loading) return <p>{t('messages.loading')}</p>
                  if (error) return <p>{t('school.locations.error_loading')}</p>
                  if (!data.schoolLocations) {
                    return t('school.locations.empty_list') //"No locations found."
                  } else {
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
                                  {(displayPublic) ? 'yep': 'nope'}
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
              <Button color="primary btn-block mb-6">
                <Icon prefix="fe" name="plus-circle" /> {t('add')}
              </Button>
            </HasPermissionWrapper>
            <SchoolMenu active_link='schoollocation'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(SchoolLocations)