import { useEffect, useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { getProducts, searchProducts, addToCart, getCart, removeFromCart, updateCartQuantity } from "../api"
import type { Product } from "../api"
import { useAuth } from "../context/AuthContext"
import { CATEGORIES } from "../constants"

const PAGE_SIZE = 9

const TILE_STYLES: Record<string, string> = {
    shoes: "from-sky-100 to-sky-50 text-sky-800",
    electronics: "from-emerald-100 to-emerald-50 text-emerald-800",
    clothing: "from-violet-100 to-violet-50 text-violet-800",
    sports: "from-amber-100 to-amber-50 text-amber-800",
}

function ProductImage({ product }: { product: Product }) {
    const [failed, setFailed] = useState(false)
    if (!product.image_url || failed) {
        const style = TILE_STYLES[product.category] ?? "from-slate-100 to-slate-50 text-brand"
        return (
            <div className={`h-48 w-full bg-linear-to-br ${style} flex items-center justify-center text-5xl font-extrabold`}>
                {product.name.charAt(0).toUpperCase()}
            </div>
        )
    }
    return (
        <img
            src={product.image_url}
            alt={product.name}
            onError={() => setFailed(true)}
            className="h-48 w-full object-cover"
        />
    )
}

export default function ProductsPage() {
    const { token, user } = useAuth()
    const isAdmin = user?.is_admin === true
    const navigate = useNavigate()
    const [products, setProducts] = useState<Product[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [adding, setAdding] = useState<number | null>(null)
    const [quantities] = useState<Record<number, number>>({})
    const [cartProductIds, setCartProductIds] = useState<Set<number>>(new Set())
    const [cartQuantities, setCartQuantities] = useState<Record<number, number>>({})
    const [page, setPage] = useState(1)
    const [category, setCategory] = useState("")
    const [searchInput, setSearchInput] = useState("")
    const [search, setSearch] = useState("")

    useEffect(() => {
        const load = search ? searchProducts(search) : getProducts(page, PAGE_SIZE, category)
        load
            .then((data) => {
                setProducts(data)
                setError(null)
            })
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [page, category, search])

    useEffect(() => {
        if (!token || !user || user.is_admin) return
        getCart(token).then((items) => {
            setCartProductIds(new Set(items.map((i) => i.product_id)))
            const qtyMap: Record<number, number> = {}
            items.forEach((i) => { qtyMap[i.product_id] = i.quantity })
            setCartQuantities(qtyMap)
        })
    }, [token, user])

    function goToPage(newPage: number) {
        setLoading(true)
        setPage(newPage)
    }

    function selectCategory(newCategory: string) {
        if (newCategory === category && !search) return
        setLoading(true)
        setSearch("")
        setSearchInput("")
        setCategory(newCategory)
        setPage(1)
    }

    function handleSearch(e: FormEvent) {
        e.preventDefault()
        const q = searchInput.trim()
        if (!q || q === search) return
        setLoading(true)
        setSearch(q)
    }

    function clearSearch() {
        setLoading(true)
        setSearchInput("")
        setSearch("")
        setPage(1)
    }

    function getQty(product_id: number) {
        return quantities[product_id] ?? 1
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

    return (
        <div className="max-w-6xl mx-auto px-4 sm:px-8 py-8">
            <h1 className="text-3xl font-extrabold tracking-tight text-brand-dark">Products</h1>
            <p className="text-gray-500 mt-1 mb-6">Browse our collection</p>
            <form onSubmit={handleSearch} className="flex gap-2 mb-4">
                <input
                    type="search"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    placeholder='Try "gear for a morning run"'
                    maxLength={200}
                    className="flex-1 bg-white border border-slate-300 rounded-xl px-4 py-2.5 focus:outline-none focus:border-accent"
                />
                <button
                    type="submit"
                    className="bg-brand text-white px-5 py-2.5 rounded-xl font-semibold hover:bg-brand-dark transition-colors"
                >
                    Search
                </button>
            </form>
            <div className="flex flex-wrap gap-2 mb-8">
                {["", ...CATEGORIES].map((c) => (
                    <button
                        key={c || "all"}
                        onClick={() => selectCategory(c)}
                        className={`px-4 py-1.5 rounded-full text-sm font-semibold capitalize border transition-colors ${
                            category === c && !search
                                ? "bg-brand text-white border-brand"
                                : "bg-white text-brand border-slate-300 hover:border-accent hover:bg-accent-soft"
                        }`}
                    >
                        {c || "All"}
                    </button>
                ))}
            </div>
            {search && (
                <div className="flex items-center gap-3 mb-6">
                    <p className="text-gray-700">Results for <span className="font-semibold">"{search}"</span></p>
                    <button onClick={clearSearch} className="text-sm text-brand font-semibold hover:underline">
                        ✕ Clear search
                    </button>
                </div>
            )}
            {loading ? (
                <p className="text-gray-500">Loading products...</p>
            ) : error ? (
                <p className="text-red-600">{error}</p>
            ) : (
                <>
                    {products.length === 0 && (
                        <p className="text-gray-500">{search ? "No products match your search." : page > 1 ? "No more products." : "No products found."}</p>
                    )}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {products.map((product) => (
                            <div
                                key={product.id}
                                className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden flex flex-col"
                            >
                                <ProductImage product={product} />
                                <div className="p-5 flex flex-col flex-1">
                                    <span className="self-start text-xs font-bold uppercase tracking-wide text-brand bg-accent-soft px-2.5 py-1 rounded-full">
                                        {product.category}
                                    </span>
                                    <h2 className="text-lg font-bold mt-3">{product.name}</h2>
                                    <p className="text-gray-500 text-sm mt-1 mb-4 flex-1">{product.description}</p>
                                    <div className="flex items-center justify-between mb-4">
                                        <span className="text-xl font-extrabold text-brand-dark">${product.price}</span>
                                        {product.stock > 0 ? (
                                            <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full">
                                                {product.stock} in stock
                                            </span>
                                        ) : (
                                            <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2.5 py-1 rounded-full">
                                                Out of stock
                                            </span>
                                        )}
                                    </div>

                                    {isAdmin ? null : cartProductIds.has(product.id) ? (
                                        <div className="flex items-center justify-between border border-slate-200 rounded-xl px-3 py-2">
                                            <button
                                                onClick={() => handleRemoveFromCart(product.id)}
                                                disabled={adding === product.id}
                                                className="w-8 h-8 rounded-full border border-brand text-brand text-lg font-bold hover:bg-accent-soft disabled:opacity-50"
                                            >−</button>
                                            <span className="font-semibold">{cartQuantities[product.id]}</span>
                                            <button
                                                onClick={() => handleAddToCart(product.id)}
                                                disabled={adding === product.id || cartQuantities[product.id] >= product.stock}
                                                className="w-8 h-8 rounded-full border border-brand text-brand text-lg font-bold hover:bg-accent-soft disabled:opacity-50"
                                            >+</button>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => handleAddToCart(product.id)}
                                            disabled={adding === product.id || product.stock === 0}
                                            className="w-full bg-brand text-white py-2.5 rounded-xl font-semibold hover:bg-brand-dark transition-colors disabled:opacity-50"
                                        >
                                            {adding === product.id ? "Adding..." : product.stock === 0 ? "Out of Stock" : "Add to Cart"}
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
            {!search && (
            <div className="flex justify-center items-center gap-4 mt-10">
                <button
                    onClick={() => goToPage(page - 1)}
                    disabled={page === 1}
                    className="bg-white border border-slate-300 text-brand font-semibold px-4 py-2 rounded-xl hover:bg-accent-soft disabled:opacity-40 disabled:hover:bg-white"
                >
                    ← Previous
                </button>
                <span className="text-sm text-gray-500">Page {page}</span>
                <button
                    onClick={() => goToPage(page + 1)}
                    disabled={products.length < PAGE_SIZE}
                    className="bg-white border border-slate-300 text-brand font-semibold px-4 py-2 rounded-xl hover:bg-accent-soft disabled:opacity-40 disabled:hover:bg-white"
                >
                    Next →
                </button>
            </div>
            )}
        </div>
    )
}
