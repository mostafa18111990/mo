import React from 'react'
import { Link } from 'react-router-dom'

export default function SuspendedPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-yellow-50">
      <div className="text-center p-8">
        <div className="text-6xl mb-4">⚠️</div>
        <h1 className="text-2xl font-bold text-yellow-800 mb-2">Instance Suspended</h1>
        <p className="text-yellow-700 mb-6">
          This Odoo instance has been suspended due to a billing issue.
          Please update your payment method to restore access.
        </p>
        <Link to="/tenants" className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 font-semibold">
          Go to Dashboard
        </Link>
      </div>
    </div>
  )
}
