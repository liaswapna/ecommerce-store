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

    const container = "max-w-xl mx-auto px-4 sm:px-8 py-8"
    const inputClass = "w-full border border-slate-300 rounded-xl px-3 py-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
    const labelClass = "block text-sm font-medium text-gray-700 mb-1"

    if (loading) return <p className={`${container} text-gray-500`}>Loading product...</p>

    const categoryOptions = CATEGORIES.includes(form.category) ? CATEGORIES : [...CATEGORIES, form.category]

    return (
        <div className={container}>
            <Link to="/admin" className="text-sm font-semibold text-brand hover:underline">← Back to products</Link>
            <h1 className="text-3xl font-extrabold tracking-tight text-brand-dark mt-4 mb-6">{isEdit ? "Edit product" : "New product"}</h1>
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
                {error && <p className="bg-red-50 text-red-700 text-sm rounded-xl px-3 py-2 mb-4">{error}</p>}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className={labelClass}>Name</label>
                        <input
                            className={inputClass}
                            value={form.name}
                            onChange={(e) => updateField("name", e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <label className={labelClass}>Description</label>
                        <textarea
                            className={inputClass}
                            rows={3}
                            value={form.description}
                            onChange={(e) => updateField("description", e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <label className={labelClass}>Image URL (optional)</label>
                        <input
                            className={inputClass}
                            value={form.image_url}
                            onChange={(e) => updateField("image_url", e.target.value)}
                        />
                    </div>
                    <div>
                        <label className={labelClass}>Category</label>
                        <select
                            className={`${inputClass} capitalize`}
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
                            <label className={labelClass}>Price ($)</label>
                            <input
                                className={inputClass}
                                type="number"
                                step="0.01"
                                min="0.01"
                                value={form.price}
                                onChange={(e) => updateField("price", e.target.value)}
                                required
                            />
                        </div>
                        <div className="flex-1">
                            <label className={labelClass}>Stock</label>
                            <input
                                className={inputClass}
                                type="number"
                                step="1"
                                min="0"
                                value={form.stock}
                                onChange={(e) => updateField("stock", e.target.value)}
                                required
                            />
                        </div>
                    </div>
                    <label className="flex items-start gap-3 pt-1">
                        <input
                            type="checkbox"
                            className="mt-1 w-4 h-4 accent-brand"
                            checked={form.is_active}
                            onChange={(e) => updateField("is_active", e.target.checked)}
                        />
                        <span>
                            <span className="block font-medium text-gray-700">Active</span>
                            <span className="block text-sm text-gray-500">Visible to customers</span>
                        </span>
                    </label>
                    <div className="flex gap-3 pt-2">
                        <button
                            type="submit"
                            disabled={saving}
                            className="bg-brand text-white px-5 py-2.5 rounded-xl font-semibold hover:bg-brand-dark transition-colors disabled:opacity-50"
                        >
                            {saving ? "Saving..." : isEdit ? "Save changes" : "Create product"}
                        </button>
                        <Link
                            to="/admin"
                            className="bg-white border border-brand text-brand px-5 py-2.5 rounded-xl font-semibold hover:bg-accent-soft transition-colors"
                        >
                            Cancel
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    )
}
