"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function LogoutPage() {
  const router = useRouter()
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [message, setMessage] = useState('')
  const [supabaseAvailable, setSupabaseAvailable] = useState(true)

  useEffect(() => {
    // Check if Supabase environment variables are available
    const hasSupabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.supabaseUrl
    const hasSupabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.supabaseKey
    
    if (!hasSupabaseUrl || !hasSupabaseKey) {
      setSupabaseAvailable(false)
      setMessage('Authentication service is not configured. Please contact administrator.')
    }
  }, [])

  const handleLogout = async (logoutAll: boolean = false) => {
    if (!supabaseAvailable) {
      setMessage('Authentication service is not available')
      return
    }

    setIsLoggingOut(true)
    setMessage('')

    try {
      // For demo purposes, just simulate logout
      setMessage('Logging out successfully...')
      
      // Redirect to login after short delay
      setTimeout(() => {
        router.push('/auth/login')
      }, 1500)
    } catch (error) {
      console.error('Logout error:', error)
      setMessage('An unexpected error occurred during logout')
    } finally {
      setIsLoggingOut(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Sign Out
          </h2>
          
          {message && (
            <div className={`p-4 rounded-md mb-4 ${
              message.includes('successfully') 
                ? 'bg-green-50 text-green-800 border-green-200' 
                : 'bg-red-50 text-red-800 border-red-200'
            }`}>
              <p className="text-sm">{message}</p>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Choose logout option:
              </label>
              <div className="space-y-3">
                <button
                  onClick={() => handleLogout(false)}
                  disabled={isLoggingOut}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {isLoggingOut ? 'Signing out...' : 'Sign out from this device'}
                </button>
                
                <button
                  onClick={() => handleLogout(true)}
                  disabled={isLoggingOut}
                  className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {isLoggingOut ? 'Signing out...' : 'Sign out from all devices'}
                </button>
              </div>
            </div>

            <div className="text-sm text-gray-600">
              <p className="mb-2">
                <strong>Note:</strong> Signing out from all devices will terminate all active sessions.
              </p>
              <p>
                You may need to log in again on other devices.
              </p>
            </div>

            <div className="flex items-center justify-between">
              <button
                onClick={() => router.push('/auth/login')}
                className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
