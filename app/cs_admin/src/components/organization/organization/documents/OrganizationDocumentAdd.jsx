// @flow

import React from 'react'
import { useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'

import { ADD_DOCUMENT, GET_DOCUMENTS_QUERY } from "./queries"
import { DOCUMENT_SCHEMA } from './yupSchema'
import { dateToLocalISO } from "../../../../tools/date_tools"
import OrganizationDocumentForm from './OrganizationDocumentForm'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationMenu from '../../OrganizationMenu'
import OrganizationDocumentsBase from "./OrganizationDocumentsBase"


const return_url = "/organization/levels"

function OrganizationDocumentAdd({ t, match, history }) {
  const organizationId = match.params.organization_id
  const documentType = match.params.document_type
  
  const returnUrl = `/organization/documents/${organizationId}/${documentType}`
  const back = <Link to={returnUrl}>
    <Button 
      icon="arrow-left"
      className="mr-2"
      outline
      color="secondary"
    >
      {t('general.back_to')} {t('organization.documents.list.title')}
    </Button>
  </Link>
  const sidebarButton = <HasPermissionWrapper 
    permission="add"
    resource="organizationdocument">
      <Link to={returnUrl} >
        <Button color="primary btn-block mb-6" >
          <Icon prefix="fe" name="plus-circle" /> {t('organization.documents.add')}
        </Button>
      </Link>
  </HasPermissionWrapper>

  const [addDocument, { data }] = useMutation(ADD_DOCUMENT)

  return (
    <OrganizationDocumentsBase headerLinks={back} sidebarButton={sidebarButton}>
      <Card>
        <Card.Header>
          <Card.Title>
            {t('organizations.documents.add')}
          </Card.Title>
        </Card.Header>
        <Formik
          initialValues={{ 
            version: '',
            dateStart: '', 
            dateEnd: '',
            document: ''
          }}
          // validationSchema={DOCUMENT_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
            let dateEnd
            if (values.dateEnd) {
              dateEnd = dateToLocalISO(values.dateEnd)
            } else {
              dateEnd = values.dateEnd
            }

            addDocument({ variables: {
              input: {
                documentType: documentType,
                name: values.name, 
                version: values.version,
                dateStart: dateToLocalISO(values.dateStart),
                dateEnd: dateEnd,
                document: values.document,
              }
            }, refetchQueries: [
                {query: GET_DOCUMENTS_QUERY, variables: {documentType: documentType}}
            ]})
            .then(({ data }) => {
                console.log('got data', data);
                toast.success((t('organization.documents.toast_add_success')), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
              }).catch((error) => {
                toast.error((t('general.toast_server_error')) + ': ' +  error, {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                console.log('there was an error sending the query', error)
                setSubmitting(false)
              })
          }}
          >
          {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
              <OrganizationDocumentForm 
                isSubmitting={isSubmitting}
                values={values}
                errors={errors}
                setFieldTouched={setFieldTouched}
                setFieldValue={setFieldValue}
                return_url={return_url}
              />
          )}
        </Formik>
      </Card>
    </OrganizationDocumentsBase>
  )
}

export default withTranslation()(OrganizationDocumentAdd)


// const OrganizationLevelAdd = ({ t, history }) => (
//   <SiteWrapper>
//     <div className="my-3 my-md-5">
//       <Container>
//         <Page.Header title={t('organization.title')} />
//         <Grid.Row>
//           <Grid.Col md={9}>
//           <Card>
//             <Card.Header>
//               <Card.Title>{t('organization.levels.title_add')}</Card.Title>
//             </Card.Header>
//             <Mutation mutation={ADD_LEVEL} onCompleted={() => history.push(return_url)}> 
//                 {(addLocation, { data }) => (
//                     <Formik
//                         initialValues={{ name: '', code: '' }}
//                         validationSchema={LEVEL_SCHEMA}
//                         onSubmit={(values, { setSubmitting }) => {
//                             addLocation({ variables: {
//                               input: {
//                                 name: values.name, 
//                               }
//                             }, refetchQueries: [
//                                 {query: GET_LEVELS_QUERY, variables: {"archived": false }}
//                             ]})
//                             .then(({ data }) => {
//                                 console.log('got data', data);
//                                 toast.success((t('organization.levels.toast_add_success')), {
//                                     position: toast.POSITION.BOTTOM_RIGHT
//                                   })
//                               }).catch((error) => {
//                                 toast.error((t('general.toast_server_error')) + ': ' +  error, {
//                                     position: toast.POSITION.BOTTOM_RIGHT
//                                   })
//                                 console.log('there was an error sending the query', error)
//                                 setSubmitting(false)
//                               })
//                         }}
//                         >
//                         {({ isSubmitting, errors }) => (
//                             <OrganizationLevelForm 
//                               isSubmitting={isSubmitting}
//                               errors={errors}
//                               return_url={return_url}
//                             />
//                         )}
//                     </Formik>
//                 )}
//                 </Mutation>
//           </Card>
//           </Grid.Col>
//           <Grid.Col md={3}>
//             <HasPermissionWrapper permission="add"
//                                   resource="organizationlevel">
//               <Button color="primary btn-block mb-6"
//                       onClick={() => history.push(return_url)}>
//                 <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
//               </Button>
//             </HasPermissionWrapper>
//             <OrganizationMenu active_link='levels'/>
//           </Grid.Col>
//         </Grid.Row>
//       </Container>
//     </div>
//   </SiteWrapper>
// )

// export default withTranslation()(withRouter(OrganizationLevelAdd))