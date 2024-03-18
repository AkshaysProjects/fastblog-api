# Import necessary modules and classes
from fastapi import APIRouter, HTTPException
from typing import List

# Import dependencies
from auth import UserDependency
from dependencies import DatabaseDependency

# Create API router instance for dashboard
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Define endpoint to retrieve blogs based on user's interests


@router.get("/", summary="Retrieve blogs with tags user is interested in", response_description="List of blogs retrieved successfully")
async def get_dashboard_blogs(db: DatabaseDependency, user: UserDependency, page: int = 1, limit: int = 10) -> List[dict]:
    """
    Retrieve paginated blogs from the database based on user's interests.
    """
    # Calculate skip value for pagination
    skip = (page - 1) * limit

    # Get collection from database
    collection = db.get_collection('Blogs')

    # Construct MongoDB aggregation pipeline for querying blogs
    pipeline = [
        {
            "$match": {
                "tags": {"$in": user.tags}
            }
        },
        {
            "$addFields": {  # Project the count of common tags
                "commonTagsCount": {
                    "$size": {
                        "$setIntersection": ["$tags", user.tags]
                    }
                }
            }
        },
        {
            "$sort": {  # Sort in descending order of common tags count
                "commonTagsCount": -1
            }
        },
        {"$skip": skip},
        {"$limit": limit}
    ]

    # Fetch paginated blogs from the database
    paginated_blogs = collection.aggregate(pipeline)

    # Convert MongoDB cursor to a list of dictionaries
    paginated_blogs_list = [blog for blog in paginated_blogs]

    # If no blogs found, raise HTTPException
    if not paginated_blogs_list:
        raise HTTPException(status_code=404, detail="No blogs found")

    return paginated_blogs_list
