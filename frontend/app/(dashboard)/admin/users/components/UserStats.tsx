"use client";

import React from "react";

interface UserStatsProps {
  stats: {
    total_users: number;
    active_users: number;
    blocked_users: number;
    pending_users: number;
    users_by_role: Record<string, number>;
    registrations_today: number;
    registrations_this_week: number;
    registrations_this_month: number;
  };
}

export const UserStats: React.FC<UserStatsProps> = ({ stats }) => {
  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      'FARMER': 'bg-green-100 text-green-800',
      'RESTAURANT': 'bg-blue-100 text-blue-800',
      'CITIZEN': 'bg-purple-100 text-purple-800',
      'ADMIN': 'bg-red-100 text-red-800',
      'SUPPORT': 'bg-yellow-100 text-yellow-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {/* Total Users */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">Total Users</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total_users.toLocaleString()}</p>
          </div>
          <div className="p-3 bg-blue-100 rounded-full">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 016-6V7a6 6 0 016-6h2a6 6 0 016 6v8a6 6 0 01-6 6h6a6 6 0 006-6V7a6 6 0 00-6-6h-2" />
            </svg>
          </div>
        </div>
      </div>

      {/* Active Users */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">Active Users</p>
            <p className="text-2xl font-bold text-green-600">{stats.active_users.toLocaleString()}</p>
          </div>
          <div className="p-3 bg-green-100 rounded-full">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a10 10 0 110-20 0v4a10 10 0 0020 0v-4" />
            </svg>
          </div>
        </div>
      </div>

      {/* Blocked Users */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">Blocked Users</p>
            <p className="text-2xl font-bold text-red-600">{stats.blocked_users.toLocaleString()}</p>
          </div>
          <div className="p-3 bg-red-100 rounded-full">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 0018.364 5.636m-9 9 0 00-12.728 0m12.728 12.728L5.636 18.364m9-9V5.636m0 12.728" />
            </svg>
          </div>
        </div>
      </div>

      {/* Pending Users */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">Pending Users</p>
            <p className="text-2xl font-bold text-yellow-600">{stats.pending_users.toLocaleString()}</p>
          </div>
          <div className="p-3 bg-yellow-100 rounded-full">
            <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 110-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Users by Role */}
      <div className="bg-white rounded-lg shadow p-6 md:col-span-2 lg:col-span-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Users by Role</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {Object.entries(stats.users_by_role).map(([role, count]) => (
            <div key={role} className="text-center">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full text-sm font-medium ${getRoleColor(role)}`}>
                {count}
              </div>
              <p className="text-xs text-gray-600 mt-1">{role}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Registration Stats */}
      <div className="bg-white rounded-lg shadow p-6 md:col-span-2 lg:col-span-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Registration Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{stats.registrations_today}</p>
            <p className="text-sm text-gray-600">Today</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{stats.registrations_this_week}</p>
            <p className="text-sm text-gray-600">This Week</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600">{stats.registrations_this_month}</p>
            <p className="text-sm text-gray-600">This Month</p>
          </div>
        </div>
      </div>
    </div>
  );
};
