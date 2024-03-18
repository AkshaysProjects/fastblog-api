from fastapi import FastAPI
from routes.users import router as users_router

# Create an instance of the FastAPI class
app = FastAPI()

# Define a function that will be called when the user visits the root URL
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Include the users_router in the app
app.include_router(users_router)