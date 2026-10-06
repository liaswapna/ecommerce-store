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

    const pageButton = "bg-white border border-slate-300 text-brand font-semibold px-4 py-2 rounded-xl hover:bg-accent-soft disabled:opacity-40 disabled:hover:bg-white"

    return (
        <div className="max-w-6xl mx-auto px-4 sm:px-8 py-8">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                <div>
                    <h1 className="text-3xl font-extrabold tracking-tight text-brand-dark">Manage Products</h1>
                    <p className="text-gray-500 mt-1">Create, edit and filter products</p>
                </div>
                <Link
                    to="/admin/products/new"
                    className="bg-brand text-white px-4 py-2.5 rounded-xl font-semibold hover:bg-brand-dark transition-colors"
                >
                    + New product
                </Link>
            </div>

            <div className="mb-4 flex items-center gap-2">
                <label className="text-sm font-medium text-gray-600">Category:</label>
                <select
                    value={category}
                    onChange={(e) => changeCategory(e.target.value)}
                    className="border border-slate-300 rounded-xl px-3 py-2 bg-white capitalize focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
                >
                    <option value="">All</option>
                    {CATEGORIES.map((c) => (
                        <option key={c} value={c}>{c}</option>
                    ))}
                </select>
            </div>

            {error && <p className="bg-red-50 text-red-700 text-sm rounded-xl px-3 py-2 mb-4">{error}</p>}

            {loading ? (
                <p className="text-gray-500">Loading products...</p>
            ) : products.length === 0 ? (
                <p className="text-gray-500">{page > 1 ? "No more products." : "No products found."}</p>
            ) : (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-slate-50 text-left text-xs font-bold uppercase tracking-wide text-gray-500">
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
                                <tr key={product.id} className="border-t border-slate-200 hover:bg-slate-50 transition-colors">
                                    <td className="p-3 font-medium">{product.name}</td>
                                    <td className="p-3">
                                        <span className="text-xs font-bold uppercase tracking-wide text-brand bg-accent-soft px-2.5 py-1 rounded-full">
                                            {product.category}
                                        </span>
                                    </td>
                                    <td className="p-3 font-semibold text-brand-dark">${product.price}</td>
                                    <td className="p-3">{product.stock}</td>
                                    <td className="p-3">
                                        {product.is_active ? (
                                            <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full">Active</span>
                                        ) : (
                                            <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2.5 py-1 rounded-full">Inactive</span>
                                        )}
                                    </td>
                                    <td className="p-3 text-right">
                                        <Link to={`/admin/products/${product.id}/edit`} className="text-brand font-semibold hover:underline">
                                            Edit
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <div className="flex justify-center items-center gap-4 mt-10">
                <button
                    onClick={() => goToPage(page - 1)}
                    disabled={page === 1 || loading}
                    className={pageButton}
                >
                    ← Previous
                </button>
                <span className="text-sm text-gray-500">Page {page}</span>
                <button
                    onClick={() => goToPage(page + 1)}
                    disabled={products.length < PAGE_SIZE || loading}
                    className={pageButton}
                >
                    Next →
                </button>
            </div>
        </div>
    )
}
