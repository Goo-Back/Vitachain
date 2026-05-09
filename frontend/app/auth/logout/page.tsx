"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

export default function LogoutPage() {
  const router = useRouter()
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [message, setMessage] = useState('')
  const supabase = createClientComponentClient()

  const handleLogout = async (logoutAll: boolean = false) => {
    setIsLoggingOut(true)
    setMessage('')

    try {
      // Get current session
      const { data: { session } } = await supabase.auth.getSession()
      
      if (session) {
        // Call logout API
        const response = await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`
          },
          body: JSON.stringify({
            logout_all: logoutAll,
            session_id: session.user?.app_metadata?.session_id
          })
        })

        if (response.ok) {
          const result = await response.json()
          setMessage(result.message)
          
          // Clear client-side session
          await supabase.auth.signOut()
          
          // Redirect to login after short delay
          setTimeout(() => {
            router.push('/auth/login')
          }, 1500)
        } else {
          const error = await response.json()
          setMessage(error.error?.message || 'Logout failed')
        }
      } else {
        setMessage('No active session found')
      }
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
