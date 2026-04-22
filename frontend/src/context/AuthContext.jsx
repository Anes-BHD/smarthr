import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authApi } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(() => {
    try { return JSON.parse(localStorage.getItem('shr_user')) } catch { return null }
  })
  const [token,   setToken]   = useState(() => localStorage.getItem('shr_token'))
  const [loading, setLoading] = useState(true)

  // Validate token on mount
  useEffect(() => {
    if (!token) { setLoading(false); return }
    authApi.me()
      .then(r => setUser(r.data))
      .catch(() => { logout() })
      .finally(() => setLoading(false))
  }, []) // eslint-disable-line

  const login = useCallback(async (email, password) => {
    const res = await authApi.login({ email, password })
    const { token: tok, user: u } = res.data
    localStorage.setItem('shr_token', tok)
    localStorage.setItem('shr_user', JSON.stringify(u))
    setToken(tok)
    setUser(u)
    return u
  }, [])

  const logout = useCallback(async () => {
    try { await authApi.logout() } catch {}
    localStorage.removeItem('shr_token')
    localStorage.removeItem('shr_user')
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
