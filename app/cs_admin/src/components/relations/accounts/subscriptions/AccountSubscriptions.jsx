// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
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
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import BooleanBadge from "../../../ui/BooleanBadge"
import RelationsAccountsBack from "../RelationsAccountsBack"
import confirm_delete from "../../../../tools/confirm_delete"

import ContentCard from "../../../general/ContentCard"
import ProfileMenu from "../ProfileMenu"
import ProfileCardSmall from "../../../ui/ProfileCardSmall"

import { GET_ACCOUNT_SUBSCRIPTIONS_QUERY } from "./queries"

const DELETE_ACCOUNT_SUBSCRIPTION = gql`
  mutation DeleteAccountSubscription($input: DeleteAccountSubscriptionInput!) {
    deleteAccountSubscription(input: $input) {
      ok
    }
  }
`


const AccountSubscriptions = ({ t, history, match, archived=false }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Query query={GET_ACCOUNT_SUBSCRIPTIONS_QUERY} variables={{ archived: archived, accountId: match.params.id }}> 
        {({ loading, error, data, refetch, fetchMore }) => {
          // Loading
          if (loading) return <p>{t('general.loading_with_dots')}</p>
          // Error
          if (error) {
            console.log(error)
            return <p>{t('general.error_sad_smiley')}</p>
          }

          const account = data.account
          const accountSubscriptions = data.accountSubscriptions

          return (
            <Container>
              <Page.Header title={account.firstName + " " + account.lastName} >
                <RelationsAccountsBack />
              </Page.Header>
              <Grid.Row>
                <Grid.Col md={9}>
                  <ContentCard 
                    cardTitle={t('relations.accounts.subscriptions')}
                    pageInfo={accountSubscriptions.pageInfo}
                    onLoadMore={() => {
                      fetchMore({
                        variables: {
                          after: accountSubscriptions.pageInfo.endCursor
                        },
                        updateQuery: (previousResult, { fetchMoreResult }) => {
                          const newEdges = fetchMoreResult.accountSubscriptions.edges
                          const pageInfo = fetchMoreResult.accountSubscriptions.pageInfo

                          return newEdges.length
                            ? {
                                // Put the new accountSubscriptions at the end of the list and update `pageInfo`
                                // so we have the new `endCursor` and `hasNextPage` values
                                accountSubscriptions: {
                                  __typename: previousResult.accountSubscriptions.__typename,
                                  edges: [ ...previousResult.accountSubscriptions.edges, ...newEdges ],
                                  pageInfo
                                }
                              }
                            : previousResult
                        }
                      })
                    }} 
                  >
                    <Table>
                      <Table.Header>
                        <Table.Row key={v4()}>
                          <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                          <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
                          <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
                          <Table.ColHeader>{t('general.payment_method')}</Table.ColHeader>
                          <Table.ColHeader></Table.ColHeader> 
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                          {accountSubscriptions.edges.map(({ node }) => (
                            <Table.Row key={v4()}>
                              <Table.Col key={v4()}>
                                {node.organizationSubscription.name}
                              </Table.Col>
                              <Table.Col key={v4()}>
                                {node.dateStart}
                              </Table.Col>
                              <Table.Col key={v4()}>
                                {node.dateEnd}
                              </Table.Col>
                              <Table.Col key={v4()}>
                                {(node.financePaymentMethod) ? node.financePaymentMethod.name : ""}
                              </Table.Col>
                              <Table.Col className="text-right" key={v4()}>
                                <Link to={"/relations/accounts/" + match.params.id + "/subscriptions/edit/" + node.id}>
                                  <Button className='btn-sm' 
                                          color="secondary">
                                    {t('general.edit')}
                                  </Button>
                                </Link>
                              </Table.Col>
                              <Mutation mutation={DELETE_ACCOUNT_SUBSCRIPTION} key={v4()}>
                                {(deleteAccountSubscription, { data }) => (
                                  <Table.Col className="text-right" key={v4()}>
                                    <button className="icon btn btn-link btn-sm" 
                                      title={t('general.delete')} 
                                      href=""
                                      onClick={() => {
                                        confirm_delete({
                                          t: t,
                                          msgConfirm: t("relations.accounts.subscriptions_delete_confirm_msg"),
                                          msgDescription: <p>{node.organizationSubscription.name} {node.dateStart}</p>,
                                          msgSuccess: t('relations.accounts.subscription_deleted'),
                                          deleteFunction: deleteAccountSubscription,
                                          functionVariables: { variables: {
                                            input: {
                                              id: node.id
                                            }
                                          }, refetchQueries: [
                                            {query: GET_ACCOUNT_SUBSCRIPTIONS_QUERY, variables: { archived: archived, accountId: match.params.id }} 
                                          ]}
                                        })
                                    }}>
                                      <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
                                    </button>
                                  </Table.Col>
                                )}
                              </Mutation>
                            </Table.Row>
                          ))}
                      </Table.Body>
                    </Table>
                  </ContentCard>
                </Grid.Col>
                <Grid.Col md={3}>
                  <ProfileCardSmall user={account}/>
                  <HasPermissionWrapper permission="add"
                                        resource="accountsubscription">
                    <Link to={"/relations/accounts/" + match.params.id + "/subscriptions/add"}>
                      <Button color="primary btn-block mb-6">
                              {/* //  onClick={() => history.push("/organization/subscriptions/add")}> */}
                        <Icon prefix="fe" name="plus-circle" /> {t('relations.accounts.subscription_add')}
                      </Button>
                    </Link>
                  </HasPermissionWrapper>
                  <ProfileMenu 
                    active_link='subscriptions' 
                    account_id={match.params.id}
                  />
                </Grid.Col>
              </Grid.Row>
            </Container>
          )
        }}
      </Query>
    </div>
  </SiteWrapper>
)
      
        


