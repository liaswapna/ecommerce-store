import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { login, register } from "../api"
import { useAuth } from "../context/AuthContext"

export default function LoginPage() {
    const { login: setToken } = useAuth()
    const navigate = useNavigate()
    const [isRegister, setIsRegister] = useState(false)
    const [name, setName] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        setError(null)
        setLoading(true)
        try {
            if (isRegister) await register(name, email, password)
            const res = await login(email, password)
            setToken(res.access_token)
            navigate("/")
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : "Something went wrong")
        } finally {
            setLoading(false)
        }
    }

    const inputClass = "w-full border border-slate-300 rounded-xl px-3 py-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"

    return (
        <div className="flex justify-center px-4 py-16">
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm w-full max-w-md overflow-hidden">
                <div className="h-1.5 bg-brand" />
                <div className="p-8">
                    <h1 className="text-2xl font-extrabold tracking-tight text-brand-dark">{isRegister ? "Create account" : "Sign in"}</h1>
                    <p className="text-gray-500 text-sm mt-1 mb-6">{isRegister ? "Join MyStore" : "Welcome back"}</p>
                    {error && <p className="bg-red-50 text-red-700 text-sm rounded-xl px-3 py-2 mb-4">{error}</p>}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {isRegister && (
                            <input
                                className={inputClass}
                                placeholder="Name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        )}
                        <input
                            className={inputClass}
                            placeholder="Email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                        <input
                            className={inputClass}
                            placeholder="Password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-brand text-white py-2.5 rounded-xl font-semibold hover:bg-brand-dark transition-colors disabled:opacity-50"
                        >
                            {loading ? "Please wait..." : isRegister ? "Register" : "Login"}
                        </button>
                    </form>
                    <p className="text-sm text-center mt-6 text-gray-500">
                        {isRegister ? "Already have an account?" : "Don't have an account?"}
                        <button
                            className="ml-1 text-brand font-semibold hover:underline"
                            onClick={() => setIsRegister(!isRegister)}
                        >
                            {isRegister ? "Sign in" : "Register"}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    )
}
