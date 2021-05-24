import React, { Component } from 'react'
import { withTranslation } from 'react-i18next'

import {
    Button,
    Card,
  } from "tabler-react"


class ContentCard extends Component {
    componentDidMount() {
      window.addEventListener("scroll", this.handleOnScroll);
    }
  
    componentWillUnmount() {
      window.removeEventListener("scroll", this.handleOnScroll);
    }

    handleOnScroll = () => {
      // http://stackoverflow.com/questions/9439725/javascript-how-to-detect-if-browser-window-is-scrolled-to-bottom
      var scrollTop =
        (document.documentElement && document.documentElement.scrollTop) ||
        document.body.scrollTop;
      var scrollHeight =
        (document.documentElement && document.documentElement.scrollHeight) ||
        document.body.scrollHeight;
      var clientHeight =
        document.documentElement.clientHeight || window.innerHeight;
      var scrolledToBottom = Math.ceil(scrollTop + clientHeight) >= scrollHeight;
      if (scrolledToBottom) {
        const pageInfo = this.props.pageInfo
        if (pageInfo) {
          if (pageInfo.hasNextPage) {
            this.props.onLoadMore()
          }
        }
      }
    }

    render() {
      const t = this.props.t
      const cardTitle = this.props.cardTitle
      const headerContent = this.props.headerContent
      const onLoadMore = this.props.onLoadMore 
      const pageInfo = this.props.pageInfo
      const children = this.props.children
      const cardTabs = this.props.cardTabs
      const hasCardBody = this.props.hasCardBody 


      return(
        <Card>
          <Card.Header>
            <Card.Title>{cardTitle}</Card.Title>
            {headerContent}
          </Card.Header>
          {cardTabs}
          {(hasCardBody) ? 
            <Card.Body>{children}</Card.Body> :
            children
          }
          <Card.Footer>
            {(!pageInfo) ? '':
              (pageInfo.hasNextPage) ? 
                <Button 
                  link
                  onClick={onLoadMore} 
                  >
                  {t('general.load_more')}
                </Button>
               : t('general.loaded_all')
            }
          </Card.Footer>
        </Card>
      )
    }
}

ContentCard.defaultProps = {
  onLoadMore: f=>f,
  hasCardBody: true
}
  
export default withTranslation()(ContentCard)
