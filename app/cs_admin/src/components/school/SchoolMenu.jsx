import React from 'react'
import { Query } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"

// @flow

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"

let schoollocation_active

const SchoolMenu = ({active_link}) => (
    <List.Group transparent={true}>
        {
            (active_link == 'schoollocation') ? schoollocation_active = true: schoollocation_active = false
        }

        <HasPermissionWrapper 
            permission="view"
            resource="schoollocation">
            <List.GroupItem
                key={v4()}
                className="d-flex align-items-center"
                to="#/school/locations"
                icon="home"
                active={schoollocation_active}
                >
            Locations
            </List.GroupItem>
        </HasPermissionWrapper>
    </List.Group>
);

export default SchoolMenu