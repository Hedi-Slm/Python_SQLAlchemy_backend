from sqlalchemy.orm import Session, joinedload

from app.models.contract import Contract
from app.models.event import Event
from app.models.user import User, UserRole
from datetime import datetime


def create_event(db: Session, client_id: int, contract_id: int, name: str, start: datetime, end: datetime,
                 location: str, attendees: int, notes: str) -> Event:
    event = Event(
        name=name,
        client_id=client_id,
        contract_id=contract_id,
        date_start=start,
        date_end=end,
        location=location,
        attendees=attendees,
        notes=notes
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def assign_support_to_event(db: Session, event_id: int, support_user_id: int) -> Event:
    event = db.query(Event).filter_by(id=event_id).first()
    event.support_id = support_user_id
    db.commit()
    return event


def update_event(db: Session, event_id: int, updater: User, **fields) -> Event:
    event = db.query(Event).filter_by(id=event_id).first()
    if updater.role == UserRole.SUPPORT and event.support_id != updater.id:
        raise PermissionError("You can only update your assigned events.")
    for key, value in fields.items():
        setattr(event, key, value)
    db.commit()
    return event


def list_unassigned_events(db: Session):
    return db.query(Event).filter_by(support_id=None).all()


def list_events_by_support(db: Session, support_user_id: int):
    return db.query(Event).filter_by(support_id=support_user_id).all()


def get_all_events(db: Session):
    return db.query(Event).all()


def get_events_with_details(db: Session):
    return db.query(Event).options(joinedload(Event.contract).joinedload(Contract.client),
                                   joinedload(Event.support_contact)).all()


def get_filtered_events(db: Session, filters: dict):
    query = db.query(Event).options(
        joinedload(Event.contract).joinedload(Contract.client),
        joinedload(Event.support_contact)
    )

    for filter_key, filter_value in filters.items():
        if filter_key == "support_contact_id":
            if filter_value is None:
                query = query.filter(Event.support_id is None)
            else:
                query = query.filter(Event.support_id == filter_value)
        elif filter_key == "support_contact_id_not_null":
            query = query.filter(Event.support_id is not None)
        elif filter_key == "commercial_contact_id":
            query = query.join(Contract).filter(Contract.commercial_id == filter_value)
        elif filter_key == "start_date_gte":
            query = query.filter(Event.date_start >= filter_value)
        elif filter_key == "end_date_lt":
            query = query.filter(Event.date_end < filter_value)

    return query.all()


def get_signed_contracts_for_commercial(db: Session, commercial_id: int):
    """Get signed contracts for a specific commercial user"""
    return db.query(Contract).filter(Contract.commercial_id == commercial_id,
                                     Contract.is_signed == True).options(joinedload(Contract.client)).all()


def get_contract_by_id(db: Session, contract_id: int):
    """Get a contract by its ID"""
    return db.query(Contract).filter_by(id=contract_id).first()


def get_events_for_support_user(db: Session, support_user_id: int):
    """Get events that a support user can update (assigned to them or unassigned)"""
    return db.query(Event).filter((Event.support_id == support_user_id) | (Event.support_id is None)).options(
        joinedload(Event.contract).joinedload(Contract.client), joinedload(Event.support_contact)).all()


def get_all_events_for_management(db: Session):
    """Get all events for management users"""
    return db.query(Event).options(joinedload(Event.contract).joinedload(Contract.client),
                                   joinedload(Event.support_contact)).all()


def get_support_users(db: Session):
    """Get all support users"""
    return db.query(User).filter_by(role=UserRole.SUPPORT).all()
