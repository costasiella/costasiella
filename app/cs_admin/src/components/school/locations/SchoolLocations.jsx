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
import { confirmAlert } from 'react-confirm-alert'; // Import

import SchoolMenu from "../SchoolMenu"
import SchoolLocationsCard from "./SchoolLocationsCard"

export const GET_LOCATIONS_QUERY = gql`
  query SchoolLocations($archived: Boolean!) {
    schoolLocations(archived:$archived) {
      id
      name
      displayPublic
      archived
    }
  }
`

const onClickArchive = (t, id) => {
  const options = {
    title: t('please_confirm'),
    message: t('school.locations.confirm_archive'),
    buttons: [
      {
        label: t('yes'),
        onClick: () => alert('Click Yes'),
        class: 'btn btn-primary'
      },
      {
        label: t('no'),
        onClick: () => alert('Click No')
      }
    ],
    childrenElement: () => <div />,
    // customUI: ({ title, message, onClose }) => <div>Custom UI</div>,
    willUnmount: () => {}
  }

  confirmAlert(options)
}


const SchoolLocations = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title="School" />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_LOCATIONS_QUERY} variables={{ archived }}>
             {({ loading, error, data, refetch }) => {
                // Loading
                if (loading) return (
                  <SchoolLocationsCard>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </SchoolLocationsCard>
                )
                // Error
                if (error) return (
                  <SchoolLocationsCard>
                    <p>{t('school.locations.error_loading')}</p>
                  </SchoolLocationsCard>
                )
                const headerOptions = <Card.Options>
                  <Button color={(!archived) ? 'primary': 'secondary'}  
                          size="sm"
                          onClick={() => {archived=false; refetch({archived});}}>
                    {t('current')}
                  </Button>
                  <Button color={(archived) ? 'primary': 'secondary'} 
                          size="sm" 
                          className="ml-2" 
                          onClick={() => {archived=true; refetch({archived});}}>
                    {t('archive')}
                  </Button>
                </Card.Options>
                
                // Empty list
                if (!data.schoolLocations.length) { return (
                  <SchoolLocationsCard header_content={headerOptions}>
                    <p>
                    {(!archived) ? t('school.locations.empty_list') : t("school.locations.empty_archive")}
                    </p>
                   
                  </SchoolLocationsCard>
                )} else {   
                // Life's good! :)
                return (
                  <SchoolLocationsCard header_content={headerOptions}>
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
                                  <Table.Col className="text-right" key={v4()}>
                                    <Button className='btn-sm' 
                                            onClick={() => history.push("/school/locations/edit/" + id)}
                                            color="secondary">
                                      {t('edit')}
                                    </Button>
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    <a className="icon" title={t('archive')} onClick={() => onClickArchive(t, id)}><Icon prefix="fa" name="inbox"></Icon></a>
                                  </Table.Col>
                                </Table.Row>
                              ))}
                          </Table.Body>
                        </Table>
                  </SchoolLocationsCard>
                )}}
             }
            </Query>
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