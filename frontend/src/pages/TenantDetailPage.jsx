import React, { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import client from '../api/client'

const STATUS_COLORS = {
  active: 'bg-green-100 text-green-800',
  suspended: 'bg-yellow-100 text-yellow-800',
  provisioning: 'bg-blue-100 text-blue-800',
  error: 'bg-red-100 text-red-800',
  terminated: 'bg-gray-100 text-gray-800',
  upgrading: 'bg-purple-100 text-purple-800',
}

const STATUS_AR = {
  active: 'نشط',
  suspended: 'موقوف',
  provisioning: 'جارٍ الإنشاء...',
  error: 'خطأ',
  terminated: 'محذوف',
  upgrading: 'جارٍ التحديث',
}

export default function TenantDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [showLogs, setShowLogs] = useState(false)
  const [upgradeVersion, setUpgradeVersion] = useState('')

  const { data: tenant, isLoading } = useQuery({
    queryKey: ['tenant', id],
    queryFn: () => client.get(`/tenants/${id}`).then(r => r.data),
    refetchInterval: 15_000,
  })

  const { data: sectors = [] } = useQuery({
    queryKey: ['sectors'],
    queryFn: () => client.get('/sectors').then(r => r.data),
  })

  const { data: logs } = useQuery({
    queryKey: ['tenant-logs', id],
    queryFn: () => client.get(`/monitoring/${id}/logs`).then(r => r.data.logs),
    enabled: showLogs,
  })

  const actionMutation = useMutation({
    mutationFn: ({ action, target_version }) =>
      client.post(`/tenants/${id}/action`, { action, target_version }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tenant', id] })
      qc.invalidateQueries({ queryKey: ['tenants'] })
    },
  })

  if (isLoading) return <div className="p-8 text-center text-gray-500">Loading...</div>
  if (!tenant) return <div className="p-8 text-center text-red-500">Tenant not found</div>

  const runAction = (action, target_version) => {
    if (action === 'delete' && !confirm('حذف هذه النسخة؟ لا يمكن التراجع عن هذه العملية.')) return
    actionMutation.mutate({ action, target_version })
  }

  const sectorInfo = sectors.find(s => s.code === tenant.sector_code)

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <nav className="bg-white shadow px-6 py-4">
        <Link to="/tenants" className="text-indigo-600 hover:text-indigo-800 text-sm">← العودة للنسخ</Link>
      </nav>

      <div className="max-w-4xl mx-auto p-6 space-y-6">
        {/* بيانات النسخة */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold">{tenant.display_name}</h1>
              <p className="text-gray-500 text-sm mt-1" dir="ltr">{tenant.subdomain}.myodoo.com</p>
              {tenant.company_email && (
                <p className="text-gray-400 text-sm mt-0.5" dir="ltr">{tenant.company_email}</p>
              )}
              {tenant.company_phone && (
                <p className="text-gray-400 text-sm mt-0.5" dir="ltr">{tenant.company_phone}</p>
              )}
            </div>
            <span className={`text-sm px-3 py-1 rounded-full font-medium ${STATUS_COLORS[tenant.status] || 'bg-gray-100'}`}>
              {STATUS_AR[tenant.status] || tenant.status}
            </span>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div><span className="text-gray-500">الإصدار:</span> Odoo {tenant.odoo_version}</div>
            <div><span className="text-gray-500">المعالج:</span> {tenant.cpu_usage?.toFixed(2)}%</div>
            <div><span className="text-gray-500">الذاكرة:</span> {tenant.memory_usage?.toFixed(0)} MB</div>
            <div><span className="text-gray-500">تاريخ الإنشاء:</span> {new Date(tenant.created_at).toLocaleDateString('ar-SA')}</div>
          </div>
        </div>

        {/* القطاع والموديولات */}
        {sectorInfo && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="font-semibold mb-3">القطاع والموديولات المثبتة</h2>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">{sectorInfo.icon}</span>
              <div>
                <div className="font-bold text-gray-900">{sectorInfo.name_ar}</div>
                <div className="text-sm text-gray-500">{sectorInfo.description_ar}</div>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {sectorInfo.modules?.map(m => (
                <span key={m} className="text-xs bg-indigo-50 border border-indigo-200 text-indigo-700 px-2 py-1 rounded font-mono">
                  {m}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* الإجراءات */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="font-semibold mb-4">الإجراءات</h2>
          <div className="flex flex-wrap gap-3">
            <a href={`https://${tenant.subdomain}.myodoo.com`} target="_blank" rel="noreferrer"
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700">
              فتح النسخة
            </a>
            <button onClick={() => runAction('restart')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700">
              إعادة التشغيل
            </button>
            {tenant.status === 'active' ? (
              <button onClick={() => runAction('suspend')}
                className="bg-yellow-500 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-yellow-600">
                إيقاف مؤقت
              </button>
            ) : tenant.status === 'suspended' ? (
              <button onClick={() => runAction('resume')}
                className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-700">
                إعادة تفعيل
              </button>
            ) : null}
            <button onClick={() => runAction('backup')}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-700">
              نسخ احتياطي
            </button>
            <button onClick={() => runAction('delete')}
              className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-red-700">
              حذف النسخة
            </button>
          </div>

          <div className="mt-4 flex gap-2 items-center" dir="ltr">
            <input value={upgradeVersion} onChange={e => setUpgradeVersion(e.target.value)}
              placeholder="Target version (e.g. 17.0.2)"
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            <button onClick={() => runAction('upgrade', upgradeVersion)}
              disabled={!upgradeVersion}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-purple-700 disabled:opacity-50">
              ترقية
            </button>
          </div>
        </div>

        {/* السجلات */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-center mb-3">
            <h2 className="font-semibold">سجلات النظام</h2>
            <button onClick={() => setShowLogs(!showLogs)}
              className="text-sm text-indigo-600 hover:text-indigo-800">
              {showLogs ? 'إخفاء' : 'إظهار'} السجلات
            </button>
          </div>
          {showLogs && (
            <pre className="bg-gray-900 text-green-400 text-xs p-4 rounded-lg overflow-auto max-h-80 font-mono" dir="ltr">
              {logs || 'No logs available'}
            </pre>
          )}
        </div>
      </div>
    </div>
  )
}
