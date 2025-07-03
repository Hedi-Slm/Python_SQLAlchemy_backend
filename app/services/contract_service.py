from sqlalchemy.orm import Session
from app.models.contract import Contract
from app.models.user import User, UserRole


def create_contract(db: Session, client_id: int, commercial_id: int, total_amount: float) -> Contract:
    contract = Contract(
        client_id=client_id,
        commercial_id=commercial_id,
        total_amount=total_amount,
        amount_due=total_amount,
        is_signed=False
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


def update_contract(db: Session, contract_id: int, updater: User, **fields) -> Contract:
    contract = db.query(Contract).filter_by(id=contract_id).first()
    if updater.role == UserRole.COMMERCIAL and contract.commercial_id != updater.id:
        raise PermissionError("You can only update your own contracts.")
    for key, value in fields.items():
        setattr(contract, key, value)
    db.commit()
    return contract


def list_unsigned_contracts(db: Session):
    return db.query(Contract).filter_by(is_signed=False).all()


def list_unpaid_contracts(db: Session):
    return db.query(Contract).filter(Contract.amount_due > 0).all()


def get_all_contracts(db: Session):
    return db.query(Contract).all()


def get_contracts_by_user(db: Session, user: User):
    if user.role == UserRole.COMMERCIAL:
        return db.query(Contract).filter_by(commercial_id=user.id).all()
    return db.query(Contract).all()