//         <Grid.Row>
//           <Grid.Col md={9}>
//             <Query query={GET_SUBSCRIPTIONS_QUERY} variables={{ archived }}>
//              {({ loading, error, data: {organizationSubscriptions: subscriptions}, refetch, fetchMore }) => {
//                 // Loading
//                 if (loading) return (
//                   <ContentCard cardTitle={t('organization.subscriptions.title')}>
//                     <Dimmer active={true}
//                             loadder={true}>
//                     </Dimmer>
//                   </ContentCard>
//                 )
//                 // Error
//                 if (error) return (
//                   <ContentCard cardTitle={t('organization.subscriptions.title')}>
//                     <p>{t('organization.subscriptions.error_loading')}</p>
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
//                 if (!subscriptions.edges.length) { return (
//                   <ContentCard cardTitle={t('organization.subscriptions.title')}
//                                headerContent={headerOptions}>
//                     <p>
//                     {(!archived) ? t('organization.subscriptions.empty_list') : t("organization.subscriptions.empty_archive")}
//                     </p>
                   
//                   </ContentCard>
//                 )} else {   
//                 // Life's good! :)
//                 return (
//                   <ContentCard cardTitle={t('organization.subscriptions.title')}
//                                headerContent={headerOptions}
//                                pageInfo={subscriptions.pageInfo}
//                                onLoadMore={() => {
//                                 fetchMore({
//                                   variables: {
//                                     after: subscriptions.pageInfo.endCursor
//                                   },
//                                   updateQuery: (previousResult, { fetchMoreResult }) => {
//                                     const newEdges = fetchMoreResult.organizationSubscriptions.edges
//                                     const pageInfo = fetchMoreResult.organizationSubscriptions.pageInfo

