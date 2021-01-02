import React from 'react'

const OrganizationContext = React.createContext({})

export const OrganizationProvider = OrganizationContext.Provider
export const OrganizationConsumer = OrganizationContext.Consumer

export default OrganizationContext