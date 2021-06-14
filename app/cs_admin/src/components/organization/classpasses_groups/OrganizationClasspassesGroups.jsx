// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


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
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import confirm_delete from "../../../tools/confirm_delete"
import ContentCard from "../../general/ContentCard"
import CardHeaderSeparator from "../../general/CardHeaderSeparator"
import OrganizationMenu from "../OrganizationMenu"
import OrganizationClasspassesGroupsBase from "./OrganizationClasspassesGroupsBase"

import { GET_CLASSPASS_GROUPS_QUERY, DELETE_CLASSPASS_GROUP } from "./queries"


function OrganizationClasspassesGroups({ t, history}) {
  const { loading, error, data, fetchMore } = useQuery(GET_CLASSPASS_GROUPS_QUERY)
  const [deleteClasspassGroup] = useMutation(DELETE_CLASSPASS_GROUP)

  // Loading
  if (loading) return (
    <OrganizationClasspassesGroupsBase>
      <ContentCard cardTitle={t('organization.classpass_groups.title')}>
        <Dimmer active={true}
                loader={true}>
        </Dimmer>
      </ContentCard>
    </OrganizationClasspassesGroupsBase>
  )
  // Error
  if (error) return (
    <OrganizationClasspassesGroupsBase>
      <ContentCard cardTitle={t('organization.classpass_groups.title')}>
        <p>{t('organization.classpass_groups.error_loading')}</p>
      </ContentCard>
    </OrganizationClasspassesGroupsBase>
  )
  
  const classpass_groups = data.organizationClasspassGroups

  // Empty list
  if (!classpass_groups.edges.length) { return (
    <OrganizationClasspassesGroupsBase>
      <ContentCard cardTitle={t('organization.classpass_groups.title')}>
        <p>{t('organization.classpass_groups.empty_list')}</p>
      </ContentCard>
    </OrganizationClasspassesGroupsBase>
  )} 

  
  // We have data
  return (
    <OrganizationClasspassesGroupsBase>
      <ContentCard cardTitle={t('organization.classpass_groups.title')}
                    pageInfo={classpass_groups.pageInfo}
                    onLoadMore={() => {
                    fetchMore({
                      variables: {
                        after: classpass_groups.pageInfo.endCursor
                      },
                      updateQuery: (previousResult, { fetchMoreResult }) => {
                        const newEdges = fetchMoreResult.organizationClasspassGroups.edges
                        const pageInfo = fetchMoreResult.organizationClasspassGroups.pageInfo

                        return newEdges.length
                          ? {
                              // Put the new classpass_groups at the end of the list and update `pageInfo`
                              // so we have the new `endCursor` and `hasNextPage` values
                              organizationClasspassGroups: {
                                __typename: previousResult.organizationClasspassGroups.__typename,
                                edges: [ ...previousResult.organizationClasspassGroups.edges, ...newEdges ],
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
                  <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.description')}</Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {classpass_groups.edges.map(({ node }) => (
                  <Table.Row key={v4()}>
                    <Table.Col key={v4()}>
                      {node.name}
                    </Table.Col>
                    <Table.Col key={v4()}>
                      {node.description.substring(0, 24)}
                    </Table.Col>
                    <Table.Col className="text-right" key={v4()}>
                        <Button className='btn-sm' 
                                onClick={() => history.push("/organization/classpasses/groups/edit/" + node.id)}
                                color="secondary">
                          {t('general.edit')}
                        </Button>
                        <Button className='btn-sm' 
                                onClick={() => history.push("/organization/classpasses/groups/edit/passes/" + node.id)}
                                color="secondary">
                          {t('organization.classpasses.groups.edit_passes')}
                        </Button>
                    </Table.Col>
                    <Table.Col>
                      <button className="icon btn btn-link btn-sm float-right" 
                        title={t('general.delete')} 
                        href=""
                        onClick={() => {
                          confirm_delete({
                            t: t,
                            msgConfirm: t("organization.classpasses.groups.delete_confirm_msg"),
                            msgDescription: <p>{node.name}</p>,
                            msgSuccess: t('organization.classpasses.groups.deleted'),
                            deleteFunction: deleteClasspassGroup,
                            functionVariables: { variables: {
                              input: {
                                id: node.id
                              }
                            }, refetchQueries: [
                              {query: GET_CLASSPASS_GROUPS_QUERY} 
                            ]}
                          })
                      }}>
                        <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
                      </button>
                    </Table.Col>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
      </ContentCard>
    </OrganizationClasspassesGroupsBase>
   )

}



// const OrganizationClasspassesGroups = ({ t, history }) => (
//   <SiteWrapper>
//     <div className="my-3 my-md-5">
//       <Container>
//         <Page.Header title={t("organization.title")}>
//           <div className="page-options d-flex">
//             <Link to="/organization/classpasses" 
//                   className='btn btn-outline-secondary btn-sm'>
//                 <Icon prefix="fe" name="arrow-left" /> {t('general.back_to')} {t('organization.classpasses.title')}
//             </Link>
//           </div>
//         </Page.Header>
//         <Grid.Row>
//           <Grid.Col md={9}>
//             <Query query={GET_CLASSPASS_GROUPS_QUERY} >
//              {({ loading, error, data: {organizationClasspassGroups: classpass_groups}, refetch, fetchMore }) => {
//                 // Loading
//                 if (loading) return (
//                   <ContentCard cardTitle={t('organization.classpass_groups.title')}>
//                     <Dimmer active={true}
//                             loader={true}>
//                     </Dimmer>
//                   </ContentCard>
//                 )
//                 // Error
//                 if (error) return (
//                   <ContentCard cardTitle={t('organization.classpass_groups.title')}>
//                     <p>{t('organization.classpass_groups.error_loading')}</p>
//                   </ContentCard>
//                 )
                
//                 // Empty list
//                 if (!classpass_groups.edges.length) { return (
//                   <ContentCard cardTitle={t('organization.classpass_groups.title')}>
//                     <p>{t('organization.classpass_groups.empty_list')}</p>
//                   </ContentCard>
//                 )} else {   
//                 // Life's good! :)
//                 return (
//                   <ContentCard cardTitle={t('organization.classpass_groups.title')}
//                                pageInfo={classpass_groups.pageInfo}
//                                onLoadMore={() => {
//                                 fetchMore({
//                                   variables: {
//                                     after: classpass_groups.pageInfo.endCursor
//                                   },
//                                   updateQuery: (previousResult, { fetchMoreResult }) => {
//                                     const newEdges = fetchMoreResult.organizationClasspassGroups.edges
//                                     const pageInfo = fetchMoreResult.organizationClasspassGroups.pageInfo

//                                     return newEdges.length
//                                       ? {
//                                           // Put the new classpass_groups at the end of the list and update `pageInfo`
//                                           // so we have the new `endCursor` and `hasNextPage` values
//                                           organizationClasspassGroups: {
//                                             __typename: previousResult.organizationClasspassGroups.__typename,
//                                             edges: [ ...previousResult.organizationClasspassGroups.edges, ...newEdges ],
//                                             pageInfo
//                                           }
//                                         }
//                                       : previousResult
//                                   }
//                                 })
//                               }} >
//                         <Table>
//                           <Table.Header>
//                             <Table.Row key={v4()}>
//                               <Table.ColHeader>{t('general.name')}</Table.ColHeader>
//                             </Table.Row>
//                           </Table.Header>
//                           <Table.Body>
//                               {classpass_groups.edges.map(({ node }) => (
//                                 <Table.Row key={v4()}>
//                                   <Table.Col key={v4()}>
//                                     {node.name}
//                                   </Table.Col>
//                                   <Table.Col className="text-right" key={v4()}>
//                                       <Button className='btn-sm' 
//                                               onClick={() => history.push("/organization/classpasses/groups/edit/" + node.id)}
//                                               color="secondary">
//                                         {t('general.edit')}
//                                       </Button>
//                                       <Button className='btn-sm' 
//                                               onClick={() => history.push("/organization/classpasses/groups/edit/passes/" + node.id)}
//                                               color="secondary">
//                                         {t('organization.classpasses.groups.edit_passes')}
//                                       </Button>
//                                   </Table.Col>
//                                   {/* <Mutation mutation={ARCHIVE_CLASSPASS_GROUP} key={v4()}>
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
//                                             {query: GET_CLASSPASS_GROUPS_QUERY, variables: {"archived": archived }}
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
//                                   </Mutation> */}
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
//                                   resource="organizationclasspassgroup">
//               <Button color="primary btn-block mb-6"
//                       onClick={() => history.push("/organization/classpasses/groups/add")}>
//                 <Icon prefix="fe" name="plus-circle" /> {t('organization.classpass_groups.add')}
//               </Button>
//             </HasPermissionWrapper>
//             <OrganizationMenu active_link=''/>
//           </Grid.Col>
//         </Grid.Row>
//       </Container>
//     </div>
//   </SiteWrapper>
// )

export default withTranslation()(withRouter(OrganizationClasspassesGroups))