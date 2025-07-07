from datetime import date, datetime
from app.models.user import User, UserRole
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class TestUserModel:
    """Test cases for User model"""

    def test_user_role_enum(self):
        """Test UserRole enum values"""
        assert UserRole.COMMERCIAL.value == "commercial"
        assert UserRole.SUPPORT.value == "support"
        assert UserRole.GESTION.value == "gestion"

    def test_user_creation(self):
        """Test User model creation"""
        user = User()
        user.id = 1
        user.name = "Test User"
        user.email = "test@example.com"
        user.password = "hashed_password"
        user.role = UserRole.COMMERCIAL

        assert user.id == 1
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.password == "hashed_password"
        assert user.role == UserRole.COMMERCIAL


class TestClientModel:
    """Test cases for Client model"""

    def test_client_creation(self):
        """Test Client model creation"""
        client = Client()
        client.id = 1
        client.full_name = "Test Client"
        client.email = "client@example.com"
        client.phone = "123456789"
        client.company_name = "Test Company"
        client.date_created = date.today()
        client.last_contact = date.today()
        client.commercial_id = 1

        assert client.id == 1
        assert client.full_name == "Test Client"
        assert client.email == "client@example.com"
        assert client.phone == "123456789"
        assert client.company_name == "Test Company"
        assert client.date_created == date.today()
        assert client.last_contact == date.today()
        assert client.commercial_id == 1

    def test_client_required_fields(self):
        """Test Client model with required fields only"""
        client = Client()
        client.id = 1
        client.full_name = "Test Client"
        client.email = "client@example.com"
        client.commercial_id = 1

        assert client.id == 1
        assert client.full_name == "Test Client"
        assert client.email == "client@example.com"
        assert client.commercial_id == 1


class TestContractModel:
    """Test cases for Contract model"""

    def test_contract_creation(self):
        """Test Contract model creation"""
        contract = Contract()
        contract.id = 1
        contract.client_id = 1
        contract.commercial_id = 1
        contract.total_amount = 10000.0
        contract.amount_due = 5000.0
        contract.date_created = date.today()
        contract.is_signed = False

        assert contract.id == 1
        assert contract.client_id == 1
        assert contract.commercial_id == 1
        assert contract.total_amount == 10000.0
        assert contract.amount_due == 5000.0
        assert contract.date_created == date.today()
        assert contract.is_signed == False


class TestEventModel:
    """Test cases for Event model"""
    def test_event_creation(self):
        """Test Event model creation"""
        event = Event()
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

        assert event.id == 1
        assert event.name == "Test Event"
        assert event.contract_id == 1
        assert event.client_id == 1
        assert event.support_id == 1
        assert event.date_start == datetime(2025, 1, 1, 10, 0, 0)
        assert event.date_end == datetime(2025, 1, 1, 18, 0, 0)
        assert event.location == "Test Location"
        assert event.attendees == 100
        assert event.notes == "Test notes"

    def test_event_required_fields(self):
        """Test Event model with required fields only"""
        event = Event()
        event.id = 1
        event.name = "Test Event"
        event.contract_id = 1
        event.client_id = 1
        event.date_start = datetime(2025, 1, 1, 10, 0, 0)
        event.date_end = datetime(2025, 1, 1, 18, 0, 0)

        assert event.id == 1
        assert event.name == "Test Event"
        assert event.contract_id == 1
        assert event.client_id == 1
        assert event.date_start == datetime(2025, 1, 1, 10, 0, 0)
        assert event.date_end == datetime(2025, 1, 1, 18, 0, 0)
        assert event.support_id is None  # Optional field

    def test_event_optional_support(self):
        """Test Event model with optional support_id"""
        event = Event()
        event.name = "Test Event"
        event.contract_id = 1
        event.client_id = 1
        event.date_start = datetime(2025, 1, 1, 10, 0, 0)
        event.date_end = datetime(2025, 1, 1, 18, 0, 0)
        event.support_id = None

        assert event.support_id is None
