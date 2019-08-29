import CSLS from "./cs_local_storage"


export const CSAuth = {
    token: localStorage.getItem(CSLS.AUTH_TOKEN),
    auth_success(token) {
        localStorage.setItem(CSLS.AUTH_TOKEN, token)
    },
    logout() {
        localStorage.removeItem(CSLS.AUTH_TOKEN)
    }
}