from fastapi import FastAPI
from routes.users import router as users_router
from routes.blogs import router as blogs_router
from routes.dashboard import router as dashboard_router

# Create an instance of the FastAPI class
app = FastAPI()

# Include the users_router in the app
app.include_router(users_router)

# Include the blogs_router in the app
app.include_router(blogs_router)

# Include the dashboard_router in the app
app.include_router(dashboard_router)
