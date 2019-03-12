import React from 'react'
// import { Query } from "react-apollo"
// import gql from "graphql-tag"
import { v4 } from "uuid"

// @flow

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"

let schoollocations_active
let schoolclasstypes_active

const SchoolMenu = ({active_link}) => (
    <List.Group transparent={true}>
        {
            (active_link == 'schoollocations') ? schoollocations_active = true: schoollocations_active = false
            (active_link == 'schoolclasstypes') ? schoolclasstypes_active = true: schoolclasstypes_active = false
        }

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/school/locations"
            icon="home"
            active={schoollocations_active}
            >
        Locations
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/school/classtypes"
            icon="book-open"
            active={schoolclasstypes_active}
            >
        Class types
        </List.GroupItem>
        {/* <HasPermissionWrapper 
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
        </HasPermissionWrapper> */}
    </List.Group>
);

export default SchoolMenu