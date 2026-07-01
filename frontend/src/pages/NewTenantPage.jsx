import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import client from '../api/client'

const SECTOR_ICONS = {
  retail: '🛍️',
  services: '🤝',
  manufacturing: '🏭',
  custom: '⚙️',
}

export default function NewTenantPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1=sector, 2=company info, 3=plan
  const [sectorCode, setSectorCode] = useState('')
  const [slug, setSlug] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [companyEmail, setCompanyEmail] = useState('')
  const [companyPhone, setCompanyPhone] = useState('')
  const [planCode, setPlanCode] = useState('')
  const [billingPeriod, setBillingPeriod] = useState('monthly')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { data: sectors = [] } = useQuery({
    queryKey: ['sectors'],
    queryFn: () => client.get('/sectors').then(r => r.data),
  })
  const { data: plans = [] } = useQuery({
    queryKey: ['plans'],
    queryFn: () => client.get('/plans').then(r => r.data),
  })

  const selectedSector = sectors.find(s => s.code === sectorCode)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data: tenant } = await client.post('/tenants', {
        slug,
        display_name: displayName,
        plan_code: planCode,
        billing_period: billingPeriod,
        sector_code: sectorCode,
        company_email: companyEmail,
        company_phone: companyPhone,
      })
      navigate(`/tenants/${tenant.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'فشل إنشاء الحساب')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow px-6 py-4">
        <Link to="/tenants" className="text-indigo-600 hover:text-indigo-800 text-sm">
          ← العودة
        </Link>
      </nav>

      <div className="max-w-2xl mx-auto p-6">
        {/* خطوات */}
        <div className="flex items-center mb-8 gap-2">
          {['اختيار القطاع', 'بيانات الشركة', 'الخطة والإطلاق'].map((label, i) => (
            <React.Fragment key={i}>
              <div className={`flex items-center gap-2 text-sm font-medium
                ${step === i + 1 ? 'text-indigo-600' : step > i + 1 ? 'text-green-600' : 'text-gray-400'}`}>
                <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold
                  ${step === i + 1 ? 'bg-indigo-600 text-white' : step > i + 1 ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>
                  {step > i + 1 ? '✓' : i + 1}
                </span>
                {label}
              </div>
              {i < 2 && <div className="flex-1 h-px bg-gray-200" />}
            </React.Fragment>
          ))}
        </div>

        {/* الخطوة 1: اختيار القطاع */}
        {step === 1 && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold mb-2">اختر قطاع نشاطك التجاري</h2>
            <p className="text-gray-500 text-sm mb-6">
              سيتم تثبيت موديولات Odoo المناسبة لقطاعك تلقائياً
            </p>
            <div className="grid grid-cols-2 gap-4">
              {sectors.map(sector => (
                <button
                  key={sector.code}
                  onClick={() => setSectorCode(sector.code)}
                  className={`p-5 rounded-xl border-2 text-right transition-all
                    ${sectorCode === sector.code
                      ? 'border-indigo-500 bg-indigo-50 shadow-md'
                      : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'}`}
                >
                  <div className="text-3xl mb-2">{sector.icon}</div>
                  <div className="font-bold text-gray-900">{sector.name_ar}</div>
                  <div className="text-xs text-gray-500 mt-1">{sector.description_ar}</div>
                </button>
              ))}
            </div>

            {selectedSector && (
              <div className="mt-5 p-4 bg-indigo-50 rounded-lg border border-indigo-100">
                <p className="text-sm font-medium text-indigo-800 mb-2">
                  الموديولات التي ستُثبَّت تلقائياً:
                </p>
                <div className="flex flex-wrap gap-1">
                  {selectedSector.modules?.map(m => (
                    <span key={m} className="text-xs bg-white border border-indigo-200 text-indigo-700 px-2 py-1 rounded">
                      {m}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => setStep(2)}
              disabled={!sectorCode}
              className="mt-6 w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold
                hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              التالي ←
            </button>
          </div>
        )}

        {/* الخطوة 2: بيانات الشركة */}
        {step === 2 && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold mb-2">بيانات شركتك</h2>
            <p className="text-gray-500 text-sm mb-6">
              ستُحفظ هذه البيانات تلقائياً في إعدادات الشركة داخل Odoo
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  اسم الشركة <span className="text-red-500">*</span>
                </label>
                <input
                  value={displayName}
                  onChange={e => setDisplayName(e.target.value)}
                  placeholder="شركة الأمثلة للتجارة"
                  required
                  className="w-full border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  النطاق الفرعي <span className="text-red-500">*</span>
                </label>
                <div className="flex items-center border rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500">
                  <input
                    value={slug}
                    onChange={e => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                    placeholder="my-company"
                    required
                    className="flex-1 px-4 py-2.5 outline-none"
                    dir="ltr"
                  />
                  <span className="bg-gray-50 px-3 py-2.5 text-gray-500 text-sm border-l">
                    .myodoo.com
                  </span>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  البريد الإلكتروني للشركة
                </label>
                <input
                  type="email"
                  value={companyEmail}
                  onChange={e => setCompanyEmail(e.target.value)}
                  placeholder="info@company.com"
                  className="w-full border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  dir="ltr"
                />
                <p className="text-xs text-gray-400 mt-1">
                  سيُستخدم أيضاً كبريد تسجيل الدخول لـ Odoo
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  رقم الهاتف
                </label>
                <input
                  type="tel"
                  value={companyPhone}
                  onChange={e => setCompanyPhone(e.target.value)}
                  placeholder="+966 5x xxx xxxx"
                  className="w-full border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  dir="ltr"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setStep(1)}
                className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-50">
                ← السابق
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={!displayName || !slug}
                className="flex-1 bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
              >
                التالي ←
              </button>
            </div>
          </div>
        )}

        {/* الخطوة 3: الخطة والإطلاق */}
        {step === 3 && (
          <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold mb-2">اختر خطة الاشتراك</h2>
            <p className="text-gray-500 text-sm mb-6">اختر الخطة المناسبة لحجم نشاطك</p>

            {error && <p className="text-red-600 text-sm mb-4 bg-red-50 p-3 rounded">{error}</p>}

            <div className="space-y-3 mb-5">
              {plans.map(plan => (
                <label key={plan.code}
                  className={`flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all
                    ${planCode === plan.code ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200 hover:border-indigo-300'}`}>
                  <input type="radio" name="plan" value={plan.code}
                    checked={planCode === plan.code} onChange={() => setPlanCode(plan.code)}
                    className="ml-3" />
                  <div className="flex-1">
                    <div className="font-bold">{plan.name}</div>
                    <div className="text-xs text-gray-500">{plan.max_users} مستخدم · {plan.max_storage_gb} GB</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-indigo-700">
                      ${billingPeriod === 'monthly'
                        ? (plan.monthly_price_cents / 100).toFixed(0)
                        : (plan.yearly_price_cents / 100).toFixed(0)}
                    </div>
                    <div className="text-xs text-gray-400">/{billingPeriod === 'monthly' ? 'شهر' : 'سنة'}</div>
                  </div>
                </label>
              ))}
            </div>

            <div className="flex gap-3 mb-6">
              {['monthly', 'yearly'].map(p => (
                <button key={p} type="button" onClick={() => setBillingPeriod(p)}
                  className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-colors
                    ${billingPeriod === p ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 hover:bg-gray-50'}`}>
                  {p === 'monthly' ? 'شهري' : 'سنوي'}
                  {p === 'yearly' && <span className="mr-1 text-xs opacity-75">(وفر 15%)</span>}
                </button>
              ))}
            </div>

            {/* ملخص */}
            <div className="bg-gray-50 rounded-xl p-4 mb-6 text-sm space-y-1">
              <div className="flex justify-between"><span className="text-gray-500">القطاع</span><span>{selectedSector?.name_ar}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">الشركة</span><span>{displayName}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">الإيميل</span><span dir="ltr">{companyEmail || '-'}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">النطاق</span><span dir="ltr">{slug}.myodoo.com</span></div>
            </div>

            <div className="flex gap-3">
              <button type="button" onClick={() => setStep(2)}
                className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-50">
                ← السابق
              </button>
              <button type="submit" disabled={loading || !planCode}
                className="flex-1 bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50">
                {loading ? 'جارٍ الإنشاء...' : '🚀 إنشاء الحساب'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
