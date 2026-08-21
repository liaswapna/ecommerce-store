const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, options)
    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Something went wrong")
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

export function getProducts(skip = 0, limit = 20): Promise<Product[]> {
    return request<Product[]>(`/products/?skip=${skip}&limit=${limit}`)
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
