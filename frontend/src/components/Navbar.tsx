import { Link, NavLink, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

const linkClass = ({ isActive }: { isActive: boolean }) =>
    `pb-1 border-b-2 transition-colors ${
        isActive ? "text-white border-accent" : "text-white/75 border-transparent hover:text-white"
    }`

const buttonClass =
    "border border-accent rounded-full px-4 py-1.5 text-white hover:bg-accent hover:text-brand-dark transition-colors"

export default function Navbar() {
    const { token, user, logout } = useAuth()
    const navigate = useNavigate()

    function handleLogout() {
        logout()
        navigate("/")
    }

    return (
        <nav className="bg-brand text-white px-4 sm:px-8 py-4 flex justify-between items-center shadow-sm">
            <Link to="/" className="text-xl font-extrabold tracking-tight">
                My<span className="text-accent">Store</span>
            </Link>
            <div className="flex gap-4 sm:gap-6 items-center">
                <NavLink to="/" end className={linkClass}>Products</NavLink>
                {token ? (
                    <>
                        {user?.is_admin && (
                            <NavLink to="/admin" className={linkClass}>Admin</NavLink>
                        )}
                        {user && !user.is_admin && (
                            <>
                                <NavLink to="/cart" className={linkClass}>Cart</NavLink>
                                <NavLink to="/orders" className={linkClass}>Orders</NavLink>
                            </>
                        )}
                        <button onClick={handleLogout} className={buttonClass}>Logout</button>
                    </>
                ) : (
                    <Link to="/login" className={buttonClass}>Login</Link>
                )}
            </div>
        </nav>
    )
}
