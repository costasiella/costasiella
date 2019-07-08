// @flow

import React, { Component } from 'react'
import { withTranslation } from 'react-i18next'

import {
    Button,
    Icon
  } from "tabler-react"

import CSLS from "../../tools/cs_local_storage"

class InputSearch extends Component {
  constructor(props) {
    super(props)
    console.log("Input search props:")
    console.log(props)
    this.input = React.createRef()
    let inputValue
    const initialValue = localStorage.getItem(this.props.initialValueKey)
    if (initialValue) {
      inputValue = initialValue 
    } else {
      inputValue = ""
    }

    this.state = {
      inputValue: inputValue,
      submitValue: "",
      doneTypingInterval: 500
    }
  }
  
  componentDidMount() {
    this.typingTimer = null
    this.input.current.focus()
  }

  componentWillUnmount() {
    clearTimeout(this.typingTimer)
  }


  onInputKeyUp() {
    // Clear timeout
    if (this.typingTimer) {
      clearTimeout(this.typingTimer)
    }
    
    this.typingTimer = setTimeout(() => {
      // console.log(this.input.current.value)  
      this.setState({submitValue: this.input.current.value})
      this.props.onChange(this.state.submitValue)
    }, this.state.doneTypingInterval)
  }


  onInputChange(event) {
    this.setState({inputValue: event.target.value})
  }


  render() {
    const t = this.props.t
    const placeholder = this.props.placeholder

    return(
        <div className="row row gutters-xs">
          <div className="col">
            <div className="input-icon">
              <span className="input-icon-addon">
                <Icon name="search" />
              </span>
              <input 
                ref={this.input}
                className="form-control" 
                type="text" 
                placeholder={placeholder} 
                value={this.state.inputValue}
                onKeyUp={this.onInputKeyUp.bind(this)}
                onChange={this.onInputChange.bind(this)}
              />
            </div>
          </div>
          <div className="col col-auto">
            <Button
              color="secondary"
              icon="x"
              disabled={!(this.state.inputValue)}
              onClick={() => {
                this.setState({inputValue: "", submitValue: ""}, () => {
                  // setState callback, this makes sure the onChange function is calles with new values
                  console.log(this.state)
                  this.props.onChange(this.state.submitValue) 
                })
              }}
            >
            </Button>
          </div>
        </div>
    )
  }
}

InputSearch.defaultProps = {
  onChange: f=>f,
  onClear: f=>f,
}
  
export default withTranslation()(InputSearch)