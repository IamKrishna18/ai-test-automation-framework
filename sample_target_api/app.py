import json
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Sample Target API",
    description="A predictable test API for the AI Test Automation Framework",
    version="1.0.0",
)

# --- Mock Data ---
USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35},
]

PRODUCTS = [
    {"id": 1, "name": "Widget", "price": 9.99, "in_stock": True},
    {"id": 2, "name": "Gadget", "price": 24.99, "in_stock": False},
]

# --- Models ---
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: str
    age: int

class UserResponse(UserCreate):
    id: int

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool

# --- User Endpoints ---

@app.get("/users", response_model=List[UserResponse])
def get_users(limit: Optional[int] = Query(None, description="Limit the number of results")):
    """List all users."""
    if limit is not None and limit > 0:
        return USERS[:limit]
    return USERS

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int = Path(..., description="The ID of the user")):
    """Get a specific user by ID."""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if user_id >= 1000:
        # Simulate a server error for testing
        raise HTTPException(status_code=500, detail="Internal server error")
        
    for user in USERS:
        if user["id"] == user_id:
            return user
            
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Create a new user."""
    if not user.name.strip():
        raise HTTPException(status_code=422, detail="Name cannot be empty")
    
    if user.age < 0 or user.age > 150:
        raise HTTPException(status_code=400, detail="Age must be between 0 and 150")
        
    if "@" not in user.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
        
    new_user = user.model_dump()
    new_user["id"] = 4  # Predictable ID for testing
    return new_user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate):
    """Update an existing user."""
    if user_id not in [1, 2, 3]:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.name.strip():
        raise HTTPException(status_code=422, detail="Name cannot be empty")
    
    if user.age < 0 or user.age > 150:
        raise HTTPException(status_code=400, detail="Age must be between 0 and 150")
        
    if "@" not in user.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
        
    updated = user.model_dump()
    updated["id"] = user_id
    return updated

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """Delete a user."""
    if user_id not in [1, 2, 3]:
        raise HTTPException(status_code=404, detail="User not found")
    return None

# --- Product Endpoints ---

@app.get("/products", response_model=List[ProductResponse])
def get_products():
    """List all products."""
    return PRODUCTS

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    """Get a specific product by ID."""
    if product_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    if product_id >= 1000:
        raise HTTPException(status_code=500, detail="Internal server error")
        
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
            
    raise HTTPException(status_code=404, detail="Product not found")

# --- Health Endpoint ---

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
