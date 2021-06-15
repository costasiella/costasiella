// @flow

import React, { useContext } from 'react'
import { useQuery, useMutation } from "react-apollo"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import moment from 'moment'

import {
  Dimmer,
  Button,
  Icon,
  Table
} from "tabler-react";
import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import confirm_delete from "../../../tools/confirm_delete"
import AppSettingsContext from '../../context/AppSettingsContext'
import ContentCard from "../../general/ContentCard"
import BadgeBoolean from "../../ui/BadgeBoolean"
import OrganizationAnnouncementsBase from "./OrganizationAnnouncementsBase"

import { GET_ANNOUNCEMENTS_QUERY, DELETE_ANNOUNCEMENT } from "./queries"

function OrganizationAnnouncements({ t, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat

  const { loading, error, data, fetchMore } = useQuery(GET_ANNOUNCEMENTS_QUERY)
  const [ deleteAnnouncement ] = useMutation(DELETE_ANNOUNCEMENT)

  const cardTitle = t('organization.announcements.title')

  // Loading
  if (loading) return (
    <OrganizationAnnouncementsBase>
      <ContentCard cardTitle={cardTitle}>
        <Dimmer active={true}
                loader={true}>
        </Dimmer>
      </ContentCard>
    </OrganizationAnnouncementsBase>
  )
  // Error
  if (error) return (
    <OrganizationAnnouncementsBase>
      <ContentCard cardTitle={cardTitle}>
        <p>{t('organization.announcements.error_loading')}</p>
      </ContentCard>
    </OrganizationAnnouncementsBase>
  )

  const organizationAnnouncements = data.organizationAnnouncements

  // Empty list
  if (!organizationAnnouncements.edges.length) { return (
    <OrganizationAnnouncementsBase>
      <ContentCard cardTitle={cardTitle}>
        <p>{t('organization.announcements.empty_list')}</p>
      </ContentCard>
    </OrganizationAnnouncementsBase>
  )}

  return (
    <OrganizationAnnouncementsBase>
      <ContentCard cardTitle={cardTitle}
                    pageInfo={organizationAnnouncements.pageInfo}
                    onLoadMore={() => {
                    fetchMore({
                      variables: {
                        after: organizationAnnouncements.pageInfo.endCursor
                      },
                      updateQuery: (previousResult, { fetchMoreResult }) => {
                        const newEdges = fetchMoreResult.organizationAnnouncements.edges
                        const pageInfo = fetchMoreResult.organizationAnnouncements.pageInfo

                        return newEdges.length
                          ? {
                              // Put the new organizationAnnouncements at the end of the list and update `pageInfo`
                              // so we have the new `endCursor` and `hasNextPage` values
                              organizationAnnouncements: {
                                __typename: previousResult.organizationAnnouncements.__typename,
                                edges: [ ...previousResult.organizationAnnouncements.edges, ...newEdges ],
                                pageInfo
                              }
                            }
                          : previousResult
                      }
                    })
                  }} >
        <Table>
              <Table.Header>
                <Table.Row key={v4()}>
                  <Table.ColHeader>{t('general.title')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.display_public')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.shop')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.backend')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.priority')}</Table.ColHeader>
                  <Table.ColHeader></Table.ColHeader>
                  <Table.ColHeader></Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                  {organizationAnnouncements.edges.map(({ node }) => (
                    <Table.Row key={v4()}>
                      <Table.Col key={v4()}>
                        {node.title}
                      </Table.Col>
                      <Table.Col><BadgeBoolean value={node.displayPublic} /></Table.Col>
                      <Table.Col><BadgeBoolean value={node.displayShop} /></Table.Col>
                      <Table.Col><BadgeBoolean value={node.displayBackend} /></Table.Col>
                      <Table.Col>{moment(node.dateStart).format(dateFormat)}</Table.Col>
                      <Table.Col>{(node.dateEnd) ? moment(node.dateEnd).format(dateFormat): ""}</Table.Col>
                      <Table.Col>{node.priority}</Table.Col>
                      <Table.Col className="text-right" key={v4()}>
                        <Link to={`/organization/announcements/edit/${node.id}`}>
                          <Button className='btn-sm' 
                                  color="secondary">
                            {t('general.edit')}
                          </Button>
                        </Link>
                      </Table.Col>
                      <Table.Col>
                        <button 
                          className="icon btn btn-link btn-sm" 
                          title={t('general.delete')} 
                          href=""
                          onClick={() => {
                            confirm_delete({
                              t: t,
                              msgConfirm: t("organization.announcements.delete_confirm_msg"),
                              msgDescription: <p><br />{node.title}</p>,
                              msgSuccess: t('organization.announcements.deleted'),
                              deleteFunction: deleteAnnouncement,
                              functionVariables: { variables: {
                                input: {
                                  id: node.id
                                }
                              }, refetchQueries: [
                                {query: GET_ANNOUNCEMENTS_QUERY} 
                              ]}
                            })
                        }}>
                          <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
                        </button>
                      </Table.Col>
                      {/* <Mutation mutation={ARCHIVE_LEVEL} key={v4()}>
                        {(archiveCostcenter, { data }) => (
                          <Table.Col className="text-right" key={v4()}>
                            <button className="icon btn btn-link btn-sm" 
                                title={t('general.archive')} 
                                href=""
                                onClick={() => {
                                  console.log("clicked archived")
                                  let id = node.id
                                  archiveCostcenter({ variables: {
                                    input: {
                                    id,
                                    archived: !archived
                                    }
                            }, refetchQueries: [
                                {query: GET_LEVELS_QUERY, variables: {"archived": archived }}
                            ]}).then(({ data }) => {
                              console.log('got data', data);
                              toast.success(
                                (archived) ? t('general.unarchived'): t('general.archived'), {
                                  position: toast.POSITION.BOTTOM_RIGHT
                                })
                            }).catch((error) => {
                              toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                  position: toast.POSITION.BOTTOM_RIGHT
                                })
                              console.log('there was an error sending the query', error);
                            })
                            }}>
                              <Icon prefix="fa" name="inbox" />
                            </button>
                          </Table.Col>
                        )}
                      </Mutation> */}
                    </Table.Row>
                  ))}
              </Table.Body>
            </Table>
      </ContentCard>
    </OrganizationAnnouncementsBase>
  )
}


