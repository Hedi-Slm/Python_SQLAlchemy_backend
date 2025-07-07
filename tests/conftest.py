import pytest
from unittest.mock import Mock
from datetime import date, datetime
from app.models.user import User, UserRole
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    user = Mock(spec=User)
    user.id = 1
    user.name = "Test User"
    user.email = "test@example.com"
    user.password = "hashed_password"
    user.role = UserRole.COMMERCIAL
    return user


@pytest.fixture
def mock_support_user():
    """Create a mock support user for testing"""
    user = Mock(spec=User)
    user.id = 2
    user.name = "Support User"
    user.email = "support@example.com"
    user.password = "hashed_password"
    user.role = UserRole.SUPPORT
    return user


@pytest.fixture
def mock_gestion_user():
    """Create a mock gestion user for testing"""
    user = Mock(spec=User)
    user.id = 3
    user.name = "Gestion User"
    user.email = "gestion@example.com"
    user.password = "hashed_password"
    user.role = UserRole.GESTION
    return user


@pytest.fixture
def mock_client():
    """Create a mock client for testing"""
    client = Mock(spec=Client)
    client.id = 1
    client.full_name = "Test Client"
    client.email = "client@example.com"
    client.phone = "06.12.25.35.45"
    client.company_name = "Test Company"
    client.date_created = date.today()
    client.last_contact = date.today()
    client.commercial_id = 1
    return client


@pytest.fixture
def mock_contract():
    """Create a mock contract for testing"""
    contract = Mock(spec=Contract)
    contract.id = 1
    contract.client_id = 1
    contract.commercial_id = 1
    contract.total_amount = 10000.0
    contract.amount_due = 5000.0
    contract.date_created = date.today()
    contract.is_signed = False
    return contract


@pytest.fixture
def mock_event():
    """Create a mock event for testing"""
    event = Mock(spec=Event)
    event.id = 1
    event.name = "Test Event"
    event.contract_id = 1
    event.client_id = 1
    event.support_id = 1
    event.date_start = datetime(2025, 1, 1, 10, 0, 0)
    event.date_end = datetime(2025, 1, 1, 18, 0, 0)
    event.location = "Test Location"
    event.attendees = 100
    event.notes = "Test notes"
    return event


@pytest.fixture
def mock_database_session():
    """Create a mock database session for testing"""
    db_session = Mock()
    db_session.query.return_value = Mock()
    db_session.add = Mock()
    db_session.commit = Mock()
    db_session.refresh = Mock()
    db_session.close = Mock()
    return db_session


@pytest.fixture
def sample_client_data():
    """Provide sample client data for testing"""
    return {
        "full_name": "Test Client",
        "email": "client@example.com",
        "phone": "06.12.25.35.45",
        "company_name": "Test Company"
    }


@pytest.fixture
def sample_contract_data():
    """Provide sample contract data for testing"""
    return {
        "client_id": 1,
        "commercial_id": 1,
        "total_amount": 10000.0,
        "amount_due": 5000.0,
        "date_created": date.today(),
        "is_signed": False
    }


@pytest.fixture
def sample_event_data():
    """Provide sample event data for testing"""
    return {
        "name": "Test Event",
        "contract_id": 1,
        "client_id": 1,
        "support_id": 1,
        "date_start": datetime(2025, 1, 1, 10, 0, 0),
        "date_end": datetime(2025, 1, 1, 18, 0, 0),
        "location": "Test Location",
        "attendees": 100,
        "notes": "Test notes"
    }


@pytest.fixture
def sample_user_credentials():
    """Provide sample user credentials for testing"""
    return {
        "email": "test@example.com",
        "password": "test_password_123"
    }
