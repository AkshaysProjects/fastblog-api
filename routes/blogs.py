from typing import List, Optional
from bson import ObjectId

from fastapi import APIRouter, HTTPException, status, Depends

from auth import UserDependency
from dependencies import DatabaseDependency
from models import Blog, User

# Create a router for the blogs
router = APIRouter(prefix="/blogs", tags=["blogs"])


# Endpoint to create a new blog
@router.post("/", summary="Create a new blog", response_description="Blog created successfully")
async def create_blog(db: DatabaseDependency, blog: Blog, user: UserDependency):
    """
    Endpoint to create a new blog.
    """
    # Get the collection
    collection = db.get_collection('Blogs')

    # Add author information
    blog_dict = blog.dict()
    blog_dict["author"] = user.username

    # Insert the blog into the database
    result = collection.insert_one(blog_dict)
    return {"message": "Blog created successfully", "blog_id": str(result.inserted_id)}


# Endpoint to retrieve all blogs with pagination
@router.get("/", summary="Retrieve all blogs with pagination", response_description="List of blogs retrieved successfully")
async def get_all_blogs(db: DatabaseDependency, page: int = 1, limit: int = 10):
    """
    Endpoint to retrieve all blogs with pagination.
    """
    # Calculate skip value for pagination
    skip = (page - 1) * limit

    # Get the collection
    collection = db.get_collection('Blogs')

    # Retrieve all blogs
    blogs_cursor = collection.find().skip(skip).limit(limit)

    # Convert cursor to list of dictionaries
    blogs = []
    for blog in blogs_cursor:
        # Convert ObjectId to string for serialization
        blog['_id'] = str(blog['_id'])
        blogs.append(blog)

    return blogs


# Endpoint to retrieve a specific blog by ID
@router.get("/{blog_id}", summary="Retrieve a specific blog by ID", response_description="Blog retrieved successfully")
async def get_blog_by_id(db: DatabaseDependency, blog_id: str):
    """
    Endpoint to retrieve a specific blog by ID.
    """
    # Get the collection
    collection = db.get_collection('Blogs')

    # Retrieve the blog by ID
    blog = collection.find_one({"_id": ObjectId(blog_id)})
    if blog:
        return blog
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )


# Endpoint to update an existing blog
@router.put("/{blog_id}", summary="Update existing blog", response_description="Blog updated successfully")
async def update_blog(db: DatabaseDependency, blog_id: str, blog: Blog, user: UserDependency):
    """
    Endpoint to update an existing blog.
    """
    # Get the collection
    collection = db.get_collection('Blogs')

    # Check if the blog exists
    if collection.find_one({"_id": ObjectId(blog_id)}):
        # Check if the current user is the author of the blog
        if collection.find_one({"_id": ObjectId(blog_id), "author": user.username}):
            # Update the blog
            collection.update_one({"_id": ObjectId(blog_id)}, {
                                  "$set": blog.dict()})
            return {"message": "Blog updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to update this blog",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )


# Endpoint to delete a blog
@router.delete("/{blog_id}", summary="Delete blog", response_description="Blog deleted successfully")
async def delete_blog(db: DatabaseDependency, blog_id: str, user: UserDependency):
    """
    Endpoint to delete a blog.
    """
    # Get the collection
    collection = db.get_collection('Blogs')

    # Check if the blog exists
    if collection.find_one({"_id": ObjectId(blog_id)}):
        # Check if the current user is the author of the blog or an admin
        if user.role == "admin" or collection.find_one({"_id": ObjectId(blog_id), "author": user.username}):
            # Delete the blog
            collection.delete_one({"_id": ObjectId(blog_id)})
            return {"message": "Blog deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to delete this blog",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )
