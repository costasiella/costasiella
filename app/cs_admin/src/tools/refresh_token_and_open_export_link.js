export function refreshTokenAndOpenExportLinkInNewTab(doTokenRefresh, history, exportUrl) {
    doTokenRefresh()
      .then(() => {
        window.open(exportUrl, "_blank")
        // history.push(export_url)
      }).catch((error) => {
        console.log(error)
        history.push("/#/user/login")
      })
  }
