import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import client from '../api/client'
import { useAuthStore } from '../store/auth'

const STATUS_COLORS = {
  active: 'bg-green-100 text-green-800',
  suspended: 'bg-yellow-100 text-yellow-800',
  provisioning: 'bg-blue-100 text-blue-800',
  error: 'bg-red-100 text-red-800',
  terminated: 'bg-gray-100 text-gray-800',
  upgrading: 'bg-purple-100 text-purple-800',
}

export default function TenantsPage() {
  const { logout } = useAuthStore()
  const { data: tenants = [], isLoading } = useQuery({
    queryKey: ['tenants'],
    queryFn: () => client.get('/tenants').then(r => r.data),
    refetchInterval: 10_000,
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-indigo-700">Odoo SaaS</h1>
        <div className="flex gap-4 items-center">
          <Link to="/plans" className="text-sm text-gray-600 hover:text-indigo-600">Plans</Link>
          <Link to="/admin" className="text-sm text-gray-600 hover:text-indigo-600">Admin</Link>
          <button onClick={logout} className="text-sm text-red-600 hover:text-red-800">Logout</button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">My Instances</h2>
          <Link to="/tenants/new"
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 font-semibold text-sm">
            + New Instance
          </Link>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-gray-500">Loading...</div>
        ) : tenants.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No instances yet.</p>
            <Link to="/tenants/new" className="text-indigo-600 font-semibold">Create your first instance</Link>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {tenants.map(tenant => (
              <Link key={tenant.id} to={`/tenants/${tenant.id}`}
                className="bg-white rounded-xl shadow-sm p-5 hover:shadow-md transition-shadow border border-gray-100">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{tenant.display_name}</h3>
                    <p className="text-xs text-gray-500">{tenant.subdomain}.myodoo.com</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[tenant.status] || 'bg-gray-100'}`}>
                    {tenant.status}
                  </span>
                </div>
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>CPU</span><span>{tenant.cpu_usage?.toFixed(1)}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full"
                      style={{ width: `${Math.min(tenant.cpu_usage || 0, 100)}%` }} />
                  </div>
                </div>
                <p className="text-xs text-gray-400 mt-3">Odoo {tenant.odoo_version}</p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
