import CSLS from "./cs_local_storage"


export const CSAuth = {
    login(token) {
        localStorage.setItem(CSLS.AUTH_TOKEN, token)
    },
    logout() {
        localStorage.removeItem(CSLS.AUTH_TOKEN)
    }
}