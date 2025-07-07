import pytest
from unittest.mock import Mock, patch

from app.services.contract_service import (
    create_contract, update_contract, list_unsigned_contracts,
    list_unpaid_contracts, list_signed_contracts, list_paid_contracts,
    get_all_contracts, get_contracts_by_user, get_all_clients,
    get_commercial_users
)
from app.models.user import UserRole
from app.models.contract import Contract
from app.models.client import Client
from app.models.user import User


class TestCreateContract:
    def test_create_contract_success(self, mock_database_session):
        mock_contract = Mock(spec=Contract)
        mock_contract.id = 1
        mock_contract.client_id = 1
        mock_contract.commercial_id = 1
        mock_contract.total_amount = 10000.0
        mock_contract.amount_due = 10000.0
        mock_contract.is_signed = False

        mock_database_session.add = Mock()
        mock_database_session.commit = Mock()
        mock_database_session.refresh = Mock()

        with patch('app.services.contract_service.Contract', return_value=mock_contract):
            result = create_contract(mock_database_session, 1, 1, 10000.0)

        assert result == mock_contract
        mock_database_session.add.assert_called_once()
        mock_database_session.commit.assert_called_once()
        mock_database_session.refresh.assert_called_once_with(mock_contract)

    def test_create_contract_with_zero_amount(self, mock_database_session):
        mock_contract = Mock(spec=Contract)
        mock_contract.total_amount = 0.0
        mock_contract.amount_due = 0.0

        with patch('app.services.contract_service.Contract', return_value=mock_contract):
            result = create_contract(mock_database_session, 1, 1, 0.0)

        assert result.total_amount == 0.0
        assert result.amount_due == 0.0


class TestUpdateContract:
    def test_update_contract_success_gestion_user(self, mock_database_session, mock_gestion_user):
        mock_contract = Mock(spec=Contract)
        mock_contract.id = 1
        mock_contract.commercial_id = 2

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_contract

        result = update_contract(mock_database_session, 1, mock_gestion_user, total_amount=15000.0, is_signed=True)

        assert result == mock_contract
        assert mock_contract.total_amount == 15000.0
        assert mock_contract.is_signed is True
        mock_database_session.commit.assert_called_once()

    def test_update_contract_success_commercial_own_contract(self, mock_database_session, mock_user):
        mock_contract = Mock(spec=Contract)
        mock_contract.id = 1
        mock_contract.commercial_id = mock_user.id

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_contract

        result = update_contract(mock_database_session, 1, mock_user, is_signed=True)

        assert result == mock_contract
        assert mock_contract.is_signed is True
        mock_database_session.commit.assert_called_once()

    def test_update_contract_permission_error_commercial_other_contract(self, mock_database_session, mock_user):
        mock_contract = Mock(spec=Contract)
        mock_contract.id = 1
        mock_contract.commercial_id = 999

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_contract

        with pytest.raises(PermissionError, match="You can only update your own contracts."):
            update_contract(mock_database_session, 1, mock_user, is_signed=True)

    def test_update_contract_multiple_fields(self, mock_database_session, mock_gestion_user):
        mock_contract = Mock(spec=Contract)
        mock_contract.id = 1

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_contract

        result = update_contract(mock_database_session, 1, mock_gestion_user,
                                 total_amount=20000.0, amount_due=10000.0, is_signed=True)

        assert result == mock_contract
        assert mock_contract.total_amount == 20000.0
        assert mock_contract.amount_due == 10000.0
        assert mock_contract.is_signed is True


