// @flow

import React from 'react'

import {
    Icon
  } from "tabler-react";

const InputSearch = ({ placeholder, defaultValue="", onChange=f=>f }) => (
    <div className="input-icon">
        <span className="input-icon-addon">
            <Icon name="search" />
        </span>
        <input className="form-control" type="text" placeholder={placeholder} defaultValue={defaultValue} onChange={onChange} />
    </div>
)

export default InputSearch