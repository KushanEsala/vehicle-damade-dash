from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from core.exceptions import DuplicateResourceError, ResourceNotFoundError, ValidationError
from core.security import hash_password, generate_temporary_password
from database.repositories.customer_repository import CustomerRepository
from database.repositories.user_repository import UserRepository
from database.repositories.audit_repository import AuditRepository
from database.models.customer import Customer
from database.models.user import User


class CustomerService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.customer_repo = CustomerRepository(session)
        self.user_repo = UserRepository(session)
        self.audit_repo = AuditRepository(session)

    def generate_customer_code(self) -> str:
        year = datetime.now(timezone.utc).year
        count = len(self.customer_repo.list_customers()) + 1
        return f"CUS-{year}-{count:06d}"

    def create_customer(
        self,
        full_name: str,
        phone_primary: str,
        email: str,
        address_line_1: str,
        city: str,
        operator_user_id: int,
        nic_or_passport: str | None = None,
        phone_secondary: str | None = None,
        address_line_2: str | None = None,
        postal_code: str | None = None,
        notes: str | None = None,
        create_user_account: bool = False,
    ) -> tuple[Customer, str | None]:
        email = email.strip().lower()
        if not full_name.strip() or not phone_primary.strip() or not email or not address_line_1.strip() or not city.strip():
            raise ValidationError("Full name, primary phone, email, address, and city are required.")

        code = self.generate_customer_code()

        customer = Customer(
            customer_code=code,
            full_name=full_name.strip(),
            nic_or_passport=nic_or_passport.strip() if nic_or_passport else None,
            phone_primary=phone_primary.strip(),
            phone_secondary=phone_secondary.strip() if phone_secondary else None,
            email=email,
            address_line_1=address_line_1.strip(),
            address_line_2=address_line_2.strip() if address_line_2 else None,
            city=city.strip(),
            postal_code=postal_code.strip() if postal_code else None,
            notes=notes.strip() if notes else None,
            status="active",
            created_by=operator_user_id,
        )
        self.customer_repo.save(customer)

        temp_password = None
        if create_user_account:
            customer_role = self.user_repo.get_role_by_code("customer")
            if customer_role:
                username = f"cus_{customer.id}"
                temp_password = generate_temporary_password()
                user = User(
                    role_id=customer_role.id,
                    customer_id=customer.id,
                    username=username,
                    email=email,
                    password_hash=hash_password(temp_password),
                    must_change_password=True,
                    is_active=True,
                    created_by=operator_user_id,
                )
                self.user_repo.save(user)

        self.audit_repo.log_event(
            action="create_customer",
            entity_type="customer",
            user_id=operator_user_id,
            entity_id=customer.id,
            new_values={"code": code, "name": full_name, "email": email},
        )

        return customer, temp_password

    def get_customer_by_id(self, customer_id: int) -> Customer:
        c = self.customer_repo.get_by_id(customer_id)
        if not c:
            raise ResourceNotFoundError(f"Customer #{customer_id} not found.")
        return c

    def list_customers(self) -> list[Customer]:
        return self.customer_repo.list_customers()

    def search_customers(self, query: str) -> list[Customer]:
        return self.customer_repo.search_customers(query)
