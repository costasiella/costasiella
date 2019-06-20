// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'

import {
  Avatar,
  Card,
  Icon,
  List,
  Media,
  SocialNetworksList,
  Tooltip,
} from "tabler-react"

const ProfileCardSmall = ({ t, value, user, avatarSize='md' }) => (
  <Card>
    <Card.Body>
      <Media>
        {(user.imageURL) ? 
          <Avatar size={avatarSize + " mr-5"} imageURL="avatarImageURL" /> :
          <Avatar size={avatarSize + " mr-5"} icon="user" />
        }
        <Media.Body>
          <h4 className="mb-2">{user.firstName + " " + user.lastName}</h4>
          <div className="text-muted mb-0">
            <SocialNetworksList className="mb-0 mt-2">

              {
                (user.phone) ? 
                  <List.Item inline>
                    <Tooltip content={user.phone} placement="top">
                      <span>
                        <Icon prefix="fe" name="phone" />
                      </span>
                    </Tooltip>
                  </List.Item>
                // No phone number found
                : ""
              }
              {
                (user.mobile) ?
                  <List.Item inline>
                    <Tooltip content={user.mobile} placement="top">
                      <span>
                        <Icon prefix="fe" name="smartphone" />
                      </span>
                    </Tooltip>
                  </List.Item> 
                  // No mobile number found
                  : ""
              }

              <List.Item inline>
                <Tooltip content={user.email} placement="top">
                  <a href={"mailto:" + user.email}>
                    <Icon prefix="fe" name="mail" />
                  </a>
                </Tooltip>
              </List.Item>

            </SocialNetworksList>
            {/* items={[
              <a href={"mailto:" + user.email}
                 title={user.email}>
                <Icon prefix="fe" name="mail" />
              </a>,
              <span title="Phone number here">
                <Icon prefix="fe" name="phone" />
              </span>,
              <span title="Phone number here">
                <Icon prefix="fe" name="mobile" />
              </span>,
              
            ]}
          /> */}
            {/* <Text.Small>
              <Icon name="mail" />  <a href={"mailto:" + user.email}>{user.email}</a> <br/>
              <Icon name="phone" /> user phone nr here... <br />
              <Icon name="smartphone" /> user mobile nr here...
            </Text.Small> */}
          </div>
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