"""
Tests for comparison utilities.
"""
import pytest
from datetime import datetime, timedelta
from src.core.comparison import compare_sessions, get_quality_trend, get_recent_sessions
from src.db.models import CheckSession, Issue


@pytest.mark.integration
class TestCompareSessions:
    """Tests for comparing two sessions."""
    
    def test_compare_sessions_improving(self, clean_db, db_session):
        """Test comparison showing improving trend."""
        # Create first session (older, more issues)
        session1 = CheckSession(
            filename="test1.csv",
            file_format="csv",
            rows=100,
            issues_found=20,
            created_at=datetime.utcnow() - timedelta(days=7)
        )
        db_session.add(session1)
        db_session.flush()
        
        # Add issues to session1
        for i in range(20):
            issue = Issue(
                session_id=session1.id,
                row_number=i,
                column_name="test_col",
                issue_type="test_issue",
                description=f"Issue {i}",
                severity="high" if i < 10 else "medium"
            )
            db_session.add(issue)
        
        # Create second session (newer, fewer issues)
        session2 = CheckSession(
            filename="test2.csv",
            file_format="csv",
            rows=100,
            issues_found=10,
            created_at=datetime.utcnow()
        )
        db_session.add(session2)
        db_session.flush()
        
        # Add issues to session2
        for i in range(10):
            issue = Issue(
                session_id=session2.id,
                row_number=i,
                column_name="test_col",
                issue_type="test_issue",
                description=f"Issue {i}",
                severity="high" if i < 3 else "medium"
            )
            db_session.add(issue)
        
        db_session.commit()
        
        # Compare sessions
        result = compare_sessions(session1.id, session2.id, db_session)
        
        assert result is not None
        assert "session1" in result
        assert "session2" in result
        assert "comparison" in result
        
        assert result["comparison"]["total_issues_change"] == -10
        assert result["comparison"]["trend"] == "improving"
        assert result["comparison"]["trend_icon"] == "📈"
    
    def test_compare_sessions_degrading(self, clean_db, db_session):
        """Test comparison showing degrading trend."""
        # Create first session (older, fewer issues)
        session1 = CheckSession(
            filename="test1.csv",
            file_format="csv",
            rows=100,
            issues_found=5,
            created_at=datetime.utcnow() - timedelta(days=7)
        )
        db_session.add(session1)
        db_session.flush()
        
        for i in range(5):
            issue = Issue(
                session_id=session1.id,
                row_number=i,
                column_name="test_col",
                issue_type="test_issue",
                description=f"Issue {i}",
                severity="medium"
            )
            db_session.add(issue)
        
        # Create second session (newer, more issues)
        session2 = CheckSession(
            filename="test2.csv",
            file_format="csv",
            rows=100,
            issues_found=15,
            created_at=datetime.utcnow()
        )
        db_session.add(session2)
        db_session.flush()
        
        for i in range(15):
            issue = Issue(
                session_id=session2.id,
                row_number=i,
                column_name="test_col",
                issue_type="test_issue",
                description=f"Issue {i}",
                severity="high" if i < 8 else "medium"
            )
            db_session.add(issue)
        
        db_session.commit()
        
        # Compare sessions
        result = compare_sessions(session1.id, session2.id, db_session)
        
        assert result["comparison"]["total_issues_change"] == 10
        assert result["comparison"]["trend"] == "degrading"
        assert result["comparison"]["trend_icon"] == "📉"
    
    def test_compare_sessions_stable(self, clean_db, db_session):
        """Test comparison showing stable trend."""
        session1 = CheckSession(
            filename="test1.csv",
            file_format="csv",
            rows=100,
            issues_found=10,
            created_at=datetime.utcnow() - timedelta(days=7)
        )
        db_session.add(session1)
        db_session.flush()
        
        for i in range(10):
            issue = Issue(
                session_id=session1.id,
                row_number=i,
                column_name="test_col",
                issue_type="test_issue",
                description=f"Issue {i}",
                severity="medium"
            )
            db_session.add(issue)
        
        session2 = CheckSession(
            filename="test2.csv",
            file_format="csv",
            rows=100,
            issues_found=10,
            created_at=datetime.utcnow()
        )
        db_session.add(session2)
        db_session.flush()
        
        for i in range(10):
            issue = Issue(
                session_id=session2.id,
                row_number=i,
                column_name="test_col",
                issue_type="test_issue",
                description=f"Issue {i}",
                severity="medium"
            )
            db_session.add(issue)
        
        db_session.commit()
        
        result = compare_sessions(session1.id, session2.id, db_session)
        
        assert result["comparison"]["total_issues_change"] == 0
        assert result["comparison"]["trend"] == "stable"
        assert result["comparison"]["trend_icon"] == "➡️"
    
    def test_compare_sessions_not_found(self, clean_db, db_session):
        """Test comparison with non-existent sessions."""
        result = compare_sessions(999, 998, db_session)
        
        assert "error" in result
        assert "not found" in result["error"].lower()


