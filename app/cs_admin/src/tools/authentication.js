import CSLS from "./cs_local_storage"


export const CSAuth = {
    login(token) {
        // localStorage.setItem(CSLS.AUTH_TOKEN, token)
        localStorage.removeItem(CSLS.AUTH_LOGIN_NEXT)
    },
    updateTokenInfo(payload) {
        localStorage.setItem(CSLS.AUTH_TOKEN_EXP, payload.exp)
        localStorage.setItem(CSLS.AUTH_TOKEN_ORIGIAT, payload.origIat)
    },
    logout(expired=false) {
        if (!expired) {
            // Manual logout, remove everything
            localStorage.removeItem(CSLS.AUTH_TOKEN_EXP)
            localStorage.removeItem(CSLS.AUTH_TOKEN_ORIGIAT)
            localStorage.removeItem(CSLS.AUTH_LOGIN_NEXT)
        } 
        // //  Always remove token
        // localStorage.removeItem(CSLS.AUTH_TOKEN)
        
    }
}