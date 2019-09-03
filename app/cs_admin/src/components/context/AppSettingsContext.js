import React from 'react'

const AppSettingsContext = React.createContext({})

export const AppSettingsProvider = AppSettingsContext.Provider
export const AppSettingsConsumer = AppSettingsContext.Consumer

export default AppSettingsContext