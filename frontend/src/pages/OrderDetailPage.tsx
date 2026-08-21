import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { getOrderById } from "../api"
import type { Order } from "../api"
import { useAuth } from "../context/AuthContext"

export default function OrderDetailPage() {
    const { token } = useAuth()
    const navigate = useNavigate()
    const { id } = useParams<{ id: string }>()
    const [order, setOrder] = useState<Order | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!token) { navigate("/login"); return }
        getOrderById(token, Number(id))
            .then(setOrder)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [token, id])

    if (loading) return <p className="p-8 text-gray-500">Loading order...</p>
    if (error) return <p className="p-8 text-red-500">{error}</p>
    if (!order) return null

    return (
        <div className="p-8 max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold mb-2">Order #{order.id}</h1>
            <p className="text-gray-500 mb-1">{new Date(order.created_at).toLocaleDateString()}</p>
            <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 capitalize">{order.status}</span>

            <div className="mt-6 space-y-3">
                {order.items?.map((item) => (
                    <div key={item.product_id} className="flex justify-between border rounded-lg p-4">
                        <div>
                            <p className="font-semibold">{item.name_at_purchase}</p>
                            <p className="text-sm text-gray-500">Qty: {item.quantity} × ${item.price_at_purchase}</p>
                        </div>
                        <p className="font-bold">${(parseFloat(item.price_at_purchase) * item.quantity).toFixed(2)}</p>
                    </div>
                ))}
            </div>

            <div className="mt-6 text-right">
                <p className="text-xl font-bold">Total: ${order.total_price}</p>
            </div>
        </div>
    )
}
