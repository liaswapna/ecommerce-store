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

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
                <h1 className="text-2xl font-bold mb-6">{isRegister ? "Create account" : "Sign in"}</h1>
                {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {isRegister && (
                        <input
                            className="w-full border rounded px-3 py-2"
                            placeholder="Name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                        />
                    )}
                    <input
                        className="w-full border rounded px-3 py-2"
                        placeholder="Email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <input
                        className="w-full border rounded px-3 py-2"
                        placeholder="Password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-black text-white py-2 rounded hover:bg-gray-800 disabled:opacity-50"
                    >
                        {loading ? "Please wait..." : isRegister ? "Register" : "Login"}
                    </button>
                </form>
                <p className="text-sm text-center mt-4 text-gray-500">
                    {isRegister ? "Already have an account?" : "Don't have an account?"}
                    <button
                        className="ml-1 text-black underline"
                        onClick={() => setIsRegister(!isRegister)}
                    >
                        {isRegister ? "Sign in" : "Register"}
                    </button>
                </p>
            </div>
        </div>
    )
}
