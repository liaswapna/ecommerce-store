import { createContext, useContext, useEffect, useState } from "react"
import type { ReactNode } from "react"
import { getMe } from "../api"
import type { User } from "../api"

interface AuthContextType {
    token: string | null
    user: User | null
    login: (token: string) => void
    logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [token, setToken] = useState<string | null>(null)
    const [user, setUser] = useState<User | null>(null)

    useEffect(() => {
        if (!token) return
        getMe(token)
            .then(setUser)
            .catch(() => {
                setToken(null)
                setUser(null)
            })
    }, [token])

    function login(token: string) {
        setToken(token)
    }

    function logout() {
        setToken(null)
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ token, user, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error("useAuth must be used inside AuthProvider")
    return ctx
}
