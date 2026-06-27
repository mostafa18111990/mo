import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import client from '../api/client'

export default function NewTenantPage() {
  const navigate = useNavigate()
  const [slug, setSlug] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [planCode, setPlanCode] = useState('')
  const [billingPeriod, setBillingPeriod] = useState('monthly')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { data: plans = [] } = useQuery({
    queryKey: ['plans'],
    queryFn: () => client.get('/plans').then(r => r.data),
  })

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data: tenant } = await client.post('/tenants', {
        slug, display_name: displayName, plan_code: planCode, billing_period: billingPeriod,
      })
      navigate(`/tenants/${tenant.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create instance')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow px-6 py-4">
        <Link to="/tenants" className="text-indigo-600 hover:text-indigo-800 text-sm">&larr; Back</Link>
      </nav>
      <div className="max-w-xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">New Odoo Instance</h1>
        {error && <p className="text-red-600 text-sm mb-4 bg-red-50 p-3 rounded">{error}</p>}

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Display Name</label>
            <input value={displayName} onChange={e => setDisplayName(e.target.value)}
              placeholder="My Company" required
              className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Subdomain</label>
            <div className="flex items-center border rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500">
              <input value={slug} onChange={e => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                placeholder="my-company" required
                className="flex-1 px-4 py-2 outline-none" />
              <span className="bg-gray-50 px-3 py-2 text-gray-500 text-sm border-l">.myodoo.com</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Plan</label>
            <div className="space-y-2">
              {plans.map(plan => (
                <label key={plan.code} className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors
                  ${planCode === plan.code ? 'border-indigo-500 bg-indigo-50' : 'hover:bg-gray-50'}`}>
                  <input type="radio" name="plan" value={plan.code}
                    checked={planCode === plan.code} onChange={() => setPlanCode(plan.code)}
                    className="mr-3" />
                  <div className="flex-1">
                    <span className="font-medium">{plan.name}</span>
                    <span className="text-gray-500 text-sm ml-2">
                      ${billingPeriod === 'monthly' ? (plan.monthly_price_cents / 100).toFixed(0) : (plan.yearly_price_cents / 100).toFixed(0)}/
                      {billingPeriod === 'monthly' ? 'mo' : 'yr'}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">{plan.max_users} users · {plan.max_storage_gb}GB</span>
                </label>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Billing Period</label>
            <div className="flex gap-3">
              {['monthly', 'yearly'].map(p => (
                <button key={p} type="button" onClick={() => setBillingPeriod(p)}
                  className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-colors
                    ${billingPeriod === p ? 'bg-indigo-600 text-white border-indigo-600' : 'hover:bg-gray-50'}`}>
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                  {p === 'yearly' && <span className="ml-1 text-xs opacity-75">(save 15%)</span>}
                </button>
              ))}
            </div>
          </div>
          <button type="submit" disabled={loading || !planCode}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-semibold">
            {loading ? 'Creating...' : 'Create Instance'}
          </button>
        </form>
      </div>
    </div>
  )
}
