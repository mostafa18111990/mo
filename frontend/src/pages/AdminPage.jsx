import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import client from '../api/client'

export default function AdminPage() {
  const user = useAuthStore(s => s.user)

  const { data: stats } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => client.get('/admin/stats').then(r => r.data),
  })
  const { data: tenants = [] } = useQuery({
    queryKey: ['admin-tenants'],
    queryFn: () => client.get('/admin/tenants').then(r => r.data),
  })
  const { data: users = [] } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => client.get('/admin/users').then(r => r.data),
  })

  if (!user || !['super_admin', 'support'].includes(user.role)) {
    return <div className="p-8 text-center text-red-500">Access denied</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow px-6 py-4 flex justify-between">
        <Link to="/tenants" className="text-indigo-600 text-sm">&larr; My Tenants</Link>
        <h1 className="font-bold text-lg">Admin Panel</h1>
        <span className="text-sm text-gray-500">{user.email}</span>
      </nav>

      <div className="max-w-6xl mx-auto p-6 space-y-6">
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Instances', value: stats.total_tenants },
              { label: 'Active', value: stats.active_tenants, color: 'text-green-600' },
              { label: 'Suspended', value: stats.suspended_tenants, color: 'text-yellow-600' },
              { label: 'Total Users', value: stats.total_users },
            ].map(s => (
              <div key={s.label} className="bg-white rounded-xl shadow-sm p-5 text-center">
                <div className={`text-3xl font-bold ${s.color || 'text-gray-900'}`}>{s.value}</div>
                <div className="text-sm text-gray-500 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="font-semibold mb-4">All Instances</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2">Name</th><th className="pb-2">Subdomain</th>
                  <th className="pb-2">Status</th><th className="pb-2">Version</th>
                  <th className="pb-2">Created</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map(t => (
                  <tr key={t.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="py-2 font-medium">{t.display_name}</td>
                    <td className="py-2 text-gray-500">{t.subdomain}.myodoo.com</td>
                    <td className="py-2"><span className={`text-xs px-2 py-1 rounded-full ${t.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100'}`}>{t.status}</span></td>
                    <td className="py-2">{t.odoo_version}</td>
                    <td className="py-2 text-gray-500">{new Date(t.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="font-semibold mb-4">All Users</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2">Email</th><th className="pb-2">Role</th>
                  <th className="pb-2">Active</th><th className="pb-2">Joined</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="py-2">{u.email}</td>
                    <td className="py-2"><span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-1 rounded">{u.role}</span></td>
                    <td className="py-2">{u.is_active ? 'Yes' : 'No'}</td>
                    <td className="py-2 text-gray-500">{new Date(u.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
