import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { getOrderById } from "../api"
import type { Order } from "../api"
import { useAuth } from "../context/AuthContext"
import { STATUS_STYLES } from "../constants"

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

    const container = "max-w-2xl mx-auto px-4 sm:px-8 py-8"

    if (loading) return <p className={`${container} text-gray-500`}>Loading order...</p>
    if (error) return <p className={`${container} text-red-600`}>{error}</p>
    if (!order) return null

    return (
        <div className={container}>
            <Link to="/orders" className="text-sm font-semibold text-brand hover:underline">← Back to orders</Link>
            <div className="flex items-center gap-3 mt-4">
                <h1 className="text-3xl font-extrabold tracking-tight text-brand-dark">Order #{order.id}</h1>
                <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${STATUS_STYLES[order.status] ?? "bg-gray-100 text-gray-600"}`}>
                    {order.status}
                </span>
            </div>
            <p className="text-gray-500 mt-1 mb-6">{new Date(order.created_at).toLocaleDateString()}</p>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm divide-y divide-slate-200">
                {order.items?.map((item) => (
                    <div key={item.product_id} className="flex justify-between p-4">
                        <div>
                            <p className="font-semibold">{item.name_at_purchase}</p>
                            <p className="text-sm text-gray-500">Qty: {item.quantity} × ${item.price_at_purchase}</p>
                        </div>
                        <p className="font-bold text-brand-dark">${(parseFloat(item.price_at_purchase) * item.quantity).toFixed(2)}</p>
                    </div>
                ))}
                <div className="flex justify-between items-center p-4">
                    <p className="text-gray-500">Total</p>
                    <p className="text-2xl font-extrabold text-brand-dark">${order.total_price}</p>
                </div>
            </div>
        </div>
    )
}
