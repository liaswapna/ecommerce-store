import { useEffect, useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { getOrders } from "../api"
import type { Order } from "../api"
import { useAuth } from "../context/AuthContext"
import { STATUS_STYLES } from "../constants"

export default function OrdersPage() {
    const { token } = useAuth()
    const navigate = useNavigate()
    const [orders, setOrders] = useState<Order[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!token) { navigate("/login"); return }
        getOrders(token)
            .then(setOrders)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [token])

    const container = "max-w-2xl mx-auto px-4 sm:px-8 py-8"

    if (loading) return <p className={`${container} text-gray-500`}>Loading orders...</p>
    if (error) return <p className={`${container} text-red-600`}>{error}</p>
    if (orders.length === 0) return (
        <div className={container}>
            <h1 className="text-3xl font-extrabold tracking-tight text-brand-dark mb-6">Your Orders</h1>
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center">
                <p className="text-gray-500 mb-4">No orders yet.</p>
                <Link
                    to="/"
                    className="inline-block bg-brand text-white px-5 py-2.5 rounded-xl font-semibold hover:bg-brand-dark transition-colors"
                >
                    Browse products
                </Link>
            </div>
        </div>
    )

    return (
        <div className={container}>
            <h1 className="text-3xl font-extrabold tracking-tight text-brand-dark">Your Orders</h1>
            <p className="text-gray-500 mt-1 mb-6">{orders.length} order{orders.length === 1 ? "" : "s"}</p>
            <div className="space-y-4">
                {orders.map((order) => (
                    <Link
                        key={order.id}
                        to={`/orders/${order.id}`}
                        className="block bg-white rounded-2xl border border-slate-200 shadow-sm p-4 hover:border-accent hover:shadow-md transition"
                    >
                        <div className="flex justify-between items-center gap-4">
                            <div className="flex-1">
                                <p className="font-semibold">Order #{order.id}</p>
                                <p className="text-sm text-gray-500">{new Date(order.created_at).toLocaleDateString()}</p>
                            </div>
                            <div className="text-right">
                                <p className="font-extrabold text-brand-dark">${order.total_price}</p>
                                <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${STATUS_STYLES[order.status] ?? "bg-gray-100 text-gray-600"}`}>
                                    {order.status}
                                </span>
                            </div>
                            <span className="text-2xl text-slate-300">›</span>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    )
}
