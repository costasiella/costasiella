import CSLS from "../../../../tools/cs_local_storage"

export function get_list_query_variables(accountId) {
  let queryVars = {
      account: accountId
  }

  let noteType = localStorage.getItem(CSLS.RELATIONS_ACCOUNT_NOTES_NOTE_TYPE)

  queryVars.noteType = noteType  

  console.log(queryVars)

  return queryVars
}

