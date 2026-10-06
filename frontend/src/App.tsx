import { lazy, Suspense } from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import Navbar from "./components/Navbar"
import AdminRoute from "./components/AdminRoute"
import ProductsPage from "./pages/ProductsPage"
import LoginPage from "./pages/LoginPage"
import CartPage from "./pages/CartPage"
import OrdersPage from "./pages/OrdersPage"
import OrderDetailPage from "./pages/OrderDetailPage"

const AdminProductsPage = lazy(() => import("./pages/AdminProductsPage"))
const AdminProductFormPage = lazy(() => import("./pages/AdminProductFormPage"))

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Suspense fallback={<p className="p-8 text-gray-500">Loading...</p>}>
          <Routes>
            <Route path="/" element={<ProductsPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/orders/:id" element={<OrderDetailPage />} />
            <Route path="/admin" element={<AdminRoute><AdminProductsPage /></AdminRoute>} />
            <Route path="/admin/products/new" element={<AdminRoute><AdminProductFormPage /></AdminRoute>} />
            <Route path="/admin/products/:id/edit" element={<AdminRoute><AdminProductFormPage /></AdminRoute>} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