//                                     return newEdges.length
//                                       ? {
//                                           // Put the new subscriptions at the end of the list and update `pageInfo`
//                                           // so we have the new `endCursor` and `hasNextPage` values
//                                           organizationSubscriptions: {
//                                             __typename: previousResult.organizationSubscriptions.__typename,
//                                             edges: [ ...previousResult.organizationSubscriptions.edges, ...newEdges ],
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
//                               <Table.ColHeader>{t('general.public')}</Table.ColHeader>
//                               <Table.ColHeader>{t('general.shop')}</Table.ColHeader>
//                               <Table.ColHeader>{t('general.classes')}</Table.ColHeader>
//                               <Table.ColHeader><span className="pull-right">{t('general.price')}</span></Table.ColHeader>
//                             </Table.Row>
//                           </Table.Header>
//                           <Table.Body>
//                               {subscriptions.edges.map(({ node }) => (
//                                 <Table.Row key={v4()}>
//                                   <Table.Col key={v4()}>
//                                     {node.name}
//                                   </Table.Col>
//                                   <Table.Col key={v4()}>
//                                     <BooleanBadge value={node.displayPublic} />
//                                   </Table.Col>
//                                   <Table.Col key={v4()}>
//                                     <BooleanBadge value={node.displayShop} />
//                                   </Table.Col>
//                                   <Table.Col key={v4()}>
//                                     {
//                                       (node.unlimited) ? t("general.unlimited"):
//                                       <div>
//                                         {node.classes} <br />
//                                         <span className="text-muted"> {t("general.a")} {node.subscriptionUnitDisplay}</span>
//                                       </div>
//                                     }
//                                   </Table.Col>
//                                   <Table.Col className="text-right" key={v4()}>
//                                     {node.priceTodayDisplay} <br />
//                                     <Link to={"/organization/subscriptions/prices/" + node.id}
//                                           className='btn btn-link btn-sm'>
//                                         {/* <Icon prefix="fe" name="dollar-sign" />  */}
//                                         {t('general.edit_price')}
//                                     </Link>
//                                   </Table.Col>
//                                   <Table.Col className="text-right" key={v4()}>
//                                     {(node.archived) ? 
//                                       <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
//                                       <Button className='btn-sm' 
//                                               onClick={() => history.push("/organization/subscriptions/edit/" + node.id)}
//                                               color="secondary">
//                                         {t('general.edit')}
//                                       </Button>
//                                     }
//                                   </Table.Col>
//                                   <Mutation mutation={ARCHIVE_SUBSCRIPTION} key={v4()}>
//                                     {(archiveSubscription, { data }) => (
//                                       <Table.Col className="text-right" key={v4()}>
//                                         <button className="icon btn btn-link btn-sm" 
//                                            title={t('general.archive')} 
//                                            href=""
//                                            onClick={() => {
//                                              console.log("clicked archived")
//                                              let id = node.id
//                                              archiveSubscription({ variables: {
//                                                input: {
//                                                 id,
//                                                 archived: !archived
//                                                }
//                                         }, refetchQueries: [
//                                             {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": archived }}
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
//                                   resource="organizationsubscription">
//               <Button color="primary btn-block mb-6"
//                       onClick={() => history.push("/organization/subscriptions/add")}>
//                 <Icon prefix="fe" name="plus-circle" /> {t('organization.subscriptions.add')}
//               </Button>
//             </HasPermissionWrapper>
//             <OrganizationMenu active_link='subscriptions'/>
//           </Grid.Col>
//         </Grid.Row>
//     </div>
//   </SiteWrapper>
// );



// const AccountSubscriptions = ({ t, history, archived=false }) => (
//   <SiteWrapper>
//     <div className="my-3 my-md-5">
//       <Container>
//         <Page.Header title={t("organization.title")}>
//           <div className="page-options d-flex">
//             <Link to="/organization/subscriptions/groups" 
//                   className='btn btn-outline-secondary btn-sm'>
//                 <Icon prefix="fe" name="folder" /> {t('general.groups')}
//             </Link>
//           </div>
//         </Page.Header>
//         <Grid.Row>
//           <Grid.Col md={9}>
//             <Query query={GET_SUBSCRIPTIONS_QUERY} variables={{ archived }}>
//              {({ loading, error, data: {organizationSubscriptions: subscriptions}, refetch, fetchMore }) => {
//                 // Loading
//                 if (loading) return (
//                   <ContentCard cardTitle={t('organization.subscriptions.title')}>
//                     <Dimmer active={true}
//                             loadder={true}>
//                     </Dimmer>
//                   </ContentCard>
//                 )
//                 // Error
//                 if (error) return (
//                   <ContentCard cardTitle={t('organization.subscriptions.title')}>
//                     <p>{t('organization.subscriptions.error_loading')}</p>
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
//                 if (!subscriptions.edges.length) { return (
//                   <ContentCard cardTitle={t('organization.subscriptions.title')}
//                                headerContent={headerOptions}>
//                     <p>
//                     {(!archived) ? t('organization.subscriptions.empty_list') : t("organization.subscriptions.empty_archive")}
//                     </p>
                   
