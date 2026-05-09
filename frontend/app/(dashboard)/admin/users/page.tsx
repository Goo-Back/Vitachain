"use client";

import React, { useState, useEffect, useCallback } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { UserStats } from "./components/UserStats";
import { UserFilters } from "./components/UserFilters";
import { UsersTable } from "./components/UsersTable";
import { BulkActions } from "./components/BulkActions";
import { UserModal } from "./components/UserModal";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Download, RefreshCw } from "lucide-react";

// Types
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

interface UserStats {
  total_users: number;
  active_users: number;
  blocked_users: number;
  pending_users: number;
  users_by_role: Record<string, number>;
  registrations_today: number;
  registrations_this_week: number;
  registrations_this_month: number;
}

interface Pagination {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

interface Filters {
  search?: string;
  role?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}

const AdminUsersPage: React.FC = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [pagination, setPagination] = useState<Pagination>({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  });
  const [filters, setFilters] = useState<Filters>({});
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const { toast } = useToast();

  // Fetch users with filters
  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        limit: pagination.limit.toString(),
        ...(filters.search && { search: filters.search }),
        ...(filters.role && { role: filters.role }),
        ...(filters.status && { status: filters.status }),
        ...(filters.date_from && { date_from: filters.date_from }),
        ...(filters.date_to && { date_to: filters.date_to })
      });

      const response = await fetch(`/api/admin/users?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('sb-access-token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      setUsers(data.users);
      setStats(data.stats);
      setPagination(data.pagination);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast({
        title: "Error",
        description: "Failed to load users. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.limit, filters]);

  // Handle filter changes
  const handleFiltersChange = useCallback((newFilters: Filters) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  }, []);

  // Handle user selection
  const handleUserSelection = useCallback((userId: string, selected: boolean) => {
    setSelectedUsers(prev => {
      if (selected) {
        return [...prev, userId];
      } else {
        return prev.filter(id => id !== userId);
      }
    });
  }, []);

  // Handle select all users
  const handleSelectAll = useCallback(() => {
    if (selectedUsers.length === users.length) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(users.map(user => user.id));
    }
  }, [selectedUsers.length, users]);

  // Handle user details view
  const handleUserDetails = useCallback((user: AdminUser) => {
    setSelectedUser(user);
    setShowUserModal(true);
  }, []);

  // Handle bulk actions
  const handleBulkAction = useCallback(async (action: string, data: any) => {
    if (selectedUsers.length === 0) {
      toast({
        title: "Warning",
        description: "Please select users first",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/admin/users/bulk-update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('sb-access-token')}`
        },
        body: JSON.stringify({
          user_ids: selectedUsers,
          action,
          data
        })
      });

      if (!response.ok) {
        throw new Error('Failed to perform bulk action');
      }

      const result = await response.json();
      toast({
        title: "Success",
        description: `${action} completed successfully. Updated: ${result.updated_count}, Failed: ${result.failed_count}`,
        variant: "default"
      });

      setSelectedUsers([]);
      await fetchUsers(); // Refresh data
    } catch (error) {
      console.error('Error performing bulk action:', error);
      toast({
        title: "Error",
        description: `Failed to ${action}. Please try again.`,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  }, [selectedUsers, fetchUsers]);

  // Handle export
  const handleExport = useCallback(async (format: string = 'csv') => {
    try {
      const params = new URLSearchParams({
        format,
        ...(filters.role && { role: filters.role }),
        ...(filters.status && { status: filters.status }),
        ...(filters.date_from && { date_from: filters.date_from }),
        ...(filters.date_to && { date_to: filters.date_to })
      });

      const response = await fetch(`/api/admin/users/export?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('sb-access-token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to export users');
      }

      const data = await response.json();
      
      // Create and download file
      const blob = new Blob([data.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `users_export_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: "Success",
        description: "User data exported successfully",
        variant: "default"
      });
    } catch (error) {
      console.error('Error exporting users:', error);
      toast({
        title: "Error",
        description: "Failed to export users. Please try again.",
        variant: "destructive"
      });
    }
  }, [filters]);

  // Handle refresh
  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchUsers();
    setRefreshing(false);
  }, [fetchUsers]);

  // Initial load
  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <ProtectedRoute allowedRoles={['ADMIN']}>
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
            <p className="text-gray-600 mt-1">Manage platform users and their accounts</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              onClick={() => handleExport('csv')}
              className="flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Export CSV</span>
            </Button>
            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </Button>
          </div>
        </div>

        {/* User Statistics */}
        {stats && <UserStats stats={stats} />}

        {/* Filters */}
        <UserFilters 
          filters={filters} 
          onFiltersChange={handleFiltersChange}
          onReset={() => {
            setFilters({});
            setPagination(prev => ({ ...prev, page: 1 }));
          }}
        />

        {/* Bulk Actions */}
        {selectedUsers.length > 0 && (
          <BulkActions 
            selectedCount={selectedUsers.length}
            onAction={handleBulkAction}
            onClearSelection={() => setSelectedUsers([])}
          />
        )}

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <UsersTable
            users={users}
            loading={loading}
            selectedUsers={selectedUsers}
            onUserSelection={handleUserSelection}
            onSelectAll={handleSelectAll}
            onUserDetails={handleUserDetails}
            pagination={pagination}
            onPageChange={(page) => setPagination(prev => ({ ...prev, page }))}
            onLimitChange={(limit) => setPagination(prev => ({ ...prev, limit, page: 1 }))}
          />
        </div>

        {/* User Details Modal */}
        {showUserModal && selectedUser && (
          <UserModal
            user={selectedUser}
            isOpen={showUserModal}
            onClose={() => {
              setShowUserModal(false);
              setSelectedUser(null);
            }}
            onUpdate={async (updates) => {
              try {
                const response = await fetch(`/api/admin/users/${selectedUser.id}`, {
                  method: 'PATCH',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('sb-access-token')}`
                  },
                  body: JSON.stringify(updates)
                });

                if (!response.ok) {
                  throw new Error('Failed to update user');
                }

                toast({
                  title: "Success",
                  description: "User updated successfully",
                  variant: "default"
                });

                setShowUserModal(false);
                setSelectedUser(null);
                await fetchUsers();
              } catch (error) {
                console.error('Error updating user:', error);
                toast({
                  title: "Error",
                  description: "Failed to update user. Please try again.",
                  variant: "destructive"
                });
              }
            }}
          />
        )}
      </div>
    </ProtectedRoute>
  );
};

export default AdminUsersPage;
