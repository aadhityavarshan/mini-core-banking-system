from pathlib import Path

from fastapi.testclient import TestClient

from app.database.db import engine
from app.main import app


DB_PATH = Path("data") / "banking.db"


def reset_database() -> None:
    engine.dispose()
    if DB_PATH.exists():
        DB_PATH.unlink()


def test_health_check() -> None:
    reset_database()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_customer_and_list_customers() -> None:
    reset_database()

    with TestClient(app) as client:
        create_response = client.post(
            "/customers",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9999999999",
            },
        )
        list_response = client.get("/customers")

    assert create_response.status_code == 201
    assert create_response.json()["customer_id"] == 1
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_create_account_for_existing_customer() -> None:
    reset_database()

    with TestClient(app) as client:
        client.post(
            "/customers",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9999999999",
            },
        )
        account_response = client.post(
            "/accounts",
            json={"customer_id": 1, "account_type": "SAVINGS"},
        )

    assert account_response.status_code == 201
    assert account_response.json()["balance"] == "0.00"


def test_create_account_for_missing_customer_returns_404() -> None:
    reset_database()

    with TestClient(app) as client:
        response = client.post(
            "/accounts",
            json={"customer_id": 999, "account_type": "SAVINGS"},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}


def test_duplicate_customer_returns_409() -> None:
    reset_database()

    with TestClient(app) as client:
        client.post(
            "/customers",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9999999999",
            },
        )
        duplicate_response = client.post(
            "/customers",
            json={
                "name": "Jane Doe",
                "email": "john@example.com",
                "phone": "8888888888",
            },
        )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": "Customer with this email or phone already exists"
    }


def test_list_accounts_for_customer() -> None:
    reset_database()

    with TestClient(app) as client:
        client.post(
            "/customers",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9999999999",
            },
        )
        client.post("/accounts", json={"customer_id": 1, "account_type": "SAVINGS"})
        client.post("/accounts", json={"customer_id": 1, "account_type": "CURRENT"})
        response = client.get("/customers/1/accounts")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["customer_id"] == 1
    assert payload[1]["customer_id"] == 1


def test_list_accounts_for_missing_customer_returns_404() -> None:
    reset_database()

    with TestClient(app) as client:
        response = client.get("/customers/999/accounts")

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}


def test_deposit_updates_balance() -> None:
    reset_database()

    with TestClient(app) as client:
        client.post(
            "/customers",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9999999999",
            },
        )
        client.post(
            "/accounts",
            json={"customer_id": 1, "account_type": "SAVINGS"},
        )
        deposit_response = client.post(
            "/deposit",
            json={"account_id": 1, "amount": 500},
        )

    assert deposit_response.status_code == 200
    assert deposit_response.json()["status"] == "success"
    assert deposit_response.json()["balance"] == "500.00"


def test_withdraw_rejects_insufficient_balance() -> None:
    reset_database()

    with TestClient(app) as client:
        client.post(
            "/customers",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9999999999",
            },
        )
        client.post(
            "/accounts",
            json={"customer_id": 1, "account_type": "SAVINGS"},
        )
        withdraw_response = client.post(
            "/withdraw",
            json={"account_id": 1, "amount": 100},
        )

    assert withdraw_response.status_code == 400
    assert withdraw_response.json() == {"detail": "Insufficient balance"}


def test_transfer_moves_money_between_accounts() -> None:
    reset_database()

    with TestClient(app) as client:
        client.post(
            "/customers",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9999999999",
            },
        )
        client.post(
            "/customers",
            json={
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "8888888888",
            },
        )
        client.post("/accounts", json={"customer_id": 1, "account_type": "SAVINGS"})
        client.post("/accounts", json={"customer_id": 2, "account_type": "SAVINGS"})
        client.post("/deposit", json={"account_id": 1, "amount": 500})

        transfer_response = client.post(
            "/transfer",
            json={"from_account": 1, "to_account": 2, "amount": 200},
        )
        source_account = client.get("/accounts/1")
        destination_account = client.get("/accounts/2")

    assert transfer_response.status_code == 200
    assert transfer_response.json()["status"] == "success"
    assert source_account.json()["balance"] == "300.00"
    assert destination_account.json()["balance"] == "200.00"


def test_transaction_history_returns_account_activity() -> None:
    reset_database()

    with TestClient(app) as client:
        client.post(
            "/customers",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9999999999",
            },
        )
        client.post(
            "/accounts",
            json={"customer_id": 1, "account_type": "SAVINGS"},
        )
        client.post("/deposit", json={"account_id": 1, "amount": 500})
        client.post("/withdraw", json={"account_id": 1, "amount": 100})
        history_response = client.get("/transactions/1")

    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 2
    assert {entry["transaction_type"] for entry in history} == {"deposit", "withdraw"}
