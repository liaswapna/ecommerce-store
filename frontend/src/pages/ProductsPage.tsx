import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { getProducts, addToCart, getCart, removeFromCart, updateCartQuantity } from "../api"
import type { Product } from "../api"
import { useAuth } from "../context/AuthContext"

export default function ProductsPage() {
    const { token } = useAuth()
    const navigate = useNavigate()
    const [products, setProducts] = useState<Product[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [adding, setAdding] = useState<number | null>(null)
    const [quantities, setQuantities] = useState<Record<number, number>>({})
    const [cartProductIds, setCartProductIds] = useState<Set<number>>(new Set())
    const [cartQuantities, setCartQuantities] = useState<Record<number, number>>({})

    useEffect(() => {
        getProducts()
            .then(setProducts)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))

        if (token) {
            getCart(token).then((items) => {
                setCartProductIds(new Set(items.map((i) => i.product_id)))
                const qtyMap: Record<number, number> = {}
                items.forEach((i) => { qtyMap[i.product_id] = i.quantity })
                setCartQuantities(qtyMap)
            })
        }
    }, [token])

    function getQty(product_id: number) {
        return quantities[product_id] ?? 1
    }

    function changeQty(product_id: number, delta: number, stock: number) {
        setQuantities((prev) => ({
            ...prev,
            [product_id]: Math.min(stock, Math.max(1, (prev[product_id] ?? 1) + delta))
        }))
    }

    async function handleAddToCart(product_id: number) {
        if (!token) { navigate("/login"); return }
        setAdding(product_id)
        try {
            if (cartProductIds.has(product_id)) {
                const newQty = (cartQuantities[product_id] ?? 1) + 1
                await updateCartQuantity(token, product_id, newQty)
                setCartQuantities((prev) => ({ ...prev, [product_id]: newQty }))
            } else {
                await addToCart(token, product_id, getQty(product_id))
                setCartProductIds((prev) => new Set([...prev, product_id]))
                setCartQuantities((prev) => ({ ...prev, [product_id]: getQty(product_id) }))
            }
        } catch (e: unknown) {
            alert(e instanceof Error ? e.message : "Failed to add to cart")
        } finally {
            setAdding(null)
        }
    }

    async function handleRemoveFromCart(product_id: number) {
        if (!token) return
        const currentQty = cartQuantities[product_id] ?? 1
        try {
            if (currentQty <= 1) {
                await removeFromCart(token, product_id)
                setCartProductIds((prev) => { const s = new Set(prev); s.delete(product_id); return s })
                setCartQuantities((prev) => { const q = { ...prev }; delete q[product_id]; return q })
            } else {
                await updateCartQuantity(token, product_id, currentQty - 1)
                setCartQuantities((prev) => ({ ...prev, [product_id]: currentQty - 1 }))
            }
        } catch (e: unknown) {
            alert(e instanceof Error ? e.message : "Failed to update cart")
        }
    }

    if (loading) return <p className="p-8 text-gray-500">Loading products...</p>
    if (error) return <p className="p-8 text-red-500">{error}</p>
    if (products.length === 0) return <p className="p-8 text-gray-500">No products found.</p>

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6">Products</h1>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                    <div key={product.id} className="border rounded-lg p-4 shadow-sm bg-white flex flex-col">
                        {product.image_url && (
                            <img
                                src={product.image_url}
                                alt={product.name}
                                className="w-full h-48 object-cover rounded mb-3"
                            />
                        )}
                        <p className="text-xs text-gray-400 uppercase mb-1">{product.category}</p>
                        <h2 className="text-lg font-semibold">{product.name}</h2>
                        <p className="text-gray-500 text-sm mt-1 mb-3 flex-1">{product.description}</p>
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-xl font-bold">${product.price}</span>
                            <span className="text-sm text-gray-400">{product.stock} in stock</span>
                        </div>

                        {cartProductIds.has(product.id) ? (
                            <div className="flex items-center justify-between border rounded-lg px-3 py-2">
                                <button
                                    onClick={() => handleRemoveFromCart(product.id)}
                                    disabled={adding === product.id}
                                    className="w-8 h-8 rounded-full border text-lg font-bold hover:bg-gray-100 disabled:opacity-50"
                                >−</button>
                                <span className="font-semibold">{cartQuantities[product.id]}</span>
                                <button
                                    onClick={() => handleAddToCart(product.id)}
                                    disabled={adding === product.id || cartQuantities[product.id] >= product.stock}
                                    className="w-8 h-8 rounded-full border text-lg font-bold hover:bg-gray-100 disabled:opacity-50"
                                >+</button>
                            </div>
                        ) : (
                            <button
                                onClick={() => handleAddToCart(product.id)}
                                disabled={adding === product.id || product.stock === 0}
                                className="w-full bg-black text-white py-2 rounded hover:bg-gray-800 disabled:opacity-50"
                            >
                                {adding === product.id ? "Adding..." : product.stock === 0 ? "Out of Stock" : "Add to Cart"}
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}
