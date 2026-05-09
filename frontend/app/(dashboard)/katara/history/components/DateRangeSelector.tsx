"use client";

import { useState } from "react";

interface DateRangeSelectorProps {
  startDate: string;
  endDate: string;
  onDateRangeChange: (startDate: string, endDate: string) => void;
  onQuickSelect: (days: number) => void;
  isLoading?: boolean;
}

export default function DateRangeSelector({
  startDate,
  endDate,
  onDateRangeChange,
  onQuickSelect,
  isLoading = false,
}: DateRangeSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newStartDate = e.target.value;
    if (newStartDate <= endDate) {
      onDateRangeChange(newStartDate, endDate);
    }
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEndDate = e.target.value;
    if (newEndDate >= startDate) {
      onDateRangeChange(startDate, newEndDate);
    }
  };

  const handleQuickSelect = (days: number) => {
    onQuickSelect(days);
    setIsOpen(false);
  };

  const formatDateForInput = (dateString: string) => {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
  };

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-gray-700">
        Date Range
      </label>
      
      {/* Quick Select Dropdown */}
      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          disabled={isLoading}
          className="w-full px-3 py-2 text-left border border-gray-300 rounded-md shadow-sm bg-white text-sm focus:outline-none focus:ring-green-500 focus:border-green-500 disabled:opacity-50"
        >
          Quick Select: Last {Math.ceil((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24))} days
          <span className="float-right">▼</span>
        </button>
        
        {isOpen && (
          <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg">
            <div className="py-1">
              <button
                type="button"
                onClick={() => handleQuickSelect(7)}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Last 7 days
              </button>
              <button
                type="button"
                onClick={() => handleQuickSelect(30)}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Last 30 days
              </button>
              <button
                type="button"
                onClick={() => handleQuickSelect(90)}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Last 90 days
              </button>
              <button
                type="button"
                onClick={() => handleQuickSelect(365)}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Last year
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Date Inputs */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Start Date</label>
          <input
            type="date"
            value={formatDateForInput(startDate)}
            onChange={handleStartDateChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 disabled:opacity-50 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">End Date</label>
          <input
            type="date"
            value={formatDateForInput(endDate)}
            onChange={handleEndDateChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 disabled:opacity-50 text-sm"
          />
        </div>
      </div>
    </div>
  );
}
