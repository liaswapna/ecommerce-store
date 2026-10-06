import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { adminGetProduct, createProduct, updateProduct } from "../api"
import type { ProductInput } from "../api"
import { useAuth } from "../context/AuthContext"
import { CATEGORIES } from "../constants"

interface FormState {
    name: string
    description: string
    image_url: string
    category: string
    price: string
    stock: string
    is_active: boolean
}

const EMPTY_FORM: FormState = {
    name: "",
    description: "",
    image_url: "",
    category: CATEGORIES[0],
    price: "",
    stock: "",
    is_active: true,
}

export default function AdminProductFormPage() {
    const { id } = useParams()
    const isEdit = id !== undefined
    const { token } = useAuth()
    const navigate = useNavigate()
    const [form, setForm] = useState<FormState>(EMPTY_FORM)
    const [loading, setLoading] = useState(isEdit)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!token || !id) return
        adminGetProduct(token, Number(id))
            .then((p) =>
                setForm({
                    name: p.name,
                    description: p.description,
                    image_url: p.image_url ?? "",
                    category: p.category,
                    price: p.price,
                    stock: String(p.stock),
                    is_active: p.is_active,
                })
            )
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [token, id])

    function updateField<K extends keyof FormState>(field: K, value: FormState[K]) {
        setForm((prev) => ({ ...prev, [field]: value }))
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        if (!token) return
        const price = Number(form.price)
        const stock = Number(form.stock)
        if (!(price > 0)) {
            setError("Price must be greater than 0")
            return
        }
        if (!Number.isInteger(stock) || stock < 0) {
            setError("Stock must be a whole number, 0 or more")
            return
        }
        const data: ProductInput = {
            name: form.name.trim(),
            description: form.description.trim(),
            image_url: form.image_url.trim() || null,
            category: form.category,
            price,
            stock,
            is_active: form.is_active,
        }
        setError(null)
        setSaving(true)
        try {
            if (isEdit) await updateProduct(token, Number(id), data)
            else await createProduct(token, data)
            navigate("/admin")
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : "Something went wrong")
        } finally {
            setSaving(false)
        }
    }

    if (loading) return <p className="p-8 text-gray-500">Loading product...</p>

    const categoryOptions = CATEGORIES.includes(form.category) ? CATEGORIES : [...CATEGORIES, form.category]

    return (
        <div className="p-8 max-w-xl">
            <h1 className="text-3xl font-bold mb-6">{isEdit ? "Edit product" : "New product"}</h1>
            {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-gray-600 mb-1">Name</label>
                    <input
                        className="w-full border rounded px-3 py-2"
                        value={form.name}
                        onChange={(e) => updateField("name", e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-600 mb-1">Description</label>
                    <textarea
                        className="w-full border rounded px-3 py-2"
                        rows={3}
                        value={form.description}
                        onChange={(e) => updateField("description", e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-600 mb-1">Image URL (optional)</label>
                    <input
                        className="w-full border rounded px-3 py-2"
                        value={form.image_url}
                        onChange={(e) => updateField("image_url", e.target.value)}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-600 mb-1">Category</label>
                    <select
                        className="w-full border rounded px-3 py-2"
                        value={form.category}
                        onChange={(e) => updateField("category", e.target.value)}
                    >
                        {categoryOptions.map((c) => (
                            <option key={c} value={c}>{c}</option>
                        ))}
                    </select>
                </div>
                <div className="flex gap-4">
                    <div className="flex-1">
                        <label className="block text-sm text-gray-600 mb-1">Price ($)</label>
                        <input
                            className="w-full border rounded px-3 py-2"
                            type="number"
                            step="0.01"
                            min="0.01"
                            value={form.price}
                            onChange={(e) => updateField("price", e.target.value)}
                            required
                        />
                    </div>
                    <div className="flex-1">
                        <label className="block text-sm text-gray-600 mb-1">Stock</label>
                        <input
                            className="w-full border rounded px-3 py-2"
                            type="number"
                            step="1"
                            min="0"
                            value={form.stock}
                            onChange={(e) => updateField("stock", e.target.value)}
                            required
                        />
                    </div>
                </div>
                <label className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        checked={form.is_active}
                        onChange={(e) => updateField("is_active", e.target.checked)}
                    />
                    <span>Active (visible to customers)</span>
                </label>
                <div className="flex gap-3 pt-2">
                    <button
                        type="submit"
                        disabled={saving}
                        className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800 disabled:opacity-50"
                    >
                        {saving ? "Saving..." : isEdit ? "Save changes" : "Create product"}
                    </button>
                    <Link to="/admin" className="border px-4 py-2 rounded hover:bg-gray-100">Cancel</Link>
                </div>
            </form>
        </div>
    )
}
