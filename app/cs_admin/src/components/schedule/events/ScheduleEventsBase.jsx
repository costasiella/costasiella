// @flow
import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Container,
  Grid
} from "tabler-react";
import HasPermissionWrapper from "../../HasPermissionWrapper"
import SiteWrapper from "../../SiteWrapper"
// import ShopAccountBack from "../ShopAccountBack"
import ScheduleMenu from "../ScheduleMenu"


function ScheduleEventsBase({ t, match, history, children, sidebarContent="" }) {
  return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("schedule.events.title")} >
              <div className="page-options d-flex">
                {/* TODO: Add back button ? */}
                Back here...
                {/* <ShopAccountBack /> */}
              </div>
            </Page.Header>
            <Grid.Row>
            <Grid.Col md={9}>
              { children }
            </Grid.Col>
            <Grid.Col md={3}>
              { sidebarContent }
              {/* <HasPermissionWrapper permission="add"
                                    resource="scheduleevent">
                <Button color="primary btn-block mb-1"
                        onClick={() => history.push("/schedule/events/add")}>
                  <Icon prefix="fe" name="plus-circle" /> {t('schedule.events.add')}
                </Button>
              </HasPermissionWrapper> */}
                  {/* <div>
                    <Button
                      className="pull-right"
                      color="link"
                      size="sm"
                      onClick={() => {
                        localStorage.setItem(CSLS.SCHEDULE_CLASSES_FILTER_CLASSTYPE, "")
                        localStorage.setItem(CSLS.SCHEDULE_CLASSES_FILTER_LEVEL, "")
                        localStorage.setItem(CSLS.SCHEDULE_CLASSES_FILTER_LOCATION, "")
                        refetch(get_list_query_variables())
                      }}
                    >
                      {t("general.clear")}
                    </Button>
                  </div> */}
                  {/* <h5 className="mt-2 pt-1">{t("general.filter")}</h5>
                  <ScheduleClassesFilter data={data} refetch={refetch} /> */}
              <h5>{t("general.menu")}</h5>
              <ScheduleMenu active_link='events'/>
            </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
      </SiteWrapper>
  )
}

export default withTranslation()(withRouter(ScheduleEventsBase))
