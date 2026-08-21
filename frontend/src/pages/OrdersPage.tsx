import { useEffect, useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { getOrders } from "../api"
import type { Order } from "../api"
import { useAuth } from "../context/AuthContext"

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

    if (loading) return <p className="p-8 text-gray-500">Loading orders...</p>
    if (error) return <p className="p-8 text-red-500">{error}</p>
    if (orders.length === 0) return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-4">Your Orders</h1>
            <p className="text-gray-500">No orders yet.</p>
        </div>
    )

    return (
        <div className="p-8 max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Your Orders</h1>
            <div className="space-y-4">
                {orders.map((order) => (
                    <Link
                        key={order.id}
                        to={`/orders/${order.id}`}
                        className="block border rounded-lg p-4 hover:shadow-md transition"
                    >
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="font-semibold">Order #{order.id}</p>
                                <p className="text-sm text-gray-500">{new Date(order.created_at).toLocaleDateString()}</p>
                            </div>
                            <div className="text-right">
                                <p className="font-bold">${order.total_price}</p>
                                <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 capitalize">{order.status}</span>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    )
}
