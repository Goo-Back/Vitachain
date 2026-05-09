"use client";

import React, { useState } from "react";

interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  account_status: string;
  created_at: string;
  updated_at: string;
  last_login?: string;
  devices_count: number;
  listings_count: number;
  reservations_count: number;
  orders_count: number;
}

interface UserModalProps {
  user: AdminUser;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (updates: any) => Promise<void>;
}

export const UserModal: React.FC<UserModalProps> = ({ user, isOpen, onClose, onUpdate }) => {
  const [activeTab, setActiveTab] = useState<"details" | "role" | "status">("details");
  const [newRole, setNewRole] = useState(user.role);
  const [roleReason, setRoleReason] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleRoleUpdate = async () => {
    if (!roleReason || newRole === user.role) return;
    
    setIsLoading(true);
    try {
      await onUpdate({ role: newRole, role_change_reason: roleReason });
      setRoleReason("");
    } catch (error) {
      console.error("Failed to update role:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:p-0 sm:items-center sm:pt-0">
        <div className="fixed inset-0 transition-opacity" onClick={onClose}>
          <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div className="inline-block align-middle bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">User Details</h3>
              <button
                onClick={onClose}
                className="bg-white rounded-md p-2 inline-flex items-center justify-center text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                <span className="sr-only">Close</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab("details")}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "details"
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  Details
                </button>
                <button
                  onClick={() => setActiveTab("role")}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "role"
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  Role
                </button>
                <button
                  onClick={() => setActiveTab("status")}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "status"
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  Status
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            <div className="mt-6">
              {activeTab === "details" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Email</label>
                    <p className="mt-1 text-sm text-gray-900">{user.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Full Name</label>
                    <p className="mt-1 text-sm text-gray-900">{user.full_name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Phone</label>
                    <p className="mt-1 text-sm text-gray-900">{user.phone || "Not provided"}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Created</label>
                    <p className="mt-1 text-sm text-gray-900">{formatDate(user.created_at)}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Last Login</label>
                    <p className="mt-1 text-sm text-gray-900">{user.last_login ? formatDate(user.last_login) : "Never"}</p>
                  </div>
                </div>
              )}

              {activeTab === "role" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Current Role</label>
                    <p className="mt-1 text-sm text-gray-900">{user.role}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">New Role</label>
                    <select
                      value={newRole}
                      onChange={(e) => setNewRole(e.target.value)}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    >
                      <option value="FARMER">Farmer</option>
                      <option value="RESTAURANT">Restaurant</option>
                      <option value="CITIZEN">Citizen</option>
                      <option value="ADMIN">Admin</option>
                      <option value="SUPPORT">Support</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Reason</label>
                    <textarea
                      value={roleReason}
                      onChange={(e) => setRoleReason(e.target.value)}
                      rows={3}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Enter reason for role change..."
                    />
                  </div>
                  <div className="flex justify-end">
                    <button
                      onClick={handleRoleUpdate}
                      disabled={!roleReason || newRole === user.role}
                      className="bg-blue-600 text-white px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? "Updating..." : "Update Role"}
                    </button>
                  </div>
                </div>
              )}

              {activeTab === "status" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Account Status</label>
                    <p className="mt-1 text-sm text-gray-900">{user.account_status}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Devices</label>
                    <p className="mt-1 text-sm text-gray-900">{user.devices_count}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Listings</label>
                    <p className="mt-1 text-sm text-gray-900">{user.listings_count}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Reservations</label>
                    <p className="mt-1 text-sm text-gray-900">{user.reservations_count}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Orders</label>
                    <p className="mt-1 text-sm text-gray-900">{user.orders_count}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