//                   </ContentCard>
//                 )} else {   
//                 // Life's good! :)
//                 return (
//                   <ContentCard cardTitle={t('organization.subscriptions.title')}
//                                headerContent={headerOptions}
//                                pageInfo={subscriptions.pageInfo}
//                                onLoadMore={() => {
//                                 fetchMore({
//                                   variables: {
//                                     after: subscriptions.pageInfo.endCursor
//                                   },
//                                   updateQuery: (previousResult, { fetchMoreResult }) => {
//                                     const newEdges = fetchMoreResult.organizationSubscriptions.edges
//                                     const pageInfo = fetchMoreResult.organizationSubscriptions.pageInfo

//                                     return newEdges.length
//                                       ? {
//                                           // Put the new subscriptions at the end of the list and update `pageInfo`
//                                           // so we have the new `endCursor` and `hasNextPage` values
//                                           organizationSubscriptions: {
//                                             __typename: previousResult.organizationSubscriptions.__typename,
//                                             edges: [ ...previousResult.organizationSubscriptions.edges, ...newEdges ],
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
//                               <Table.ColHeader>{t('general.public')}</Table.ColHeader>
//                               <Table.ColHeader>{t('general.shop')}</Table.ColHeader>
//                               <Table.ColHeader>{t('general.classes')}</Table.ColHeader>
//                               <Table.ColHeader><span className="pull-right">{t('general.price')}</span></Table.ColHeader>
//                             </Table.Row>
//                           </Table.Header>
//                           <Table.Body>
//                               {subscriptions.edges.map(({ node }) => (
//                                 <Table.Row key={v4()}>
//                                   <Table.Col key={v4()}>
//                                     {node.name}
//                                   </Table.Col>
//                                   <Table.Col key={v4()}>
//                                     <BooleanBadge value={node.displayPublic} />
//                                   </Table.Col>
//                                   <Table.Col key={v4()}>
//                                     <BooleanBadge value={node.displayShop} />
//                                   </Table.Col>
//                                   <Table.Col key={v4()}>
//                                     {
//                                       (node.unlimited) ? t("general.unlimited"):
//                                       <div>
//                                         {node.classes} <br />
//                                         <span className="text-muted"> {t("general.a")} {node.subscriptionUnitDisplay}</span>
//                                       </div>
//                                     }
//                                   </Table.Col>
//                                   <Table.Col className="text-right" key={v4()}>
//                                     {node.priceTodayDisplay} <br />
//                                     <Link to={"/organization/subscriptions/prices/" + node.id}
//                                           className='btn btn-link btn-sm'>
//                                         {/* <Icon prefix="fe" name="dollar-sign" />  */}
//                                         {t('general.edit_price')}
//                                     </Link>
//                                   </Table.Col>
//                                   <Table.Col className="text-right" key={v4()}>
//                                     {(node.archived) ? 
//                                       <span className='text-muted'>{t('general.unarchive_to_edit')}</span> :
//                                       <Button className='btn-sm' 
//                                               onClick={() => history.push("/organization/subscriptions/edit/" + node.id)}
//                                               color="secondary">
//                                         {t('general.edit')}
//                                       </Button>
//                                     }
//                                   </Table.Col>
//                                   <Mutation mutation={ARCHIVE_SUBSCRIPTION} key={v4()}>
//                                     {(archiveSubscription, { data }) => (
//                                       <Table.Col className="text-right" key={v4()}>
//                                         <button className="icon btn btn-link btn-sm" 
//                                            title={t('general.archive')} 
//                                            href=""
//                                            onClick={() => {
//                                              console.log("clicked archived")
//                                              let id = node.id
//                                              archiveSubscription({ variables: {
//                                                input: {
//                                                 id,
//                                                 archived: !archived
//                                                }
//                                         }, refetchQueries: [
//                                             {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": archived }}
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
//                                   resource="organizationsubscription">
//               <Button color="primary btn-block mb-6"
//                       onClick={() => history.push("/organization/subscriptions/add")}>
//                 <Icon prefix="fe" name="plus-circle" /> {t('organization.subscriptions.add')}
//               </Button>
//             </HasPermissionWrapper>
//             <OrganizationMenu active_link='subscriptions'/>
//           </Grid.Col>
//         </Grid.Row>
//       </Container>
//     </div>
//   </SiteWrapper>
// );

export default withTranslation()(withRouter(AccountSubscriptions))