import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.services.event_service import (
    create_event, assign_support_to_event, update_event,
    list_unassigned_events, list_events_by_support, get_all_events,
    get_events_with_details, get_filtered_events, get_signed_contracts_for_commercial,
)
from app.models.event import Event
from app.models.contract import Contract


class TestCreateEvent:
    def test_create_event_success(self, mock_database_session, sample_event_data):
        mock_event = Mock(spec=Event, **sample_event_data)
        mock_event.id = 1

        with patch('app.services.event_service.Event', return_value=mock_event):
            result = create_event(
                db=mock_database_session,
                client_id=sample_event_data["client_id"],
                contract_id=sample_event_data["contract_id"],
                name=sample_event_data["name"],
                start=sample_event_data["date_start"],
                end=sample_event_data["date_end"],
                location=sample_event_data["location"],
                attendees=sample_event_data["attendees"],
                notes=sample_event_data["notes"]
            )

        assert result == mock_event
        mock_database_session.add.assert_called_once_with(mock_event)
        mock_database_session.commit.assert_called_once()
        mock_database_session.refresh.assert_called_once_with(mock_event)

    def test_create_event_with_zero_attendees(self, mock_database_session, sample_event_data):
        sample_event_data["attendees"] = 0
        mock_event = Mock(spec=Event, **sample_event_data)

        with patch('app.services.event_service.Event', return_value=mock_event):
            result = create_event(
                db=mock_database_session,
                client_id=sample_event_data["client_id"],
                contract_id=sample_event_data["contract_id"],
                name=sample_event_data["name"],
                start=sample_event_data["date_start"],
                end=sample_event_data["date_end"],
                location=sample_event_data["location"],
                attendees=sample_event_data["attendees"],
                notes=sample_event_data["notes"]
            )

        assert result.attendees == 0

    def test_create_event_with_empty_notes(self, mock_database_session, sample_event_data):
        sample_event_data["notes"] = ""
        mock_event = Mock(spec=Event, **sample_event_data)

        with patch('app.services.event_service.Event', return_value=mock_event):
            result = create_event(
                db=mock_database_session,
                client_id=sample_event_data["client_id"],
                contract_id=sample_event_data["contract_id"],
                name=sample_event_data["name"],
                start=sample_event_data["date_start"],
                end=sample_event_data["date_end"],
                location=sample_event_data["location"],
                attendees=sample_event_data["attendees"],
                notes=sample_event_data["notes"]
            )

        assert result.notes == ""


class TestAssignSupportToEvent:
    def test_assign_support_to_event_success(self, mock_database_session):
        event_id = 1
        support_user_id = 2

        mock_event = Mock(spec=Event)
        mock_event.id = event_id
        mock_event.support_id = None

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_event

        result = assign_support_to_event(mock_database_session, event_id, support_user_id)

        assert result == mock_event
        assert mock_event.support_id == support_user_id
        mock_database_session.commit.assert_called_once()

    def test_assign_support_to_event_reassign(self, mock_database_session):
        event_id = 1
        old_support_id = 2
        new_support_id = 3

        mock_event = Mock(spec=Event)
        mock_event.id = event_id
        mock_event.support_id = old_support_id

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_event

        result = assign_support_to_event(mock_database_session, event_id, new_support_id)

        assert result == mock_event
        assert mock_event.support_id == new_support_id
        mock_database_session.commit.assert_called_once()


class TestUpdateEvent:
    def test_update_event_success_gestion_user(self, mock_database_session, mock_gestion_user):
        event_id = 1
        mock_event = Mock(spec=Event)
        mock_event.id = event_id
        mock_event.support_id = 2

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_event

        update_fields = {"name": "Updated Event", "attendees": 150}

        result = update_event(mock_database_session, event_id, mock_gestion_user, **update_fields)

        assert result == mock_event
        assert mock_event.name == "Updated Event"
        assert mock_event.attendees == 150
        mock_database_session.commit.assert_called_once()

    def test_update_event_success_support_assigned(self, mock_database_session, mock_support_user):
        event_id = 1
        mock_event = Mock(spec=Event)
        mock_event.id = event_id
        mock_event.support_id = mock_support_user.id

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_event

        update_fields = {"location": "Updated Location"}

        result = update_event(mock_database_session, event_id, mock_support_user, **update_fields)

        assert result == mock_event
        assert mock_event.location == "Updated Location"
        mock_database_session.commit.assert_called_once()

    def test_update_event_permission_error_support_not_assigned(self, mock_database_session, mock_support_user):
        event_id = 1
        mock_event = Mock(spec=Event)
        mock_event.id = event_id
        mock_event.support_id = 999

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_event

        update_fields = {"location": "Updated Location"}

        with pytest.raises(PermissionError, match="You can only update your assigned events."):
            update_event(mock_database_session, event_id, mock_support_user, **update_fields)

    def test_update_event_multiple_fields(self, mock_database_session, mock_gestion_user):
        event_id = 1
        mock_event = Mock(spec=Event)
        mock_event.id = event_id

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_event

        update_fields = {
            "name": "Updated Event",
            "location": "New Location",
            "attendees": 200,
            "notes": "Updated notes"
        }

        result = update_event(mock_database_session, event_id, mock_gestion_user, **update_fields)

        assert result == mock_event
        assert mock_event.name == "Updated Event"
        assert mock_event.location == "New Location"
        assert mock_event.attendees == 200
        assert mock_event.notes == "Updated notes"


