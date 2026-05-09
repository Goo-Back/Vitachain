"use client";

import React from "react";

interface BulkActionsProps {
  selectedCount: number;
  onAction: (action: string, data: any) => void;
  onClearSelection: () => void;
}

export const BulkActions: React.FC<BulkActionsProps> = ({
  selectedCount,
  onAction,
  onClearSelection
}) => {
  const [action, setAction] = React.useState<string>("");
  const [reason, setReason] = React.useState<string>("");
  const [newRole, setNewRole] = React.useState<string>("");
  const [newStatus, setNewStatus] = React.useState<string>("");

  const handleBulkAction = () => {
    if (!action) return;

    let data: any = {};
    
    if (action === "update_role") {
      data = {
        new_role: newRole,
        reason: reason
      };
    } else if (action === "update_status") {
      data = {
        new_status: newStatus,
        reason: reason
      };
    }

    if (reason && (newRole || newStatus)) {
      onAction(action, data);
      // Reset form
      setAction("");
      setReason("");
      setNewRole("");
      setNewStatus("");
    }
  };

  if (selectedCount === 0) {
    return null;
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-blue-900">
            {selectedCount} user{selectedCount === 1 ? "" : "s"} selected
          </span>
          
          <button
            onClick={onClearSelection}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Clear Selection
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={action}
            onChange={(e) => setAction(e.target.value)}
            className="border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
          >
            <option value="">Choose action...</option>
            <option value="update_role">Update Role</option>
            <option value="update_status">Update Status</option>
          </select>

          {action && (
            <button
              onClick={handleBulkAction}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!reason || (action === "update_role" && !newRole) || (action === "update_status" && !newStatus)}
            >
              Apply
            </button>
          )}
        </div>
      </div>

      {/* Action-specific fields */}
      {action && (
        <div className="mt-4 space-y-4">
          {action === "update_role" && (
            <div>
              <label className="block text-sm font-medium text-blue-900 mb-2">
                New Role
              </label>
              <select
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                className="w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select role...</option>
                <option value="FARMER">Farmer</option>
                <option value="RESTAURANT">Restaurant</option>
                <option value="CITIZEN">Citizen</option>
                <option value="ADMIN">Admin</option>
                <option value="SUPPORT">Support</option>
              </select>
            </div>
          )}

          {action === "update_status" && (
            <div>
              <label className="block text-sm font-medium text-blue-900 mb-2">
                New Status
              </label>
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                className="w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select status...</option>
                <option value="active">Active</option>
                <option value="blocked">Blocked</option>
                <option value="pending">Pending</option>
              </select>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-blue-900 mb-2">
              Reason
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Enter reason for this action..."
              rows={3}
              className="w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              minLength={5}
              required
            />
          </div>
        </div>
      )}
    </div>
  );
};
