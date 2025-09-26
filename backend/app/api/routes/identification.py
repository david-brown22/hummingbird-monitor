"""
Bird identification API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.services.bird_identification import BirdIdentificationService
from app.schemas.identification import (
    IdentificationResponse, 
    BirdEmbeddingResponse,
    DatabaseStatsResponse,
    SimilarBirdsResponse
)

router = APIRouter()

@router.post("/identify", response_model=IdentificationResponse)
async def identify_bird(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Identify a bird from an uploaded image
    
    Args:
        file: Uploaded image file
        db: Database session
        
    Returns:
        IdentificationResponse with identification results
    """
    try:
        # Save uploaded file
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = f"uploads/{filename}"
        
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process identification
        identification_service = BirdIdentificationService()
        result = await identification_service.identify_bird(file_path)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        if not result.get("bird_id"):
            return {
                "success": True,
                "bird_id": None,
                "confidence": result.get("confidence", 0.0),
                "match_type": "new_bird",
                "bird_name": None,
                "similarity_score": 0.0,
                "message": "No matching bird found - this appears to be a new bird"
            }
        
        return {
            "success": True,
            "bird_id": result["bird_id"],
            "confidence": result["confidence"],
            "match_type": result.get("match_type", "existing_bird"),
            "bird_name": result.get("bird_name"),
            "similarity_score": result.get("similarity_score", 0.0),
            "message": f"Identified as {result.get('bird_name', 'Unknown Bird')}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error identifying bird: {str(e)}")

@router.post("/add-bird/{bird_id}")
async def add_bird_to_identification(
    bird_id: int,
    embedding: List[float],
    bird_name: Optional[str] = None,
    metadata: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Add a bird to the identification database
    
    Args:
        bird_id: Database ID of the bird
        embedding: Bird embedding vector
        bird_name: Optional name for the bird
        metadata: Optional metadata (JSON string)
        db: Database session
        
    Returns:
        Success status
    """
    try:
        # Parse metadata if provided
        metadata_dict = None
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Add to identification database
        identification_service = BirdIdentificationService()
        success = await identification_service.add_bird_to_database(
            embedding=embedding,
            bird_id=bird_id,
            bird_name=bird_name,
            metadata=metadata_dict,
            db=db
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add bird to identification database")
        
        return {
            "success": True,
            "message": f"Bird {bird_id} added to identification database"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding bird: {str(e)}")

@router.put("/update-bird/{bird_id}")
async def update_bird_embedding(
    bird_id: int,
    new_embedding: List[float],
    metadata: Optional[str] = None
):
    """
    Update embedding for an existing bird
    
    Args:
        bird_id: Database ID of the bird
        new_embedding: New embedding vector
        metadata: Optional metadata (JSON string)
        
    Returns:
        Success status
    """
    try:
        # Parse metadata if provided
        metadata_dict = None
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Update bird embedding
        identification_service = BirdIdentificationService()
        success = await identification_service.update_bird_embedding(
            bird_id=bird_id,
            new_embedding=new_embedding,
            metadata=metadata_dict
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update bird embedding")
        
        return {
            "success": True,
            "message": f"Bird {bird_id} embedding updated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating bird: {str(e)}")

@router.delete("/remove-bird/{bird_id}")
async def remove_bird_from_identification(bird_id: int):
    """
    Remove a bird from the identification database
    
    Args:
        bird_id: Database ID of the bird
        
    Returns:
        Success status
    """
    try:
        identification_service = BirdIdentificationService()
        success = await identification_service.remove_bird_from_database(bird_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to remove bird from identification database")
        
        return {
            "success": True,
            "message": f"Bird {bird_id} removed from identification database"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing bird: {str(e)}")

@router.get("/bird/{bird_id}/embedding", response_model=BirdEmbeddingResponse)
async def get_bird_embedding(bird_id: int):
    """
    Get embedding for a specific bird
    
    Args:
        bird_id: Database ID of the bird
        
    Returns:
        BirdEmbeddingResponse with embedding data
    """
    try:
        identification_service = BirdIdentificationService()
        embedding = await identification_service.get_bird_embedding(bird_id)
        
        if embedding is None:
            raise HTTPException(status_code=404, detail="Bird embedding not found")
        
        return {
            "bird_id": bird_id,
            "embedding": embedding,
            "dimension": len(embedding)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bird embedding: {str(e)}")

@router.get("/stats", response_model=DatabaseStatsResponse)
async def get_database_statistics():
    """
    Get statistics about the identification database
    
    Returns:
        DatabaseStatsResponse with database statistics
    """
    try:
        identification_service = BirdIdentificationService()
        stats = await identification_service.get_database_statistics()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@router.post("/rebuild-database")
async def rebuild_identification_database():
    """
    Rebuild the entire identification database
    
    Returns:
        Success status
    """
    try:
        identification_service = BirdIdentificationService()
        success = await identification_service.rebuild_identification_database()
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to rebuild database")
        
        return {
            "success": True,
            "message": "Identification database rebuilt successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebuilding database: {str(e)}")

@router.post("/search-similar")
async def search_similar_birds(
    embedding: List[float],
    k: int = 5,
    threshold: float = 0.7
):
    """
    Search for similar birds using an embedding
    
    Args:
        embedding: Query embedding vector
        k: Number of results to return
        threshold: Similarity threshold
        
    Returns:
        List of similar birds
    """
    try:
        from app.services.vector_database import VectorDatabaseService
        
        vector_db = VectorDatabaseService()
        similar_birds = await vector_db.search_similar_birds(
            query_embedding=embedding,
            k=k,
            threshold=threshold
        )
        
        return {
            "success": True,
            "similar_birds": similar_birds,
            "count": len(similar_birds)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching similar birds: {str(e)}")