// const OrganizationLevels = ({ t, history, archived=false }) => (
//   <SiteWrapper>
//     <div className="my-3 my-md-5">
//       <Container>
//         <Page.Header title={t("organization.title")} />
//         <Grid.Row>
//           <Grid.Col md={9}>
//             <Query query={GET_LEVELS_QUERY} variables={{ archived }}>
//              {({ loading, error, data: {organizationLevels: levels}, refetch, fetchMore }) => {
//                 // Loading
//                 if (loading) return (
//                   <ContentCard cardTitle={t('organization.levels.title')}>
//                     <Dimmer active={true}
//                             loader={true}>
//                     </Dimmer>
//                   </ContentCard>
//                 )
//                 // Error
//                 if (error) return (
//                   <ContentCard cardTitle={t('organization.levels.title')}>
//                     <p>{t('organization.levels.error_loading')}</p>
//                   </ContentCard>
//                 )
//                 const headerOptions = <Card.Options>
//                   <Button color={(!archived) ? 'primary': 'secondary'}  
//                           size="sm"
//                           onClick={() => {archived=false; refetch({archived});}}>
//                     {t('general.current')}
//                   </Button>
//                   <Button color={(archived) ? 'primary': 'secondary'} 
//                           size="sm" 
//                           className="ml-2" 
//                           onClick={() => {archived=true; refetch({archived});}}>
//                     {t('general.archive')}
//                   </Button>
//                 </Card.Options>
                
//                 // Empty list
//                 if (!levels.edges.length) { return (
//                   <ContentCard cardTitle={t('organization.levels.title')}
//                                headerContent={headerOptions}>
//                     <p>
//                     {(!archived) ? t('organization.levels.empty_list') : t("organization.levels.empty_archive")}
//                     </p>
                   
