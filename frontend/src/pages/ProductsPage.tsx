import { useEffect, useState } from "react"
import { getProducts } from "../api"
import type { Product } from "../api"

export default function ProductsPage() {
    const [products, setProducts] = useState<Product[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        getProducts()
            .then(setProducts)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [])

    if (loading) return <p className="p-8 text-gray-500">Loading products...</p>
    if (error) return <p className="p-8 text-red-500">{error}</p>
    if (products.length === 0) return <p className="p-8 text-gray-500">No products found.</p>

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6">Products</h1>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                    <div key={product.id} className="border rounded-lg p-4 shadow-sm bg-white">
                        {product.image_url && (
                            <img
                                src={product.image_url}
                                alt={product.name}
                                className="w-full h-48 object-cover rounded mb-3"
                            />
                        )}
                        <p className="text-xs text-gray-400 uppercase mb-1">{product.category}</p>
                        <h2 className="text-lg font-semibold">{product.name}</h2>
                        <p className="text-gray-500 text-sm mt-1 mb-3">{product.description}</p>
                        <div className="flex items-center justify-between">
                            <span className="text-xl font-bold">${product.price}</span>
                            <span className="text-sm text-gray-400">{product.stock} in stock</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