class TestListContracts:
    def test_list_unsigned_contracts(self, mock_database_session):
        mock_contracts = [Mock(spec=Contract) for _ in range(3)]
        mock_database_session.query.return_value.filter_by.return_value.all.return_value = mock_contracts

        result = list_unsigned_contracts(mock_database_session)

        assert result == mock_contracts
        mock_database_session.query.assert_called_with(Contract)
        mock_database_session.query.return_value.filter_by.assert_called_with(is_signed=False)

    def test_list_unpaid_contracts(self, mock_database_session):
        mock_contracts = [Mock(spec=Contract) for _ in range(2)]
        mock_database_session.query.return_value.filter.return_value.all.return_value = mock_contracts

        result = list_unpaid_contracts(mock_database_session)

        assert result == mock_contracts
        mock_database_session.query.assert_called_with(Contract)

    def test_list_signed_contracts(self, mock_database_session):
        mock_contracts = [Mock(spec=Contract) for _ in range(4)]
        mock_database_session.query.return_value.filter_by.return_value.all.return_value = mock_contracts

        result = list_signed_contracts(mock_database_session)

        assert result == mock_contracts
        mock_database_session.query.assert_called_with(Contract)
        mock_database_session.query.return_value.filter_by.assert_called_with(is_signed=True)

    def test_list_paid_contracts(self, mock_database_session):
        mock_contracts = [Mock(spec=Contract) for _ in range(2)]
        mock_database_session.query.return_value.filter_by.return_value.all.return_value = mock_contracts

        result = list_paid_contracts(mock_database_session)

        assert result == mock_contracts
        mock_database_session.query.assert_called_with(Contract)
        mock_database_session.query.return_value.filter_by.assert_called_with(amount_due=0)

    def test_get_all_contracts(self, mock_database_session):
        mock_contracts = [Mock(spec=Contract) for _ in range(5)]
        mock_database_session.query.return_value.all.return_value = mock_contracts

        result = get_all_contracts(mock_database_session)

        assert result == mock_contracts
        mock_database_session.query.assert_called_with(Contract)


class TestGetContractsByRole:
    def test_get_contracts_by_user_commercial(self, mock_database_session, mock_user):
        mock_contracts = [Mock(spec=Contract) for _ in range(3)]
        mock_database_session.query.return_value.filter_by.return_value.all.return_value = mock_contracts

        result = get_contracts_by_user(mock_database_session, mock_user)

        assert result == mock_contracts
        mock_database_session.query.assert_called_with(Contract)
        mock_database_session.query.return_value.filter_by.assert_called_with(commercial_id=mock_user.id)

    def test_get_contracts_by_user_gestion(self, mock_database_session, mock_gestion_user):
        mock_contracts = [Mock(spec=Contract) for _ in range(5)]
        mock_database_session.query.return_value.all.return_value = mock_contracts

        result = get_contracts_by_user(mock_database_session, mock_gestion_user)

        assert result == mock_contracts
        mock_database_session.query.assert_called_with(Contract)

    def test_get_contracts_by_user_support(self, mock_database_session, mock_support_user):
        mock_contracts = [Mock(spec=Contract) for _ in range(5)]
        mock_database_session.query.return_value.all.return_value = mock_contracts

        result = get_contracts_by_user(mock_database_session, mock_support_user)

        assert result == mock_contracts
        mock_database_session.query.assert_called_with(Contract)

    def test_get_all_clients(self, mock_database_session):
        mock_clients = [Mock(spec=Client) for _ in range(3)]
        mock_database_session.query.return_value.all.return_value = mock_clients

        result = get_all_clients(mock_database_session)

        assert result == mock_clients
        mock_database_session.query.assert_called_with(Client)

    def test_get_commercial_users(self, mock_database_session):
        mock_users = [Mock(spec=User) for _ in range(2)]
        mock_database_session.query.return_value.filter_by.return_value.all.return_value = mock_users

        result = get_commercial_users(mock_database_session)

        assert result == mock_users
        mock_database_session.query.assert_called_with(User)
        mock_database_session.query.return_value.filter_by.assert_called_with(role=UserRole.COMMERCIAL)


class TestEdgeCases:
    def test_update_contract_nonexistent_contract(self, mock_database_session, mock_gestion_user):
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(AttributeError):
            update_contract(mock_database_session, 999, mock_gestion_user, total_amount=1000)

    def test_create_contract_negative_amount(self, mock_database_session):
        mock_contract = Mock(spec=Contract)
        mock_contract.total_amount = -5000.0
        mock_contract.amount_due = -5000.0

        with patch('app.services.contract_service.Contract', return_value=mock_contract):
            result = create_contract(mock_database_session, 1, 1, -5000.0)

        assert result.total_amount == -5000.0
        assert result.amount_due == -5000.0

    def test_empty_contract_lists(self, mock_database_session):
        mock_database_session.query.return_value.filter_by.return_value.all.return_value = []

        assert list_unsigned_contracts(mock_database_session) == []
        assert list_signed_contracts(mock_database_session) == []
        assert list_paid_contracts(mock_database_session) == []
