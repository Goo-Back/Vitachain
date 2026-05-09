"use client";

import { DeviceChartData } from "../hooks/useTelemetryHistory";

interface DeviceSelectorProps {
  selectedDeviceId: string | null;
  onDeviceSelect: (deviceId: string | null) => void;
  devices: DeviceChartData[];
  isLoading?: boolean;
}

export default function DeviceSelector({
  selectedDeviceId,
  onDeviceSelect,
  devices,
  isLoading = false,
}: DeviceSelectorProps) {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onDeviceSelect(value === "all" ? null : value);
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Device Filter
      </label>
      
      <select
        value={selectedDeviceId || "all"}
        onChange={handleChange}
        disabled={isLoading}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 disabled:opacity-50 text-sm"
      >
        <option value="all">All Devices</option>
        {devices.map((device) => (
          <option key={device.device_id} value={device.device_id}>
            {device.device_name || device.device_id}
          </option>
        ))}
      </select>

      {devices.length === 0 && !isLoading && (
        <p className="text-xs text-gray-500">No devices available</p>
      )}
    </div>
  );
}
