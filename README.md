# Mini Core Banking System

A lightweight backend-only banking API built with FastAPI, SQLAlchemy, and SQLite. The project simulates core banking operations such as customer onboarding, account creation, deposits, withdrawals, transfers, and transaction history.

## Problem Statement

Banks need a core system to manage customers, accounts, balances, and money movement. This project implements a simplified version of that system for learning, interview practice, and portfolio use.

## Features

- Create and retrieve customers
- Create and retrieve accounts
- List accounts for a customer
- Deposit funds into an account
- Withdraw funds from an account
- Transfer funds between accounts
- View transaction history for an account
- Enforce basic banking validation rules

## Technology Stack

- Python 3.13
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest

## Project Structure

```text
mini-core-banking-system/
|-- app/
|   |-- database/
|   |-- models/
|   |-- routes/
|   |-- schemas/
|   |-- services/
|   `-- main.py
|-- tests/
|-- data/
|-- requirements.txt
`-- README.md
```

## Architecture

The application follows a simple layered structure:

- `routes`: FastAPI endpoints
- `schemas`: request and response validation
- `services`: business logic and balance rules
- `models`: SQLAlchemy ORM models
- `database`: engine, session, and table initialization

Request flow:

1. A client sends a request to a FastAPI route.
2. Pydantic validates the request body.
3. A service applies business rules.
4. SQLAlchemy reads or writes data in SQLite.
5. The API returns a structured JSON response.

Logging:

- Request method, path, status code, and response time are logged
- Customer, account, deposit, withdrawal, and transfer actions are logged

## Data Model

### Customer

- `customer_id`
- `name`
- `email`
- `phone`

### Account

- `account_id`
- `customer_id`
- `account_type`
- `balance`

### Transaction

- `transaction_id`
- `account_id`
- `transaction_type`
- `amount`
- `status`
- `reference_account_id`
- `timestamp`

## Database Schema

```text
Customer
  customer_id (PK)
  name
  email
  phone
      |
      | 1-to-many
      v
Account
  account_id (PK)
  customer_id (FK -> Customer.customer_id)
  account_type
  balance
      |
      | 1-to-many
      v
Transaction
  transaction_id (PK)
  account_id (FK -> Account.account_id)
  transaction_type
  amount
  status
  reference_account_id
  timestamp
```

## Validation Rules

- Customer must exist before an account can be created
- Account must exist before deposits, withdrawals, or transfers
- Amount must be greater than zero
- Withdrawal cannot exceed the available balance
- Transfer cannot exceed the source account balance
- Source and destination accounts for transfer must be different
- Duplicate customer email or phone is rejected

## Setup

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the API:

```powershell
python -m uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Running Tests

Use this command from the project root:

```powershell
python -m pytest tests -q -p no:cacheprovider
```

Current automated coverage includes:

- health check
- customer creation and listing
- account creation
- account listing by customer
- duplicate customer rejection
- deposit
- insufficient-balance withdrawal rejection
- transfer between accounts
- transaction history

## API Endpoints

### Health

- `GET /health`

### Customers

- `POST /customers`
- `GET /customers`
- `GET /customers/{customer_id}`
- `GET /customers/{customer_id}/accounts`

Example request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9999999999"
}
```

### Accounts

- `POST /accounts`
- `GET /accounts/{account_id}`

Example request:

```json
{
  "customer_id": 1,
  "account_type": "SAVINGS"
}
```

### Transactions

- `POST /deposit`
- `POST /withdraw`
- `POST /transfer`
- `GET /transactions/{account_id}`

Deposit example:

```json
{
  "account_id": 1,
  "amount": 500
}
```

Withdraw example:

```json
{
  "account_id": 1,
  "amount": 100
}
```

Transfer example:

```json
{
  "from_account": 1,
  "to_account": 2,
  "amount": 200
}
```

## Example Workflow

1. Create a customer
2. Create an account for that customer
3. Deposit money into the account
4. Withdraw or transfer money
5. Check transaction history

## Assumptions

- This is a backend-only project
- Authentication and authorization are intentionally out of scope
- SQLite is used for local simplicity, not production scale
- Balances are stored directly on the account model for the first version

## Future Improvements

- Add a ledger-entry model for stronger auditability
- Add database migrations with Alembic
- Add richer test coverage for edge cases
- Add Docker support
- Add centralized log sinks or structured JSON logging
