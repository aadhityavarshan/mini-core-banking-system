import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate

logger = logging.getLogger(__name__)


def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
    customer = Customer(
        name=customer_in.name,
        email=customer_in.email,
        phone=customer_in.phone,
    )
    db.add(customer)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this email or phone already exists",
        ) from exc
    db.refresh(customer)
    logger.info("Created customer %s", customer.customer_id)
    return customer


def list_customers(db: Session) -> list[Customer]:
    return db.query(Customer).order_by(Customer.customer_id).all()


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()