class TestListEvents:
    def test_list_unassigned_events(self, mock_database_session):
        mock_events = [Mock(spec=Event) for _ in range(3)]
        mock_database_session.query.return_value.filter_by.return_value.all.return_value = mock_events

        result = list_unassigned_events(mock_database_session)

        assert result == mock_events

    def test_list_events_by_support(self, mock_database_session):
        support_user_id = 2
        mock_events = [Mock(spec=Event) for _ in range(2)]
        mock_database_session.query.return_value.filter_by.return_value.all.return_value = mock_events

        result = list_events_by_support(mock_database_session, support_user_id)

        assert result == mock_events

    def test_get_all_events(self, mock_database_session):
        mock_events = [Mock(spec=Event) for _ in range(5)]
        mock_database_session.query.return_value.all.return_value = mock_events

        result = get_all_events(mock_database_session)

        assert result == mock_events

    def test_get_events_with_details(self, mock_database_session):
        mock_events = [Mock(spec=Event) for _ in range(3)]
        mock_database_session.query.return_value.options.return_value.all.return_value = mock_events

        result = get_events_with_details(mock_database_session)

        assert result == mock_events


class TestGetFilteredEvents:
    def test_get_filtered_events_support_contact_id(self, mock_database_session):
        filters = {"support_contact_id": 2}
        mock_events = [Mock(spec=Event) for _ in range(2)]

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_events
        mock_database_session.query.return_value.options.return_value = mock_query

        result = get_filtered_events(mock_database_session, filters)

        assert result == mock_events

    def test_get_filtered_events_support_contact_id_none(self, mock_database_session):
        filters = {"support_contact_id": None}
        mock_events = [Mock(spec=Event) for _ in range(3)]

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_events
        mock_database_session.query.return_value.options.return_value = mock_query

        result = get_filtered_events(mock_database_session, filters)

        assert result == mock_events

    def test_get_filtered_events_commercial_contact_id(self, mock_database_session):
        filters = {"commercial_contact_id": 1}
        mock_events = [Mock(spec=Event) for _ in range(2)]

        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.all.return_value = mock_events
        mock_database_session.query.return_value.options.return_value = mock_query

        result = get_filtered_events(mock_database_session, filters)

        assert result == mock_events

    def test_get_filtered_events_date_range(self, mock_database_session):
        filters = {
            "start_date_gte": datetime(2025, 1, 1),
            "end_date_lt": datetime(2025, 12, 31)
        }
        mock_events = [Mock(spec=Event) for _ in range(3)]

        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.all.return_value = mock_events
        mock_database_session.query.return_value.options.return_value = mock_query

        result = get_filtered_events(mock_database_session, filters)

        assert result == mock_events

    def test_get_filtered_events_multiple_filters(self, mock_database_session):
        filters = {
            "support_contact_id": 2,
            "start_date_gte": datetime(2025, 1, 1),
            "commercial_contact_id": 1
        }
        mock_events = [Mock(spec=Event)]

        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.join.return_value.filter.return_value.all.return_value = mock_events
        mock_database_session.query.return_value.options.return_value = mock_query

        result = get_filtered_events(mock_database_session, filters)

        assert result == mock_events


class TestGetSignedContractsForCommercial:
    def test_get_signed_contracts_for_commercial(self, mock_database_session):
        commercial_id = 1
        mock_contracts = [Mock(spec=Contract) for _ in range(3)]

        mock_database_session.query.return_value.filter.return_value.options.return_value.all.return_value = mock_contracts

        result = get_signed_contracts_for_commercial(mock_database_session, commercial_id)

        assert result == mock_contracts
        mock_database_session.query.assert_called_with(Contract)