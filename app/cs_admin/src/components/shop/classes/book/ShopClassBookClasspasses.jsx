// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import moment from 'moment'

import {
  Grid,
  Card,
} from "tabler-react";

import ShopClassBookClasspassBtn from "./ShopClassBookClasspassBtn"


function ShopClassBookClasspasses({ t, match, history, classpasses }) {
  console.log("CLASSPASSES")
  console.log(classpasses)

  return (
    classpasses.map((classpass) =>(
      <Grid.Col md={3}>
        <Card 
          statusColor="blue"
          title={t("general.classpass")} >
        <Card.Body>
          <b>{classpass.accountClasspass.organizationClasspass.name}</b><br />
          <span className="text-muted">
            {t('general.classes_remaining')}: {classpass.accountClasspass.classesRemainingDisplay} <br />
            {t('general.valid_until')}: {moment(classpass.accountClasspass.dateEnd).format('LL')} <br />
          </span>
        </Card.Body>
        <Card.Footer>
          {(!classpass.allowed) ? t('schedule.classes.class.book.classpass_not_allowed') :
            <ShopClassBookClasspassBtn classpass={classpass} />
          }
        </Card.Footer>
        </Card>
      </Grid.Col>
    ))
  )
}


export default withTranslation()(withRouter(ShopClassBookClasspasses))

