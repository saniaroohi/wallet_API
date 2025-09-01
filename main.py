from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

app = FastAPI(title="Wallet API", description="User Wallet Management", version="1.0")

# ---------------------------
# Models
# ---------------------------
class User(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    balance: float = 0.0

class Transaction(BaseModel):
    user_id: int
    amount: float
    type: str  # "deposit" or "withdraw"
    timestamp: datetime

class UpdateWalletRequest(BaseModel):
    amount: float
    type: str  # "deposit" or "withdraw"

# ---------------------------
# In-Memory Database
# ---------------------------
users: Dict[int, User] = {}
transactions: List[Transaction] = []

# Preloaded Users (for testing)
users[1] = User(id=1, name="Alice", email="alice@example.com", phone="1234567890", balance=100.0)
users[2] = User(id=2, name="Bob", email="bob@example.com", phone="9876543210", balance=200.0)

# ---------------------------
# APIs
# ---------------------------

@app.get("/users", response_model=List[User])
def list_users():
    """Fetch all users with wallet balance"""
    return list(users.values())

@app.post("/wallet/{user_id}")
def update_wallet(user_id: int, request: UpdateWalletRequest):
    """Add or update an amount in user's wallet"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    if request.type == "deposit":
        users[user_id].balance += request.amount
    elif request.type == "withdraw":
        if users[user_id].balance < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        users[user_id].balance -= request.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # Record the transaction
    transactions.append(Transaction(
        user_id=user_id,
        amount=request.amount,
        type=request.type,
        timestamp=datetime.now()
    ))

    return {"message": f"Wallet updated successfully for user {user_id}", "balance": users[user_id].balance}

@app.get("/transactions/{user_id}", response_model=List[Transaction])
def fetch_transactions(user_id: int):
    """Fetch all transactions for a specific user"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    user_transactions = [t for t in transactions if t.user_id == user_id]
    return user_transactions
