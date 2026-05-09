"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

interface LogoutButtonProps {
  className?: string
  variant?: 'default' | 'mobile' | 'navbar'
  showText?: boolean
  onLogoutComplete?: () => void
}

export default function LogoutButton({ 
  className = '', 
  variant = 'default',
  showText = true,
  onLogoutComplete 
}: LogoutButtonProps) {
  const router = useRouter()
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const supabase = createClientComponentClient()

  const handleLogout = async () => {
    if (variant === 'navbar' && !showConfirm) {
      // Quick logout from navbar - no confirmation
      await performLogout(false)
    } else {
      // Show confirmation dialog
      setShowConfirm(true)
    }
  }

  const performLogout = async (logoutAll: boolean = false) => {
    setIsLoggingOut(true)

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
          
          // Clear client-side session
          await supabase.auth.signOut()
          
          // Call completion callback
          onLogoutComplete?.()
          
          // Redirect to login
          router.push('/auth/login')
        } else {
          const error = await response.json()
          console.error('Logout failed:', error)
          // Show error message (could use toast here)
          alert(error.error?.message || 'Logout failed')
        }
      } else {
        console.error('No active session found')
        router.push('/auth/login')
      }
    } catch (error) {
      console.error('Logout error:', error)
      alert('An unexpected error occurred during logout')
    } finally {
      setIsLoggingOut(false)
      setShowConfirm(false)
    }
  }

  const getButtonStyles = () => {
    const baseStyles = "inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50"
    
    switch (variant) {
      case 'mobile':
        return `${baseStyles} text-white bg-red-600 hover:bg-red-700 focus:ring-red-500`
      case 'navbar':
        return `${baseStyles} text-gray-700 hover:text-gray-900 hover:bg-gray-50 focus:ring-indigo-500`
      default:
      return `${baseStyles} text-white bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500`
    }
  }

  if (showConfirm) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full z-50">
        <div className="flex min-h-full items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Confirm Logout
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Choose logout option:
                </label>
                <div className="space-y-3">
                  <button
                    onClick={() => performLogout(false)}
                    disabled={isLoggingOut}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                  >
                    {isLoggingOut ? 'Signing out...' : 'Sign out from this device'}
                  </button>
                  
                  <button
                    onClick={() => performLogout(true)}
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

              <div className="flex items-center justify-between space-x-3">
                <button
                  onClick={() => setShowConfirm(false)}
                  disabled={isLoggingOut}
                  className="flex-1 flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gray-600 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
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

  return (
    <button
      onClick={handleLogout}
      disabled={isLoggingOut}
      className={`${getButtonStyles()} ${className}`}
    >
      {isLoggingOut ? (
        <>
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a8 8 0 01-8 8v4a8 8 0 018-8z"></path>
          </svg>
          Processing...
        </>
      ) : (
        <>
          {showText && (
            <>
              <svg className="-ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4 4m0 0l4 4m4-4H3m6 0l-4 4m0 0l4 4" />
              </svg>
              Sign Out
            </>
          )}
        </>
      )}
    </button>
  )
}
