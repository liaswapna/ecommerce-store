import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Navbar() {
    const { token, user, logout } = useAuth()
    const navigate = useNavigate()

    function handleLogout() {
        logout()
        navigate("/")
    }

    return (
        <nav className="bg-black text-white px-8 py-4 flex justify-between items-center">
            <Link to="/" className="text-xl font-bold">MyStore</Link>
            <div className="flex gap-6 items-center">
                <Link to="/" className="hover:text-gray-300">Products</Link>
                {token ? (
                    <>
                        {user?.is_admin && (
                            <Link to="/admin" className="hover:text-gray-300">Admin</Link>
                        )}
                        {user && !user.is_admin && (
                            <>
                                <Link to="/cart" className="hover:text-gray-300">Cart</Link>
                                <Link to="/orders" className="hover:text-gray-300">Orders</Link>
                            </>
                        )}
                        <button onClick={handleLogout} className="hover:text-gray-300">Logout</button>
                    </>
                ) : (
                    <Link to="/login" className="hover:text-gray-300">Login</Link>
                )}
            </div>
        </nav>
    )
}
