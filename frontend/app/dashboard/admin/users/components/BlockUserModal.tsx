"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { X, Shield, AlertTriangle } from "lucide-react";

interface BlockUserModalProps {
  user: {
    id: string;
    email: string;
    full_name: string;
    role: string;
    account_status: string;
  };
  isOpen: boolean;
  onClose: () => void;
  onBlockComplete: () => void;
}

interface BlockRequest {
  block_reason: string;
  duration_hours: number;
  auto_block: boolean;
}

const BlockUserModal: React.FC<BlockUserModalProps> = ({
  user,
  isOpen,
  onClose,
  onBlockComplete
}) => {
  const [blockRequest, setBlockRequest] = useState<BlockRequest>({
    block_reason: "",
    duration_hours: 24,
    auto_block: false
  });
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const predefinedReasons = [
    "Suspicious activity detected",
    "Violation of terms of service",
    "Spam or inappropriate behavior",
    "Security concerns",
    "Account compromise suspected",
    "Multiple policy violations"
  ];

  const durationOptions = [
    { label: "1 Hour", value: 1 },
    { label: "6 Hours", value: 6 },
    { label: "12 Hours", value: 12 },
    { label: "24 Hours", value: 24 },
    { label: "3 Days", value: 72 },
    { label: "1 Week", value: 168 },
    { label: "2 Weeks", value: 336 },
    { label: "1 Month", value: 720 }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!blockRequest.block_reason.trim()) {
      toast({
        title: "Error",
        description: "Please provide a reason for blocking this user",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/admin/users/${user.id}/block`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('sb-access-token')}`
        },
        body: JSON.stringify(blockRequest)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.message || 'Failed to block user');
      }

      const result = await response.json();
      
      toast({
        title: "Success",
        description: `User ${user.full_name} has been blocked successfully`,
        variant: "default"
      });

      onBlockComplete();
      onClose();
    } catch (error) {
      console.error('Error blocking user:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to block user. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setBlockRequest({
        block_reason: "",
        duration_hours: 24,
        auto_block: false
      });
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-red-100 rounded-full">
              <Shield className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Block User Account</h2>
              <p className="text-sm text-gray-500">Temporarily restrict user access to the platform</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* User Info */}
        <div className="p-6 border-b border-gray-200">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-yellow-800">User to be Blocked</h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p><strong>Name:</strong> {user.full_name}</p>
                  <p><strong>Email:</strong> {user.email}</p>
                  <p><strong>Role:</strong> {user.role}</p>
                  <p><strong>Current Status:</strong> 
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                      user.account_status === 'active' 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user.account_status}
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Block Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Block Reason */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Block Reason <span className="text-red-500">*</span>
            </label>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                {predefinedReasons.map((reason) => (
                  <button
                    key={reason}
                    type="button"
                    onClick={() => setBlockRequest(prev => ({ ...prev, block_reason: reason }))}
                    className={`text-left px-3 py-2 rounded-lg border text-sm transition-colors ${
                      blockRequest.block_reason === reason
                        ? 'border-red-500 bg-red-50 text-red-700'
                        : 'border-gray-300 hover:border-gray-400 text-gray-700'
                    }`}
                  >
                    {reason}
                  </button>
                ))}
              </div>
              <textarea
                value={blockRequest.block_reason}
                onChange={(e) => setBlockRequest(prev => ({ ...prev, block_reason: e.target.value }))}
                placeholder="Or enter a custom reason..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                required
              />
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Block Duration <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-4 gap-2">
              {durationOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setBlockRequest(prev => ({ ...prev, duration_hours: option.value }))}
                  className={`px-3 py-2 rounded-lg border text-sm transition-colors ${
                    blockRequest.duration_hours === option.value
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'border-gray-300 hover:border-gray-400 text-gray-700'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
            <input
              type="number"
              min="1"
              max="8760"
              value={blockRequest.duration_hours}
              onChange={(e) => setBlockRequest(prev => ({ ...prev, duration_hours: parseInt(e.target.value) || 1 }))}
              className="mt-2 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              placeholder="Custom duration in hours (max 8760 = 1 year)"
            />
          </div>

          {/* Auto Block Option */}
          <div>
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={blockRequest.auto_block}
                onChange={(e) => setBlockRequest(prev => ({ ...prev, auto_block: e.target.checked }))}
                className="h-4 w-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
              />
              <div>
                <span className="text-sm font-medium text-gray-700">Automatic Security Block</span>
                <p className="text-xs text-gray-500">This block was triggered automatically by security systems</p>
              </div>
            </label>
          </div>

          {/* Warning Message */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-red-800">Important Notice</h4>
                <ul className="mt-2 text-sm text-red-700 space-y-1">
                  <li>• The user will be immediately blocked from all platform access</li>
                  <li>• They will receive an email notification about this block</li>
                  <li>• The block will automatically expire after the specified duration</li>
                  <li>• All blocking actions are logged for audit purposes</li>
                  <li>• You can unblock the user at any time if needed</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || !blockRequest.block_reason.trim()}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {loading ? 'Blocking...' : 'Block User'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BlockUserModal;
