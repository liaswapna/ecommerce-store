import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { getCart, removeFromCart, updateCartQuantity, placeOrder } from "../api"
import type { CartItem } from "../api"
import { useAuth } from "../context/AuthContext"

export default function CartPage() {
    const { token } = useAuth()
    const navigate = useNavigate()
    const [items, setItems] = useState<CartItem[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [placing, setPlacing] = useState(false)
    const [updating, setUpdating] = useState<number | null>(null)

    useEffect(() => {
        if (!token) { navigate("/login"); return }
        getCart(token)
            .then(setItems)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [token])

    async function handleIncrement(item: CartItem) {
        if (!token) return
        setUpdating(item.product_id)
        try {
            await updateCartQuantity(token, item.product_id, item.quantity + 1)
            setItems((prev) => prev.map((i) =>
                i.product_id === item.product_id ? { ...i, quantity: i.quantity + 1 } : i
            ))
        } catch (e: unknown) {
            alert(e instanceof Error ? e.message : "Failed to update cart")
        } finally {
            setUpdating(null)
        }
    }

    async function handleDecrement(item: CartItem) {
        if (!token) return
        setUpdating(item.product_id)
        try {
            if (item.quantity <= 1) {
                await removeFromCart(token, item.product_id)
                setItems((prev) => prev.filter((i) => i.product_id !== item.product_id))
            } else {
                await updateCartQuantity(token, item.product_id, item.quantity - 1)
                setItems((prev) => prev.map((i) =>
                    i.product_id === item.product_id ? { ...i, quantity: i.quantity - 1 } : i
                ))
            }
        } catch (e: unknown) {
            alert(e instanceof Error ? e.message : "Failed to update cart")
        } finally {
            setUpdating(null)
        }
    }

    async function handleRemove(product_id: number) {
        if (!token) return
        await removeFromCart(token, product_id)
        setItems(items.filter((i) => i.product_id !== product_id))
    }

    async function handlePlaceOrder() {
        if (!token) return
        setPlacing(true)
        try {
            const order = await placeOrder(token)
            navigate(`/orders/${order.id}`)
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : "Failed to place order")
            setPlacing(false)
        }
    }

    const total = items.reduce((sum, i) => sum + parseFloat(i.price) * i.quantity, 0)

    if (loading) return <p className="p-8 text-gray-500">Loading cart...</p>
    if (error) return <p className="p-8 text-red-500">{error}</p>
    if (items.length === 0) return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-4">Your Cart</h1>
            <p className="text-gray-500">Your cart is empty.</p>
        </div>
    )

    return (
        <div className="p-8 max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Your Cart</h1>
            <div className="space-y-4">
                {items.map((item) => (
                    <div key={item.product_id} className="flex justify-between items-center border rounded-lg p-4">
                        <div className="flex-1">
                            <p className="font-semibold">{item.name}</p>
                            <p className="text-sm text-gray-500">${item.price} each</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => handleDecrement(item)}
                                disabled={updating === item.product_id}
                                className="w-8 h-8 rounded-full border text-lg font-bold hover:bg-gray-100 disabled:opacity-50"
                            >−</button>
                            <span className="w-6 text-center font-semibold">{item.quantity}</span>
                            <button
                                onClick={() => handleIncrement(item)}
                                disabled={updating === item.product_id || item.quantity >= item.stock}
                                className="w-8 h-8 rounded-full border text-lg font-bold hover:bg-gray-100 disabled:opacity-50"
                            >+</button>
                        </div>
                        <div className="flex items-center gap-4 ml-4">
                            <p className="font-bold w-20 text-right">${(parseFloat(item.price) * item.quantity).toFixed(2)}</p>
                            <button
                                onClick={() => handleRemove(item.product_id)}
                                className="text-red-500 text-sm hover:underline"
                            >
                                Remove
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            <div className="mt-6 flex justify-between items-center">
                <p className="text-xl font-bold">Total: ${total.toFixed(2)}</p>
                <button
                    onClick={handlePlaceOrder}
                    disabled={placing}
                    className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800 disabled:opacity-50"
                >
                    {placing ? "Placing order..." : "Place Order"}
                </button>
            </div>
        </div>
    )
}
