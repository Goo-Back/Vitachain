/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { jest } from '@jest/globals';
import AlertItem from '../../../app/(dashboard)/katara/components/AlertItem';

// Mock fetch
global.fetch = jest.fn();

// Mock alert data
const mockAlert = {
  id: 'test-alert-id',
  farmer_id: 'test-farmer-id',
  device_id: 'katara-test-device',
  type: 'threshold_exceeded',
  severity: 'high',
  message: 'Temperature threshold exceeded',
  read_status: false,
  created_at: '2026-05-03T23:48:00Z',
  metric: 'temperature',
  value: 45.5,
  threshold: 40.0
};

const mockReadAlert = {
  ...mockAlert,
  read_status: true,
  read_at: '2026-05-03T23:50:00Z'
};

describe('AlertItem Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders unread alert correctly', () => {
    render(<AlertItem alert={mockAlert} />);
    
    // Check alert message is displayed
    expect(screen.getByText('Temperature threshold exceeded')).toBeInTheDocument();
    
    // Check severity badge
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    
    // Check device badge
    expect(screen.getByText('katara-test-device')).toBeInTheDocument();
    
    // Check metric details
    expect(screen.getByText('Value: 45.5')).toBeInTheDocument();
    expect(screen.getByText('Threshold: 40.0')).toBeInTheDocument();
    
    // Check mark as read button is present for unread alerts
    expect(screen.getByRole('button', { name: /mark as read/i })).toBeInTheDocument();
    
    // Check unread styling (orange border)
    const card = screen.getByRole('article');
    expect(card).toHaveClass('border-l-4', 'border-l-orange-500');
  });

  test('renders read alert correctly', () => {
    render(<AlertItem alert={mockReadAlert} />);
    
    // Check alert message is displayed
    expect(screen.getByText('Temperature threshold exceeded')).toBeInTheDocument();
    
    // Check mark as read button is NOT present for read alerts
    expect(screen.queryByRole('button', { name: /mark as read/i })).not.toBeInTheDocument();
    
    // Check no unread styling
    const card = screen.getByRole('article');
    expect(card).not.toHaveClass('border-l-4', 'border-l-orange-500');
  });

  test('marks alert as read successfully', async () => {
    const mockFetch = fetch as jest.MockedFunction<typeof global.fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 'test-alert-id', read_status: true, updated_at: '2026-05-03T23:50:00Z' })
    });

    const onMarkAsRead = jest.fn();
    render(<AlertItem alert={mockAlert} onMarkAsRead={onMarkAsRead} />);
    
    // Click mark as read button
    const markReadButton = screen.getByRole('button', { name: /mark as read/i });
    fireEvent.click(markReadButton);
    
    // Check loading state
    await waitFor(() => {
      expect(markReadButton).toBeDisabled();
    });
    
    // Wait for API call to complete
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/katara/alerts/test-alert-id/read',
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' }
        }
      );
    });
    
    // Check callback was called
    expect(onMarkAsRead).toHaveBeenCalledWith('test-alert-id');
  });

  test('handles API error gracefully', async () => {
    const mockFetch = fetch as jest.MockedFunction<typeof global.fetch>;
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(<AlertItem alert={mockAlert} />);
    
    // Click mark as read button
    const markReadButton = screen.getByRole('button', { name: /mark as read/i });
    fireEvent.click(markReadButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/error: network error/i)).toBeInTheDocument();
    });
    
    // Check button is no longer disabled
    expect(markReadButton).not.toBeDisabled();
  });

  test('displays correct timestamp formatting', () => {
    const recentAlert = {
      ...mockAlert,
      created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString() // 5 minutes ago
    };
    
    render(<AlertItem alert={recentAlert} />);
    
    expect(screen.getByText('5 minutes ago')).toBeInTheDocument();
  });

  test('displays correct metric icons', () => {
    const { rerender } = render(<AlertItem alert={mockAlert} />);
    
    // Temperature icon
    expect(screen.getByTestId('thermometer-icon')).toBeInTheDocument();
    
    // Humidity icon
    const humidityAlert = { ...mockAlert, metric: 'humidity' };
    rerender(<AlertItem alert={humidityAlert} />);
    expect(screen.getByTestId('droplets-icon')).toBeInTheDocument();
    
    // NDVI icon
    const ndviAlert = { ...mockAlert, metric: 'ndvi' };
    rerender(<AlertItem alert={ndviAlert} />);
    expect(screen.getByTestId('leaf-icon')).toBeInTheDocument();
  });

  test('applies custom className', () => {
    const customClass = 'custom-test-class';
    render(<AlertItem alert={mockAlert} className={customClass} />);
    
    const card = screen.getByRole('article');
    expect(card).toHaveClass(customClass);
  });
});
