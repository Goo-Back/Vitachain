"""
Tests for session management functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from app.services.session_service import SessionService
from app.models.session_models import SessionInfo, LogoutResponse


class TestSessionService:
    """Test cases for session service"""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        return Mock()
    
    @pytest.fixture
    def session_service(self, mock_supabase):
        """Session service fixture"""
        return SessionService(mock_supabase)
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, session_service, mock_supabase):
        """Test successful session creation"""
        # Setup mock response
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {'id': 'test-id'}
        ]
        
        # Test session creation
        result = await session_service.create_session(
            user_id='test-user-id',
            session_id='test-session-id',
            device_info={'browser': 'Chrome'},
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )
        
        assert result is True
        mock_supabase.table.return_value.insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_session_failure(self, session_service, mock_supabase):
        """Test session creation failure"""
        # Setup mock response for failure
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = None
        mock_supabase.table.return_value.insert.return_value.execute.return_value.error = 'Database error'
        
        # Test session creation
        result = await session_service.create_session(
            user_id='test-user-id',
            session_id='test-session-id'
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_session_success(self, session_service, mock_supabase):
        """Test successful session validation"""
        # Setup mock response for valid session
        future_time = datetime.utcnow() + timedelta(hours=1)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = [
            {
                'id': 'test-id',
                'user_id': 'test-user-id',
                'expires_at': future_time.isoformat(),
                'is_active': True
            }
        ]
        
        # Test session validation
        result = await session_service.validate_session(
            session_id='test-session-id',
            user_id='test-user-id'
        )
        
        assert result is True
        mock_supabase.table.return_value.select.assert_called()
    
    @pytest.mark.asyncio
    async def test_validate_session_expired(self, session_service, mock_supabase):
        """Test session validation with expired session"""
        # Setup mock response for expired session
        past_time = datetime.utcnow() - timedelta(hours=1)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = [
            {
                'id': 'test-id',
                'user_id': 'test-user-id',
                'expires_at': past_time.isoformat(),
                'is_active': True
            }
        ]
        
        # Test session validation
        result = await session_service.validate_session(
            session_id='test-session-id',
            user_id='test-user-id'
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_invalidate_session_success(self, session_service, mock_supabase):
        """Test successful session invalidation"""
        # Setup mock response
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {'id': 'test-id'}
        ]
        
        # Test session invalidation
        result = await session_service.invalidate_session(
            session_id='test-session-id',
            user_id='test-user-id',
            logout_reason='user_initiated'
        )
        
        assert result is True
        mock_supabase.table.return_value.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_invalidate_all_sessions_success(self, session_service, mock_supabase):
        """Test successful invalidation of all user sessions"""
        # Setup mock response
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {'id': 'test-id-1'},
            {'id': 'test-id-2'}
        ]
        
        # Test invalidating all sessions
        count = await session_service.invalidate_all_user_sessions(
            user_id='test-user-id',
            logout_reason='user_initiated_all_devices'
        )
        
        assert count == 2
        mock_supabase.table.return_value.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_sessions_success(self, session_service, mock_supabase):
        """Test successful retrieval of user sessions"""
        # Setup mock response
        mock_sessions = [
            {
                'id': 'test-id-1',
                'session_id': 'test-session-1',
                'device_info': {'browser': 'Chrome'},
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0',
                'created_at': datetime.utcnow().isoformat(),
                'last_accessed': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                'is_active': True
            }
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = mock_sessions
        
        # Test getting user sessions
        sessions = await session_service.get_user_sessions('test-user-id')
        
        assert len(sessions) == 1
        assert sessions[0]['session_id'] == 'test-session-1'
        mock_supabase.table.return_value.select.assert_called_once()


class TestSessionModels:
    """Test cases for session models"""
    
    def test_logout_request_model(self):
        """Test LogoutRequest model validation"""
        # Test valid request
        request = {
            'logout_all': False,
            'session_id': 'test-session-id'
        }
        from app.models.session_models import LogoutRequest
        logout_request = LogoutRequest(**request)
        
        assert logout_request.logout_all is False
        assert logout_request.session_id == 'test-session-id'
    
    def test_session_info_model(self):
        """Test SessionInfo model validation"""
        # Test valid session info
        session_data = {
            'id': 'test-id',
            'session_id': 'test-session-id',
            'device_info': {'browser': 'Chrome'},
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0',
            'created_at': datetime.utcnow(),
            'last_accessed': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=1),
            'is_active': True,
            'logout_reason': None,
            'logged_out_at': None,
            'force_logout': False
        }
        
        from app.models.session_models import SessionInfo
        session_info = SessionInfo(**session_data)
        
        assert session_info.id == 'test-id'
        assert session_info.session_id == 'test-session-id'
        assert session_info.is_active is True
        assert session_info.force_logout is False


if __name__ == "__main__":
    pytest.main([__file__])
