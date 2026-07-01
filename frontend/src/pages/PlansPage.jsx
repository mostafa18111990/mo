import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import client from '../api/client'

export default function PlansPage() {
  const { data: plans = [] } = useQuery({
    queryKey: ['plans'],
    queryFn: () => client.get('/plans').then(r => r.data),
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow px-6 py-4 flex justify-between">
        <Link to="/tenants" className="text-indigo-600 text-sm">&larr; Dashboard</Link>
        <h1 className="font-bold text-lg">Plans & Pricing</h1>
        <span />
      </nav>
      <div className="max-w-5xl mx-auto p-6">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold">Simple, transparent pricing</h2>
          <p className="text-gray-500 mt-2">Full Odoo ERP, hosted and managed for you</p>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {plans.map((plan, i) => (
            <div key={plan.code} className={`bg-white rounded-2xl shadow-sm p-8 border-2 transition
              ${i === 1 ? 'border-indigo-500 shadow-lg scale-105' : 'border-transparent'}`}>
              {i === 1 && <div className="text-xs bg-indigo-600 text-white px-3 py-1 rounded-full w-fit mb-3">Most Popular</div>}
              <h3 className="text-xl font-bold">{plan.name}</h3>
              <div className="mt-3 mb-6">
                <span className="text-4xl font-bold">${(plan.monthly_price_cents / 100).toFixed(0)}</span>
                <span className="text-gray-500">/mo</span>
              </div>
              <ul className="space-y-2 text-sm text-gray-600 mb-8">
                <li>✓ Up to {plan.max_users} users</li>
                <li>✓ {plan.max_storage_gb} GB storage</li>
                <li>✓ {plan.cpu_limit} vCPU / {plan.memory_limit} RAM</li>
                <li>✓ Daily backups</li>
                <li>✓ SSL certificate</li>
                <li>✓ Custom subdomain</li>
              </ul>
              <Link to="/tenants/new"
                className={`block text-center py-3 rounded-lg font-semibold text-sm transition
                  ${i === 1 ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'border border-indigo-600 text-indigo-600 hover:bg-indigo-50'}`}>
                Get Started
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
