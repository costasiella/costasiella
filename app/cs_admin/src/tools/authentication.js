import CSLS from "./cs_local_storage"


export const CSAuth = {
    login(token) {
        localStorage.setItem(CSLS.AUTH_TOKEN, token)
        localStorage.removeItem(CSLS.AUTH_LOGIN_NEXT)
    },
    logout() {
        localStorage.removeItem(CSLS.AUTH_TOKEN)
        localStorage.removeItem(CSLS.AUTH_LOGIN_NEXT)
    }
}