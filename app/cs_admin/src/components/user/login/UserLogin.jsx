// @flow

import React, { useContext } from 'react'
import { useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

// import { GET_ACCOUNTS_QUERY, GET_ACCOUNT_QUERY } from './queries'
// import { ACCOUNT_SCHEMA } from './yupSchema'

import {
  Button,
  Icon,
} from "tabler-react"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationContext from '../../context/OrganizationContext'

import { TOKEN_AUTH, TOKEN_REFRESH } from "../../../queries/system/auth"
import { CSAuth } from "../../../tools/authentication"
import CSLS from "../../../tools/cs_local_storage"

import UserLoginForm from "./UserLoginForm"
import CSStandaloneFormPage from "../../ui/CSStandaloneFormPage"


function UserLogin({t, match, history}) {
  const organization = useContext(OrganizationContext)
  console.log(organization)

  let errorMessage
  const [ doTokenAuth ] = useMutation(TOKEN_AUTH)
  const [ doTokenRefresh ] = useMutation(TOKEN_REFRESH)

  return (
    <CSStandaloneFormPage urlLogo={organization.urlLogoLogin} >
      <div className="text-center text-muted mb-1">
        {organization ? organization.name : ""}
      </div>
      <Formik
        initialValues={{ 
          email: "",
          password: ""
        }}
        // validationSchema={ACCOUNT_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
            let vars = {
              username: values.email,
              password: values.password,
            }

            doTokenAuth({ variables: vars,
              refetchQueries: [
                // // Refetch list
                // {query: GET_ACCOUNTS_QUERY, variables: get_list_query_variables()},
                // // Refresh local cached results for this account
                // {query: GET_ACCOUNT_QUERY, variables: {"id": match.params.account_id}}
            ]})
            .then(({ data }) => {
                console.log('got data', data)
                // TODO: Add link to "feature switcher" here
                const next = localStorage.getItem(CSLS.AUTH_LOGIN_NEXT) || "/user/welcome"
                CSAuth.login(data.tokenAuth.token)
                doTokenRefresh({
                  variables: { token: data.tokenAuth.token }
                }).then(({ data }) => {
                  console.log('got refresh data', data)
                  CSAuth.updateTokenInfo(data.refreshToken)
                  // Login success!
                  setTimeout(() => history.push(next), 500)
                }).catch((error) => {
                  toast.error((t('general.toast_server_error')) + ': ' +  error, {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                  console.log('there was an error verifying the login', error)
                  setSubmitting(false)
                })
              }).catch((error) => {
                if ( error.message.includes('credentials') ) {
                  // Request user to input valid credentials
                  toast.info((t('user.login.invalid_credentials')), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                } else {
                  // Show general error message
                  toast.error((t('general.toast_server_error')) + ': ' +  error, {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                }
                console.log('there was an error sending the query', error)
                setSubmitting(false)
              })
        }}
        >
        {({ isSubmitting, errors }) => (
          <UserLoginForm
            isSubmitting={isSubmitting}
            errors={errors}
          />
        )}
      </Formik>    
      <div className="text-center">
        <h5>{t('user.register.create_account')}</h5>
        {t('user.register.create_account_msg')} <br />
        {t('user.register.create_account_msg_click_below')} <br />
      </div>
      <Button 
        block
        color="link"
        RootComponent="a"
        href={(window.location.hostname === "localhost" || window.location.hostname === "dev.costasiella.com") ? 
          "http://localhost:8000/d/accounts/signup/" :
          "/d/accounts/signup/"
        } 
      >
        {t('user.register.create_account')} <Icon name="chevron-right" />
      </Button>
    </CSStandaloneFormPage>


    // <Page>
    //   <div className="page-single">
    //     <Container>
    //       <Grid.Row>
    //         <div className="col col-login mx-auto">            
    //           <div className="text-center mb-5">
    //             <img src={organization.urlLogoLogin} className="h-9" alt="logo" />
    //           </div>
              
    //         </div>
    //       </Grid.Row>
    //     </Container>
    //   </div>
    // </Page>
  )
}




// class RelationsAccountProfile extends Component {
//   constructor(props) {
//     super(props)
//     console.log("Organization profile props:")
//     console.log(props)
//   }

//   render() {
//     const t = this.props.t
//     const match = this.props.match
//     const history = this.props.history
//     const account_id = match.params.account_id
//     const return_url = "/relations/accounts"

//     return (
//       <SiteWrapper>
//         <div className="my-3 my-md-5">
//           <Container>
//             <Query query={GET_ACCOUNT_QUERY} variables={{ id: account_id }} >
//               {({ loading, error, data, refetch }) => {
//                   // Loading
//                   if (loading) return <p>{t('general.loading_with_dots')}</p>
//                   // Error
//                   if (error) {
//                     console.log(error)
//                     return <p>{t('general.error_sad_smiley')}</p>
//                   }
                  
//                   const initialData = data.account;
//                   console.log('query data')
//                   console.log(data)

//                   // DatePicker doesn't like a string as an initial value
//                   // This makes it a happy DatePicker :)
//                   let dateOfBirth = null
//                   if (initialData.dateOfBirth) {
//                     dateOfBirth = new Date(initialData.dateOfBirth)
//                   }

//                   return (
//                     <div>
//                       <Page.Header title={initialData.firstName + " " + initialData.lastName}>
//                         <RelationsAccountsBack />
//                       </Page.Header>
//                       <Grid.Row>
//                         <Grid.Col md={9}>
//                         <Card>
//                           <Card.Header>
//                             <Card.Title>{t('relations.accounts.profile')}</Card.Title>
//                             {console.log(match.params.account_id)}
//                           </Card.Header>
//                         <Mutation mutation={UPDATE_ACCOUNT}> 
//                          {(updateAccount, { data }) => (
//                           <Formik
//                             initialValues={{ 
//                               customer: initialData.customer, 
//                               teacher: initialData.teacher, 
//                               employee: initialData.employee, 
//                               firstName: initialData.firstName, 
//                               lastName: initialData.lastName, 
//                               email: initialData.email,
//                               dateOfBirth: dateOfBirth,
//                               gender: initialData.gender,
//                               emergency: initialData.emergency,
//                               phone: initialData.phone,
//                               mobile: initialData.mobile,
//                               address: initialData.address,
//                               postcode: initialData.postcode,
//                               city: initialData.city,
//                               country: initialData.country,
//                             }}
//                             validationSchema={ACCOUNT_SCHEMA}
//                             onSubmit={(values, { setSubmitting }) => {
//                                 console.log('submit values:')
//                                 console.log(values)

//                                 let input_vars = {
//                                   id: match.params.account_id,
//                                   customer: values.customer,
//                                   teacher: values.teacher,
//                                   employee: values.employee,
//                                   firstName: values.firstName,
//                                   lastName: values.lastName,
//                                   email: values.email,
//                                   gender: values.gender,
//                                   emergency: values.emergency,
//                                   phone: values.phone,
//                                   mobile: values.mobile,
//                                   address: values.address,
//                                   postcode: values.postcode,
//                                   city: values.city,
//                                   country: values.country
//                                 }

//                                 if (values.dateOfBirth) {
//                                   input_vars['dateOfBirth'] = dateToLocalISO(values.dateOfBirth)
//                                 } 

//                                 updateAccount({ variables: {
//                                   input: input_vars
//                                 }, refetchQueries: [
//                                     // Refetch list
//                                     {query: GET_ACCOUNTS_QUERY, variables: get_list_query_variables()},
//                                     // Refresh local cached results for this account
//                                     {query: GET_ACCOUNT_QUERY, variables: {"id": match.params.account_id}}
//                                 ]})
//                                 .then(({ data }) => {
//                                     console.log('got data', data)
//                                     toast.success((t('relations.accounts.toast_edit_success')), {
//                                         position: toast.POSITION.BOTTOM_RIGHT
//                                       })
//                                     setSubmitting(false)
//                                   }).catch((error) => {
//                                     toast.error((t('general.toast_server_error')) + ': ' +  error, {
//                                         position: toast.POSITION.BOTTOM_RIGHT
//                                       })
//                                     console.log('there was an error sending the query', error)
//                                     setSubmitting(false)
//                                   })
//                             }}
//                             >
//                             {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
//                               <RelationsAccountProfileForm
//                                 isSubmitting={isSubmitting}
//                                 setFieldTouched={setFieldTouched}
//                                 setFieldValue={setFieldValue}
//                                 errors={errors}
//                                 values={values}
//                               />
//                             )}
//                           </Formik>
//                         )}
//                       </Mutation>
//                     </Card>
//                     </Grid.Col>                                    
//                     <Grid.Col md={3}>
//                       <ProfileCardSmall user={initialData}/>
//                       <ProfileMenu 
//                         active_link='profile'
//                         account_id={account_id}
//                       /> 
//                     </Grid.Col>
//                   </Grid.Row>
//                 </div>
//               )}}
//             </Query>
//           </Container>
//         </div>
//     </SiteWrapper>
//     )}
//   }


export default withTranslation()(withRouter(UserLogin))