@pytest.mark.integration
class TestQualityTrend:
    """Tests for quality trend analysis."""
    
    def test_get_quality_trend_improving(self, clean_db, db_session):
        """Test trend analysis showing improvement."""
        # Create multiple previous sessions with many issues
        base_time = datetime.utcnow() - timedelta(days=30)
        for i in range(5):
            session = CheckSession(
                filename=f"test{i}.csv",
                file_format="csv",
                rows=100,
                issues_found=20,
                created_at=base_time + timedelta(days=i*5)
            )
            db_session.add(session)
            db_session.flush()
        
        # Create current session with fewer issues
        current_session = CheckSession(
            filename="current.csv",
            file_format="csv",
            rows=100,
            issues_found=10,
            created_at=datetime.utcnow()
        )
        db_session.add(current_session)
        db_session.commit()
        
        result = get_quality_trend(current_session.id, days_back=30, db_session=db_session)
        
        assert result is not None
        assert "current_session" in result
        assert "comparison" in result
        assert "trend" in result
        assert result["trend"] == "improving"
    
    def test_get_quality_trend_no_previous(self, clean_db, db_session):
        """Test trend analysis with no previous sessions."""
        current_session = CheckSession(
            filename="current.csv",
            file_format="csv",
            rows=100,
            issues_found=10,
            created_at=datetime.utcnow()
        )
        db_session.add(current_session)
        db_session.commit()
        
        result = get_quality_trend(current_session.id, days_back=30, db_session=db_session)
        
        assert result is not None
        assert result["trend"] == "no_previous_data"
        assert "message" in result
    
    def test_get_quality_trend_degrading(self, clean_db, db_session):
        """Test trend analysis showing degradation."""
        # Create previous sessions with few issues
        base_time = datetime.utcnow() - timedelta(days=30)
        for i in range(5):
            session = CheckSession(
                filename=f"test{i}.csv",
                file_format="csv",
                rows=100,
                issues_found=5,
                created_at=base_time + timedelta(days=i*5)
            )
            db_session.add(session)
        
        # Create current session with many issues
        current_session = CheckSession(
            filename="current.csv",
            file_format="csv",
            rows=100,
            issues_found=20,
            created_at=datetime.utcnow()
        )
        db_session.add(current_session)
        db_session.commit()
        
        result = get_quality_trend(current_session.id, days_back=30, db_session=db_session)
        
        assert result["trend"] == "degrading"


@pytest.mark.unit
class TestRecentSessions:
    """Tests for getting recent sessions."""
    
    def test_get_recent_sessions(self, clean_db, db_session):
        """Test getting recent sessions."""
        # Create multiple sessions
        for i in range(10):
            session = CheckSession(
                filename=f"test{i}.csv",
                file_format="csv",
                rows=100,
                issues_found=i,
                created_at=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(session)
        db_session.commit()
        
        sessions = get_recent_sessions(limit=5, db_session=db_session)
        
        assert len(sessions) == 5
        # Should be ordered by created_at desc
        for i in range(len(sessions) - 1):
            assert sessions[i].created_at >= sessions[i+1].created_at