//                   </ContentCard>
//                 )} else {   
//                 // Life's good! :)
//                 return (
//                   <ContentCard cardTitle={t('organization.levels.title')}
//                                headerContent={headerOptions}
//                                pageInfo={levels.pageInfo}
//                                onLoadMore={() => {
//                                 fetchMore({
//                                   variables: {
//                                     after: levels.pageInfo.endCursor
//                                   },
//                                   updateQuery: (previousResult, { fetchMoreResult }) => {
//                                     const newEdges = fetchMoreResult.organizationLevels.edges
//                                     const pageInfo = fetchMoreResult.organizationLevels.pageInfo

//                                     return newEdges.length
//                                       ? {
//                                           // Put the new levels at the end of the list and update `pageInfo`
//                                           // so we have the new `endCursor` and `hasNextPage` values
//                                           organizationLevels: {
//                                             __typename: previousResult.organizationLevels.__typename,
//                                             edges: [ ...previousResult.organizationLevels.edges, ...newEdges ],
//                                             pageInfo
//                                           }
//                                         }
//                                       : previousResult
//                                   }
//                                 })
//                               }} >
//                     <Table>
//                           <Table.Header>
//                             <Table.Row key={v4()}>
//                               <Table.ColHeader>{t('general.name')}</Table.ColHeader>
//                             </Table.Row>
//                           </Table.Header>
//                           <Table.Body>
//                               {levels.edges.map(({ node }) => (
//                                 <Table.Row key={v4()}>
//                                   <Table.Col key={v4()}>
//                                     {node.name}
//                                   </Table.Col>
//                                   <Table.Col className="text-right" key={v4()}>
//                                     {(node.archived) ? 
//                                       <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
//                                       <Button className='btn-sm' 
//                                               onClick={() => history.push("/organization/levels/edit/" + node.id)}
//                                               color="secondary">
//                                         {t('general.edit')}
//                                       </Button>
//                                     }
//                                   </Table.Col>
//                                   <Mutation mutation={ARCHIVE_LEVEL} key={v4()}>
//                                     {(archiveCostcenter, { data }) => (
//                                       <Table.Col className="text-right" key={v4()}>
//                                         <button className="icon btn btn-link btn-sm" 
//                                            title={t('general.archive')} 
//                                            href=""
//                                            onClick={() => {
//                                              console.log("clicked archived")
//                                              let id = node.id
//                                              archiveCostcenter({ variables: {
//                                                input: {
//                                                 id,
//                                                 archived: !archived
//                                                }
//                                         }, refetchQueries: [
//                                             {query: GET_LEVELS_QUERY, variables: {"archived": archived }}
//                                         ]}).then(({ data }) => {
//                                           console.log('got data', data);
//                                           toast.success(
//                                             (archived) ? t('general.unarchived'): t('general.archived'), {
//                                               position: toast.POSITION.BOTTOM_RIGHT
//                                             })
//                                         }).catch((error) => {
//                                           toast.error((t('general.toast_server_error')) + ': ' +  error, {
//                                               position: toast.POSITION.BOTTOM_RIGHT
//                                             })
//                                           console.log('there was an error sending the query', error);
//                                         })
//                                         }}>
//                                           <Icon prefix="fa" name="inbox" />
//                                         </button>
//                                       </Table.Col>
//                                     )}
//                                   </Mutation>
//                                 </Table.Row>
//                               ))}
//                           </Table.Body>
//                         </Table>
//                   </ContentCard>
//                 )}}
//              }
//             </Query>
//           </Grid.Col>
//           <Grid.Col md={3}>
//             <HasPermissionWrapper permission="add"
//                                   resource="organizationlevel">
//               <Link to={"/organization/announcements/add"}
//               <Button color="primary btn-block mb-6"
//                       onClick={() => history.push("")}>
//                 <Icon prefix="fe" name="plus-circle" /> {t('organization.levels.add')}
//               </Button>
//             </HasPermissionWrapper>
//             <OrganizationMenu active_link='levels'/>
//           </Grid.Col>
//         </Grid.Row>
//       </Container>
//     </div>
//   </SiteWrapper>
// );

export default withTranslation()(withRouter(OrganizationAnnouncements))