import React, { Component } from 'react'
import { Query } from "react-apollo"

import GET_USER from '../queries/system/get_user'

class HasPermissionWrapper extends Component {
  constructor(props) {
    super(props)
    console.log("HasPermissionWrapper props:")
    console.log(props)
  }


  all_permissions(user) {
    console.log('all_permissions here')
    const permissions = {}
    const groups = user.groups
    for (let i in groups) {
      console.log(i)
      for (let p in groups[i].permissions) {
        let codename = groups[i].permissions[p].codename
        // codename has format <permission>_<resource>
        let codename_split = codename.split('_')
        
        if (!(codename_split[1] in permissions)) {
          permissions[codename_split[1]] = new Set()
        }
        permissions[codename_split[1]].add(codename_split[0])
      }
    }

    return permissions
  }

  check_permission(permissions, permission, resource) {
    let has_permission = false

    if (resource in permissions) {
      if (permissions[resource].has(permission)) {
        has_permission = true
      }
    }
    
    return has_permission
  }
  

  render() {
    
    

    return (
      <Query query={GET_USER} >

        {({ loading, error, data }) => {
          if (loading) return <p>Loading...</p>
          if (error) return <p>Error loading user... :(</p>
          
          console.log(data)
          const permissions = this.all_permissions(data.user)
          console.log('permissions:')
          console.log(permissions)

          if (this.check_permission(permissions, this.props.permission, this.props.resource)) {
            return this.props.children
          } else {
            return ''
          }
        }}

      </Query>
    )}
  }
  
  export default HasPermissionWrapper