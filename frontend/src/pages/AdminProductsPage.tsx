import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { adminGetProducts } from "../api"
import type { Product } from "../api"
import { useAuth } from "../context/AuthContext"
import { CATEGORIES } from "../constants"

const PAGE_SIZE = 10

export default function AdminProductsPage() {
    const { token } = useAuth()
    const [products, setProducts] = useState<Product[]>([])
    const [page, setPage] = useState(1)
    const [category, setCategory] = useState("")
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!token) return
        adminGetProducts(token, page, PAGE_SIZE, category)
            .then((data) => {
                setProducts(data)
                setError(null)
            })
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [token, page, category])

    function changeCategory(value: string) {
        setLoading(true)
        setCategory(value)
        setPage(1)
    }

    function goToPage(newPage: number) {
        setLoading(true)
        setPage(newPage)
    }

    return (
        <div className="p-8">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-3xl font-bold">Manage Products</h1>
                <Link to="/admin/products/new" className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800">
                    + New product
                </Link>
            </div>

            <div className="mb-4">
                <label className="mr-2 text-sm text-gray-600">Category:</label>
                <select
                    value={category}
                    onChange={(e) => changeCategory(e.target.value)}
                    className="border rounded px-3 py-2"
                >
                    <option value="">All</option>
                    {CATEGORIES.map((c) => (
                        <option key={c} value={c}>{c}</option>
                    ))}
                </select>
            </div>

            {error && <p className="text-red-500 mb-4">{error}</p>}

            {loading ? (
                <p className="text-gray-500">Loading products...</p>
            ) : products.length === 0 ? (
                <p className="text-gray-500">{page > 1 ? "No more products." : "No products found."}</p>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full bg-white border rounded-lg">
                        <thead className="bg-gray-50 text-left text-sm text-gray-600">
                            <tr>
                                <th className="p-3">Name</th>
                                <th className="p-3">Category</th>
                                <th className="p-3">Price</th>
                                <th className="p-3">Stock</th>
                                <th className="p-3">Status</th>
                                <th className="p-3"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {products.map((product) => (
                                <tr key={product.id} className="border-t">
                                    <td className="p-3 font-medium">{product.name}</td>
                                    <td className="p-3">{product.category}</td>
                                    <td className="p-3">${product.price}</td>
                                    <td className="p-3">{product.stock}</td>
                                    <td className="p-3">
                                        {product.is_active ? (
                                            <span className="text-green-700 bg-green-100 px-2 py-1 rounded text-xs">Active</span>
                                        ) : (
                                            <span className="text-gray-600 bg-gray-200 px-2 py-1 rounded text-xs">Inactive</span>
                                        )}
                                    </td>
                                    <td className="p-3 text-right">
                                        <Link to={`/admin/products/${product.id}/edit`} className="underline hover:text-gray-600">
                                            Edit
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <div className="flex justify-between items-center mt-6">
                <button
                    onClick={() => goToPage(page - 1)}
                    disabled={page === 1 || loading}
                    className="border px-4 py-2 rounded hover:bg-gray-100 disabled:opacity-50"
                >
                    Previous
                </button>
                <span className="text-sm text-gray-600">Page {page}</span>
                <button
                    onClick={() => goToPage(page + 1)}
                    disabled={products.length < PAGE_SIZE || loading}
                    className="border px-4 py-2 rounded hover:bg-gray-100 disabled:opacity-50"
                >
                    Next
                </button>
            </div>
        </div>
    )
}
