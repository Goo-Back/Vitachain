"""
Tests for KATARA history API endpoints
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.models.schemas import (
    HistoryParams, HistoryResponse, PeriodInfo, DeviceChartData,
    HourlyData, DailyStats, TrendAnalysis, AlertPattern
)


class TestHistoryAPI:
    """Test suite for history API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_farmer_user(self):
        """Mock authenticated farmer user"""
        return {
            "user_id": str(uuid.uuid4()),
            "email": "farmer@test.com",
            "role": "FARMER",
            "user_metadata": {"role": "FARMER"}
        }
    
    @pytest.fixture
    def sample_history_params(self):
        """Sample history parameters"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        return {
            "start_date": start_date.isoformat() + "Z",
            "end_date": end_date.isoformat() + "Z",
            "aggregation": "hour"
        }
    
    @pytest.fixture
    def sample_history_response(self):
        """Sample history response data"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        return HistoryResponse(
            period_info=PeriodInfo(
                start_date=start_date,
                end_date=end_date,
                total_readings=168,
                devices_analyzed=2
            ),
            chart_data=[
                DeviceChartData(
                    device_id="katara-device-1",
                    device_name="Parcelle Nord",
                    hourly_data=[
                        HourlyData(
                            hour_bucket=start_date + timedelta(hours=1),
                            avg_temp=25.5,
                            min_temp=24.0,
                            max_temp=27.0,
                            avg_humidity=60.0,
                            avg_ndvi=0.65,
                            reading_count=12
                        )
                    ]
                )
            ],
            daily_stats=[
                DailyStats(
                    date=start_date.date().isoformat(),
                    avg_temp=25.5,
                    min_temp=24.0,
                    max_temp=27.0,
                    avg_humidity=60.0,
                    avg_ndvi=0.65,
                    total_readings=24
                )
            ],
            trend_analysis=TrendAnalysis(
                temperature_trend="stable",
                humidity_trend="increasing",
                ndvi_trend="decreasing",
                correlations={
                    "temp_humidity": -0.65,
                    "temp_ndvi": -0.23
                }
            ),
            alert_patterns=[
                AlertPattern(
                    date=start_date.date().isoformat(),
                    high_alerts=1,
                    medium_alerts=2,
                    low_alerts=1,
                    main_causes=["temperature_threshold", "humidity_threshold"]
                )
            ]
        )

    @patch('app.api.routes.katara.HistoryService')
    @patch('app.api.dependencies.require_farmer')
    def test_get_history_success(self, mock_auth, mock_history_service, client, mock_farmer_user, sample_history_params, sample_history_response):
        """Test successful history data retrieval"""
        # Setup mocks
        mock_auth.return_value = mock_farmer_user
        
        mock_service_instance = AsyncMock()
        mock_service_instance.get_historical_telemetry.return_value = sample_history_response
        mock_history_service.return_value = mock_service_instance
        
        # Make request
        response = client.get("/api/katara/history", params=sample_history_params)
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "period_info" in data
        assert "chart_data" in data
        assert "daily_stats" in data
        assert "trend_analysis" in data
        assert "alert_patterns" in data
        
        # Verify service was called correctly
        mock_service_instance.get_historical_telemetry.assert_called_once()

    @patch('app.api.dependencies.require_farmer')
    def test_get_history_invalid_date_format(self, mock_auth, client, mock_farmer_user):
        """Test history API with invalid date format"""
        # Setup mock
        mock_auth.return_value = mock_farmer_user
        
        # Make request with invalid date
        response = client.get("/api/katara/history", params={
            "start_date": "invalid-date",
            "end_date": "2026-05-01T00:00:00Z",
            "aggregation": "hour"
        })
        
        # Assertions
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_data = response.json()
        assert "error" in error_data
        assert error_data["error"]["code"] == "VALIDATION_ERROR"

    @patch('app.api.dependencies.require_farmer')
    def test_get_history_invalid_aggregation(self, mock_auth, client, mock_farmer_user):
        """Test history API with invalid aggregation level"""
        # Setup mock
        mock_auth.return_value = mock_farmer_user
        
        # Make request with invalid aggregation
        response = client.get("/api/katara/history", params={
            "start_date": "2026-04-01T00:00:00Z",
            "end_date": "2026-05-01T00:00:00Z",
            "aggregation": "invalid"
        })
        
        # Assertions
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_data = response.json()
        assert "error" in error_data

    @patch('app.api.dependencies.require_farmer')
    def test_get_history_end_date_before_start_date(self, mock_auth, client, mock_farmer_user):
        """Test history API with end date before start date"""
        # Setup mock
        mock_auth.return_value = mock_farmer_user
        
        # Make request with invalid date range
        response = client.get("/api/katara/history", params={
            "start_date": "2026-05-01T00:00:00Z",
            "end_date": "2026-04-01T00:00:00Z",
            "aggregation": "hour"
        })
        
        # Assertions
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('app.api.dependencies.require_farmer')
    def test_get_history_date_range_too_long(self, mock_auth, client, mock_farmer_user):
        """Test history API with date range exceeding maximum"""
        # Setup mock
        mock_auth.return_value = mock_farmer_user
        
        # Make request with date range > 365 days
        response = client.get("/api/katara/history", params={
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2026-05-01T00:00:00Z",
            "aggregation": "hour"
        })
        
        # Assertions
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('app.api.routes.katara.HistoryService')
    @patch('app.api.dependencies.require_farmer')
    def test_get_history_no_data_found(self, mock_auth, mock_history_service, client, mock_farmer_user, sample_history_params):
        """Test history API when no data is found"""
        # Setup mocks
        mock_auth.return_value = mock_farmer_user
        
        mock_service_instance = AsyncMock()
        mock_service_instance.get_historical_telemetry.side_effect = ValueError("No historical data found")
        mock_history_service.return_value = mock_service_instance
        
        # Make request
        response = client.get("/api/katara/history", params=sample_history_params)
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert error_data["error"]["code"] == "HISTORY_NOT_FOUND"

    @patch('app.api.routes.katara.HistoryService')
    @patch('app.api.dependencies.require_farmer')
    def test_get_history_with_device_filter(self, mock_auth, mock_history_service, client, mock_farmer_user, sample_history_response):
        """Test history API with specific device filter"""
        # Setup mocks
        mock_auth.return_value = mock_farmer_user
        
        mock_service_instance = AsyncMock()
        mock_service_instance.get_historical_telemetry.return_value = sample_history_response
        mock_history_service.return_value = mock_service_instance
        
        # Make request with device filter
        response = client.get("/api/katara/history", params={
            "start_date": "2026-04-01T00:00:00Z",
            "end_date": "2026-05-01T00:00:00Z",
            "device_id": "katara-device-1",
            "aggregation": "hour"
        })
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        
        # Verify service was called with device filter
        call_args = mock_service_instance.get_historical_telemetry.call_args
        assert call_args is not None

    @patch('app.api.routes.katara.HistoryService')
    @patch('app.api.dependencies.require_farmer')
    def test_get_history_daily_aggregation(self, mock_auth, mock_history_service, client, mock_farmer_user, sample_history_response):
        """Test history API with daily aggregation"""
        # Setup mocks
        mock_auth.return_value = mock_farmer_user
        
        mock_service_instance = AsyncMock()
        mock_service_instance.get_historical_telemetry.return_value = sample_history_response
        mock_history_service.return_value = mock_service_instance
        
        # Make request with daily aggregation
        response = client.get("/api/katara/history", params={
            "start_date": "2026-04-01T00:00:00Z",
            "end_date": "2026-05-01T00:00:00Z",
            "aggregation": "day"
        })
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK

    @patch('app.api.dependencies.require_farmer')
    def test_get_history_unauthorized(self, client):
        """Test history API without authentication"""
        # Make request without auth header
        response = client.get("/api/katara/history", params={
            "start_date": "2026-04-01T00:00:00Z",
            "end_date": "2026-05-01T00:00:00Z",
            "aggregation": "hour"
        })
        
        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.routes.katara.HistoryService')
    @patch('app.api.dependencies.require_farmer')
    def test_get_history_server_error(self, mock_auth, mock_history_service, client, mock_farmer_user, sample_history_params):
        """Test history API with server error"""
        # Setup mocks
        mock_auth.return_value = mock_farmer_user
        
        mock_service_instance = AsyncMock()
        mock_service_instance.get_historical_telemetry.side_effect = Exception("Database error")
        mock_history_service.return_value = mock_service_instance
        
        # Make request
        response = client.get("/api/katara/history", params=sample_history_params)
        
        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        error_data = response.json()
        assert error_data["error"]["code"] == "INTERNAL_ERROR"


