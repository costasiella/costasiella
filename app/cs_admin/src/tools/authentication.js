import CSLS from "./cs_local_storage"


export const CSAuth = {
    login(token) {
        // localStorage.setItem(CSLS.AUTH_TOKEN, token)
        localStorage.removeItem(CSLS.AUTH_LOGIN_NEXT)
    },
    updateTokenInfo(refreshTokenData) {
        console.log("Token payload:")
        console.log(refreshTokenData)
        localStorage.setItem(CSLS.AUTH_TOKEN_EXP, refreshTokenData.payload.exp)
        localStorage.setItem(CSLS.AUTH_TOKEN_ORIGIAT, refreshTokenData.payload.origIat)
        localStorage.setItem(CSLS.AUTH_TOKEN_REFRESH_EXP, refreshTokenData.refreshExpiresIn)
    },
    logout(expired=false) {
        if (!expired) {
            // Manual logout, remove everything
            localStorage.removeItem(CSLS.AUTH_TOKEN_EXP)
            localStorage.removeItem(CSLS.AUTH_TOKEN_ORIGIAT)
            localStorage.removeItem(CSLS.AUTH_LOGIN_NEXT)
            localStorage.removeItem(CSLS.AUTH_TOKEN_REFRESH_EXP)
        } 
        // //  Always remove token
        // localStorage.removeItem(CSLS.AUTH_TOKEN)
        
    }
}
