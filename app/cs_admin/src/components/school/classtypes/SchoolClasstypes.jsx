import React from 'react'
import { Query, Mutation } from "react-apollo"
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
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import ContentCard from "../../general/ContentCard"
import SchoolMenu from "../SchoolMenu"

import { GET_CLASSTYPES_QUERY } from "./queries"

const ARCHIVE_CLASSTYPE = gql`
    mutation ArchiveSchoolLocation($id: ID!, $archived: Boolean!) {
        archiveSchoolLocation(id: $id, archived: $archived) {
          schoolLocation {
            id
            archived
          }
        }
    }
`


const onClickArchive = (t, id) => {
  const options = {
    title: t('please_confirm'),
    message: t('school.classtypes.confirm_archive'),
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


const SchoolClasstypes = ({ t, history, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title="School" />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_CLASSTYPES_QUERY} variables={{ archived }}>
             {({ loading, error, data, refetch }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('school.classtypes.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('school.classtypes.title')}>
                    <p>{t('school.classtypes.error_loading')}</p>
                  </ContentCard>
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
                if (!data.schoolClasstypes.length) { return (
                  <ContentCard cardTitle={t('school.classtypes.title')}
                               header_content={headerOptions}>
                    <p>
                    {(!archived) ? t('school.classtypes.empty_list') : t("school.classtypes.empty_archive")}
                    </p>
                   
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  <ContentCard cardTitle={t('school.classtypes.title')}
                               header_content={headerOptions}>
                    <Table>
                          <Table.Header>
                            <Table.Row key={v4()}>
                              <Table.ColHeader>{t('name')}</Table.ColHeader>
                              <Table.ColHeader>{t('public')}</Table.ColHeader>
                              <Table.ColHeader>{t('description')}</Table.ColHeader>
                            </Table.Row>
                          </Table.Header>
                          <Table.Body>
                              {data.schoolClasstypes.map(({ id, name, description, displayPublic }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col key={v4()}>
                                    {name}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    {(displayPublic) ? 
                                      <Badge color="success">{t('yes')}</Badge>: 
                                      <Badge color="danger">{t('no')}</Badge>}
                                  </Table.Col>
                                  <Table.Col key={v4()}>
                                    <span title={description}>
                                      {description}
                                    </span>
                                  </Table.Col>
                                  <Table.Col className="text-right" key={v4()}>
                                    {(archived) ? 
                                      <span className='text-muted'>{t('unarchive_to_edit')}</span> :
                                      <Button className='btn-sm' 
                                              onClick={() => history.push("/school/classtypes/edit/" + id)}
                                              color="secondary">
                                        {t('edit')}
                                      </Button>
                                    }
                                  </Table.Col>
                                  <Mutation mutation={ARCHIVE_CLASSTYPE} key={v4()}>
                                    {(archiveLocation, { data }) => (
                                      <Table.Col className="text-right" key={v4()}>
                                        <a className="icon" 
                                           title={t('archive')} 
                                           onClick={() => {
                                             console.log("clicked archived")
                                             archiveLocation({ variables: {
                                              id,
                                              archived: !archived
                                        }, refetchQueries: [
                                            {query: GET_CLASSTYPES_QUERY, variables: {"archived": archived }}
                                        ]}).then(({ data }) => {
                                          console.log('got data', data);
                                          toast.success(
                                            (archived) ? t('unarchived'): t('archived'), {
                                              position: toast.POSITION.BOTTOM_RIGHT
                                            })
                                        }).catch((error) => {
                                          toast.error((t('toast_server_error')) + ': ' +  error, {
                                              position: toast.POSITION.BOTTOM_RIGHT
                                            })
                                          console.log('there was an error sending the query', error);
                                        })
                                        }}>
                                          <Icon prefix="fa" name="inbox" />
                                        </a>
                                      </Table.Col>
                                    )}
                                  </Mutation>
                                </Table.Row>
                              ))}
                          </Table.Body>
                        </Table>
                  </ContentCard>
                )}}
             }
            </Query>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="schoolclasstype">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/school/classtypes/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('school.classtypes.add')}
              </Button>
            </HasPermissionWrapper>
            <SchoolMenu active_link='schoolclasstypes'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(SchoolClasstypes))