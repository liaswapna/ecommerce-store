import { Navigate } from "react-router-dom"
import type { ReactNode } from "react"
import { useAuth } from "../context/AuthContext"

export default function AdminRoute({ children }: { children: ReactNode }) {
    const { token, user } = useAuth()

    if (!token) return <Navigate to="/login" replace />
    if (!user) return <p className="p-8 text-gray-500">Loading...</p>
    if (!user.is_admin) return <Navigate to="/" replace />
    return <>{children}</>
}