class TestHistoryService:
    """Test suite for HistoryService"""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        supabase_mock = MagicMock()
        supabase_mock.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value = MagicMock()
        return supabase_mock

    @pytest.fixture
    def sample_farmer_id(self):
        """Sample farmer ID"""
        return uuid.uuid4()

    @pytest.fixture
    def sample_params(self):
        """Sample history parameters"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        return HistoryParams(
            start_date=start_date,
            end_date=end_date,
            device_id=None,
            aggregation="hour"
        )

    def test_calculate_trend_increasing(self):
        """Test trend calculation for increasing data"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        data = [1.0, 2.0, 3.0, 4.0, 5.0]  # Clearly increasing
        
        trend = analytics.calculate_trend(data)
        assert trend == "increasing"

    def test_calculate_trend_decreasing(self):
        """Test trend calculation for decreasing data"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        data = [5.0, 4.0, 3.0, 2.0, 1.0]  # Clearly decreasing
        
        trend = analytics.calculate_trend(data)
        assert trend == "decreasing"

    def test_calculate_trend_stable(self):
        """Test trend calculation for stable data"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        data = [3.0, 3.1, 2.9, 3.2, 2.8]  # Relatively stable
        
        trend = analytics.calculate_trend(data)
        assert trend == "stable"

    def test_calculate_trend_insufficient_data(self):
        """Test trend calculation with insufficient data"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        data = [1.0]  # Only one data point
        
        trend = analytics.calculate_trend(data)
        assert trend == "insufficient_data"

    def test_calculate_correlation_positive(self):
        """Test correlation calculation for positively correlated data"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]  # Perfect positive correlation
        
        correlation = analytics.calculate_correlation(x, y)
        assert abs(correlation - 1.0) < 0.01  # Allow for floating point precision

    def test_calculate_correlation_negative(self):
        """Test correlation calculation for negatively correlated data"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [10.0, 8.0, 6.0, 4.0, 2.0]  # Perfect negative correlation
        
        correlation = analytics.calculate_correlation(x, y)
        assert abs(correlation + 1.0) < 0.01  # Allow for floating point precision

    def test_calculate_correlation_no_correlation(self):
        """Test correlation calculation for uncorrelated data"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [1.0, 5.0, 2.0, 8.0, 3.0]  # Random data
        
        correlation = analytics.calculate_correlation(x, y)
        assert abs(correlation) < 0.5  # Should be low correlation

    def test_calculate_correlation_insufficient_data(self):
        """Test correlation calculation with insufficient data"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        x = [1.0, 2.0]  # Only 2 data points
        y = [3.0, 4.0]
        
        correlation = analytics.calculate_correlation(x, y)
        assert correlation == 0.0

    def test_detect_anomalies(self):
        """Test anomaly detection"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        data = [10.0, 11.0, 12.0, 50.0, 13.0, 12.0, 11.0]  # One outlier
        
        anomalies = analytics.detect_anomalies(data, threshold=2.0)
        assert len(anomalies) == len(data)
        assert anomalies[3] == True  # The outlier should be detected
        assert all(not anomaly for i, anomaly in enumerate(anomalies) if i != 3)

    def test_calculate_moving_average(self):
        """Test moving average calculation"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        window = 3
        
        moving_avg = analytics.calculate_moving_average(data, window)
        
        # First two should be None, then calculate averages
        assert moving_avg[0] is None
        assert moving_avg[1] is None
        assert moving_avg[2] == 2.0  # (1+2+3)/3
        assert moving_avg[3] == 3.0  # (2+3+4)/3
        assert moving_avg[4] == 4.0  # (3+4+5)/3

    def test_calculate_statistics_summary(self):
        """Test statistics summary calculation"""
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        stats = analytics.calculate_statistics_summary(data)
        
        assert stats["count"] == 5
        assert stats["mean"] == 3.0
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["median"] == 3.0
        assert "std" in stats
        assert "q25" in stats
        assert "q75" in stats


if __name__ == "__main__":
    pytest.main([__file__])
