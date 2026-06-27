import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import client from '../api/client'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setToken, setUser } = useAuthStore()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await client.post('/auth/login', { email, password })
      setToken(data.access_token)
      const me = await client.get('/auth/me')
      setUser(me.data)
      navigate('/tenants')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Sign In</h1>
        {error && <p className="text-red-600 text-sm mb-4 bg-red-50 p-3 rounded">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)}
            className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
          <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)}
            className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
          <button type="submit" disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-semibold">
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          Don't have an account? <Link to="/register" className="text-indigo-600 font-semibold">Register</Link>
        </p>
      </div>
    </div>
  )
}
