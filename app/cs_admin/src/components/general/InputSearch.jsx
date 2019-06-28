// @flow

import React, { Component } from 'react'
import { withTranslation } from 'react-i18next'

import {
    Icon
  } from "tabler-react"


class InputSearch extends Component {
  constructor(props) {
    super(props)
    console.log("Input search props:")
    console.log(props)
    this.input = React.createRef()
  }
  
  componentDidMount() {
    this.input.current.focus()
  }


  onKeyUp = () => {
      
  }

  render() {
    const t = this.props.t
    const placeholder = this.props.placeholder
    const defaultValue = this.props.devaultValue 
    const onChange = this.props.onChange
    const onClear = this.props.onClear
    
    var typingTimer
    var doneTypingInterval = 500



    return(
      <div className="input-icon input-search">
        <span className="input-icon-addon">
          <Icon name="search" />
        </span>
        <input 
          ref={this.input}
          className="form-control" 
          type="text" 
          placeholder={placeholder} 
          defaultValue={defaultValue} 
          onKeyUp={this.onKeyUp.bind(this)}
          // onChange={(event) => onChange(event)} 
        />
        <span className="input-icon-addon">
          <Icon 
            name="x" 
            onClick={(event) => onClear(event)}
          />
        </span>
      </div>
    )
  }
}

InputSearch.defaultProps = {
  defaultValue: "",
  onChange: f=>f,
  onClear: f=>f,
}
  
export default withTranslation()(InputSearch)