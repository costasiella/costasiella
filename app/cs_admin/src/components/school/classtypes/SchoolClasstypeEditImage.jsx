// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'
import { toast } from 'react-toastify'

import { GET_CLASSTYPES_QUERY, GET_CLASSTYPE_QUERY } from './queries'
import { CLASSTYPE_SCHEMA } from './yupSchema'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import SchoolMenu from "../SchoolMenu"


const UPDATE_CLASSTYPE = gql`
  mutation UploadSchoolCLasstypeImage($input: UpdateSchoolClasstypeInput!) {
    updateSchoolClasstype(input: $input) {
      schoolClasstype {
        id
        archived
        name
        description
        displayPublic
        urlWebsite
      }
    }
  }
`


class SchoolClasstypeEditImage extends Component {
  constructor(props) {
    super(props)
    console.log("School classtype image edit props:")
    console.log(props)
    this.fileInput = React.createRef()
  }

  onSubmit(e) {
    e.preventDefault()
    console.log(e.target.name + 'clicked')
    console.log(e.value)
    console.log(this.fileInput.current.files[0])
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id
    const return_url = "/school/classtypes"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title="School" />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('edit_ct_image')}</Card.Title>
                  {console.log(match.params.id)}
                </Card.Header>
                <Query query={GET_CLASSTYPE_QUERY} variables={{ id }} >
                {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('error_sad_smiley')}</p>
                    }
                    
                    const initialData = data.schoolClasstype
                    console.log('query data')
                    console.log(data)

                    return (
                      <Form onSubmit={(event) => this.onSubmit(event)}>
                        {/* <Form.FileInput ref={this.fileInput} name="fileInput"  /> */}
                        <input type="file"
                               ref={this.fileInput}
                        />
                        <Button type='submit' value='Submit'>Submit</Button>
                      </Form>
                      )}}
                </Query>
              </Card>
              </Grid.Col>
              <Grid.Col md={3}>
                <HasPermissionWrapper permission="add"
                                      resource="schoollocation">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('back')}
                  </Button>
                </HasPermissionWrapper>
                <SchoolMenu active_link='schoollocation'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(SchoolClasstypeEditImage))