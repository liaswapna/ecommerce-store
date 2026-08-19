const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, options)
    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Something went wrong")
    }
    return response.json()
}

export interface Product {
    id: number
    name: string
    description: string
    image_url: string | null
    category: string
    price: string
    stock: number
}

export function getProducts(skip = 0, limit = 20): Promise<Product[]> {
    return request<Product[]>(`/products/?skip=${skip}&limit=${limit}`)
}
