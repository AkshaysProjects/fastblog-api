from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI()

# Define a function that will be called when the user visits the root URL
@app.get("/")
def read_root():
    return {"Hello": "World"}