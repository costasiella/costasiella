// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'

import {
  Avatar,
  Card,
  Header,
  Icon,
  Media,
  Text,
  SocialNetworksList,
} from "tabler-react"

const ProfileCardSmall = ({ t, value, user }) => (
  <Card>
    <Card.Body>
      <Media>
        {(user.imageURL) ? 
          <Avatar size="lg mr-5" imageURL="avatarImageURL" /> :
          <Avatar size="lg mr-5" icon="user" />
        }
        <Media.Body>
          <h4 className="m-0">{user.firstName + " " + user.lastName}</h4>
          <p className="text-muted mb-0">
            <Text.Small>
            <Icon name="mail" />  <a href={"mailto:" + user.email}>{user.email}</a> <br/>
            <Icon name="phone" /> user phone nr here...
            </Text.Small>
          </p>
          {/* <SocialNetworksList
            items={[
              <a href="http://www.twitter.com">
                <Icon prefix="fa" name="twitter" />
              </a>,
              <a href="http://www.facebook.com">
                <Icon prefix="fa" name="facebook" />
              </a>,
            ]}
          /> */}
        </Media.Body>
      </Media>
    </Card.Body>
  </Card>
)

export default withTranslation()(ProfileCardSmall)