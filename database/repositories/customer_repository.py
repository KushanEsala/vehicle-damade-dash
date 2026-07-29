from __future__ import annotations

from sqlalchemy.orm import Session
from database.models.customer import Customer


class CustomerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.session.query(Customer).filter(Customer.id == customer_id).first()

    def get_by_code(self, code: str) -> Customer | None:
        return self.session.query(Customer).filter(Customer.customer_code == code).first()

    def list_customers(self) -> list[Customer]:
        return self.session.query(Customer).order_by(Customer.created_at.desc()).all()

    def search_customers(self, query: str) -> list[Customer]:
        q = f"%{query.strip()}%"
        return (
            self.session.query(Customer)
            .filter(
                (Customer.full_name.like(q))
                | (Customer.customer_code.like(q))
                | (Customer.nic_or_passport.like(q))
                | (Customer.phone_primary.like(q))
                | (Customer.email.like(q))
            )
            .order_by(Customer.created_at.desc())
            .all()
        )

    def save(self, customer: Customer) -> Customer:
        self.session.add(customer)
        self.session.flush()
        return customer
