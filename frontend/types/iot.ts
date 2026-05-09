// IoT device and telemetry TypeScript interfaces

export enum DeviceType {
  ESP32 = "esp32",
  SENSOR = "sensor",
  GATEWAY = "gateway"
}

export enum DeviceStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  MAINTENANCE = "maintenance",
  ERROR = "error"
}

export interface Device {
  id: string;
  user_id: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  location_lat?: number;
  location_lng?: number;
  firmware_version?: string;
  last_seen?: string;
  api_key: string;
  configuration: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Sensor {
  id: string;
  device_id: string;
  type: string; // temperature, humidity, soil_moisture, etc.
  unit?: string; // celsius, fahrenheit, percentage, etc.
  calibration_offset: number;
  min_value?: number;
  max_value?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TelemetryData {
  id: string;
  device_id: string;
  sensor_id?: string;
  timestamp: string;
  sensor_type: string;
  value: number;
  unit?: string;
  quality_score: number; // Data quality score 0-1
  metadata: Record<string, any>;
  created_at: string;
}

export interface DeviceCreateRequest {
  name: string;
  type: DeviceType;
  location_lat?: number;
  location_lng?: number;
  configuration?: Record<string, any>;
}

export interface DeviceUpdateRequest {
  name?: string;
  status?: DeviceStatus;
  location_lat?: number;
  location_lng?: number;
  firmware_version?: string;
  configuration?: Record<string, any>;
}

export interface DeviceResponse {
  message: string;
  device: Device;
}

export interface DeviceListResponse {
  devices: Device[];
  total: number;
  page: number;
  limit: number;
}

export interface SensorCreateRequest {
  device_id: string;
  type: string;
  unit?: string;
  calibration_offset?: number;
  min_value?: number;
  max_value?: number;
}

export interface SensorUpdateRequest {
  type?: string;
  unit?: string;
  calibration_offset?: number;
  min_value?: number;
  max_value?: number;
  is_active?: boolean;
}

export interface TelemetryQuery {
  device_id?: string;
  sensor_id?: string;
  sensor_type?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}

export interface TelemetryResponse {
  telemetry: TelemetryData[];
  total: number;
  query: TelemetryQuery;
}

export interface DeviceStats {
  total_devices: number;
  active_devices: number;
  inactive_devices: number;
  devices_by_type: Record<DeviceType, number>;
  last_data_received?: string;
  total_telemetry_points: number;
}

export interface DeviceCommand {
  id: string;
  device_id: string;
  command: string;
  parameters: Record<string, any>;
  status: 'pending' | 'sent' | 'executed' | 'failed';
  sent_at?: string;
  executed_at?: string;
  error_message?: string;
  created_at: string;
}

export interface DeviceCommandRequest {
  device_id: string;
  command: string;
  parameters: Record<string, any>;
}

export interface DeviceCommandResponse {
  message: string;
  command: DeviceCommand;
}
