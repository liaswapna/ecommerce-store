const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, options)
    if (!response.ok) {
        const error = await response.json()
        const detail = Array.isArray(error.detail)
            ? error.detail.map((d: { msg: string }) => d.msg).join(", ")
            : error.detail
        throw new Error(detail || "Something went wrong")
    }
    return response.json()
}

function authHeaders(token: string) {
    return { "Content-Type": "application/json", Authorization: `Bearer ${token}` }
}

export interface Product {
    id: number
    name: string
    description: string
    image_url: string | null
    category: string
    price: string
    stock: number
    is_active: boolean
}

export interface User {
    id: number
    name: string
    email: string
    is_admin: boolean
}

export interface ProductInput {
    name: string
    description: string
    image_url: string | null
    category: string
    price: number
    stock: number
    is_active: boolean
}

export interface CartItem {
    product_id: number
    name: string
    price: string
    quantity: number
    stock: number
}

export interface OrderItem {
    product_id: number
    name_at_purchase: string
    quantity: number
    price_at_purchase: string
}

export interface Order {
    id: number
    total_price: string
    status: string
    created_at: string
    items?: OrderItem[]
}

export function getProducts(page = 1, pageSize = 9, category = ""): Promise<Product[]> {
    const path = category ? `/products/category/${category}` : "/products/"
    return request<Product[]>(`${path}?page=${page}&page_size=${pageSize}`)
}

export function login(email: string, password: string): Promise<{ access_token: string }> {
    return request("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    })
}

export function register(name: string, email: string, password: string): Promise<{ access_token: string }> {
    return request("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
    })
}

export function getCart(token: string): Promise<CartItem[]> {
    return request("/cart/", { headers: authHeaders(token) })
}

export function addToCart(token: string, product_id: number, quantity: number): Promise<CartItem> {
    return request("/cart/", {
        method: "POST",
        headers: authHeaders(token),
        body: JSON.stringify({ product_id, quantity }),
    })
}

export function updateCartQuantity(token: string, product_id: number, quantity: number): Promise<CartItem> {
    return request("/cart/", {
        method: "PATCH",
        headers: authHeaders(token),
        body: JSON.stringify({ product_id, quantity }),
    })
}

export function removeFromCart(token: string, product_id: number): Promise<CartItem> {
    return request(`/cart/${product_id}`, { method: "DELETE", headers: authHeaders(token) })
}

export function placeOrder(token: string): Promise<Order> {
    return request("/orders/", { method: "POST", headers: authHeaders(token) })
}

export function getOrders(token: string): Promise<Order[]> {
    return request("/orders/", { headers: authHeaders(token) })
}

export function getOrderById(token: string, id: number): Promise<Order> {
    return request(`/orders/${id}`, { headers: authHeaders(token) })
}

export function getMe(token: string): Promise<User> {
    return request("/auth/me", { headers: authHeaders(token) })
}

export function adminGetProducts(token: string, page = 1, pageSize = 10, category = ""): Promise<Product[]> {
    const path = category
        ? `/admin/products/category/${encodeURIComponent(category)}`
        : "/admin/products/"
    return request(`${path}?page=${page}&page_size=${pageSize}`, { headers: authHeaders(token) })
}

export function adminGetProduct(token: string, id: number): Promise<Product> {
    return request(`/admin/products/${id}`, { headers: authHeaders(token) })
}

export function createProduct(token: string, data: ProductInput): Promise<Product> {
    return request("/admin/products/", { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) })
}

export function updateProduct(token: string, id: number, data: Partial<ProductInput>): Promise<Product> {
    return request(`/admin/products/${id}`, { method: "PUT", headers: authHeaders(token), body: JSON.stringify(data) })
}
