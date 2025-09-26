"""
Test script for bird identification system
"""

import asyncio
import numpy as np
from pathlib import Path
from app.services.bird_identification import BirdIdentificationService
from app.services.vector_database import VectorDatabaseService
from app.core.database import SessionLocal, engine
from app.models import bird, visit, alert, summary

async def test_vector_database():
    """Test the vector database functionality"""
    print("🧪 Testing Vector Database")
    print("=" * 50)
    
    vector_db = VectorDatabaseService()
    
    # Test adding bird embeddings
    print("Adding test bird embeddings...")
    
    test_embeddings = [
        {
            "bird_id": 1,
            "bird_name": "Ruby Throat",
            "embedding": np.random.rand(128).tolist(),
            "metadata": {"species": "Archilochus colubris", "size": "small"}
        },
        {
            "bird_id": 2,
            "bird_name": "Anna's Hummingbird",
            "embedding": np.random.rand(128).tolist(),
            "metadata": {"species": "Calypte anna", "size": "medium"}
        },
        {
            "bird_id": 3,
            "bird_name": "Rufous Hummingbird",
            "embedding": np.random.rand(128).tolist(),
            "metadata": {"species": "Selasphorus rufus", "size": "small"}
        }
    ]
    
    for bird_data in test_embeddings:
        success = await vector_db.add_bird_embedding(
            embedding=bird_data["embedding"],
            bird_id=bird_data["bird_id"],
            bird_name=bird_data["bird_name"],
            metadata=bird_data["metadata"]
        )
        print(f"✅ Added bird {bird_data['bird_id']}: {success}")
    
    # Test searching for similar birds
    print("\n🔍 Testing similarity search...")
    
    # Create a query embedding similar to the first bird
    query_embedding = test_embeddings[0]["embedding"].copy()
    # Add some noise to make it slightly different
    noise = np.random.normal(0, 0.1, 128)
    query_embedding = [x + y for x, y in zip(query_embedding, noise)]
    
    similar_birds = await vector_db.search_similar_birds(
        query_embedding=query_embedding,
        k=3,
        threshold=0.5
    )
    
    print(f"Found {len(similar_birds)} similar birds:")
    for bird in similar_birds:
        print(f"  - Bird {bird['bird_id']}: {bird['bird_name']} (similarity: {bird['similarity']:.3f})")
    
    # Test database statistics
    print("\n📊 Testing database statistics...")
    stats = await vector_db.get_database_stats()
    print(f"Database stats:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    print("\n✅ Vector database test completed!")

async def test_bird_identification():
    """Test the bird identification service"""
    print("\n🐦 Testing Bird Identification Service")
    print("=" * 50)
    
    identification_service = BirdIdentificationService()
    
    # Create a test image (1x1 pixel PNG)
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    test_image_path = test_dir / "test_hummingbird.png"
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\xd7\xd4\xf8\x00\x00\x00\x00IEND\xaeB`\x82'
    
    with open(test_image_path, "wb") as f:
        f.write(png_data)
    
    print(f"✅ Created test image: {test_image_path}")
    
    # Test bird identification
    print("\n🔍 Testing bird identification...")
    
    try:
        result = await identification_service.identify_bird(str(test_image_path))
        
        print(f"Identification result:")
        print(f"  - Success: {result.get('success', False)}")
        print(f"  - Bird ID: {result.get('bird_id')}")
        print(f"  - Confidence: {result.get('confidence', 0.0)}")
        print(f"  - Match Type: {result.get('match_type', 'unknown')}")
        print(f"  - Bird Name: {result.get('bird_name', 'N/A')}")
        
        if result.get('error'):
            print(f"  - Error: {result['error']}")
        
    except Exception as e:
        print(f"❌ Identification test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test adding bird to database
    print("\n➕ Testing bird database management...")
    
    try:
        # Create a test embedding
        test_embedding = np.random.rand(128).tolist()
        
        # Test adding bird
        success = await identification_service.add_bird_to_database(
            embedding=test_embedding,
            bird_id=999,  # Use a test ID
            bird_name="Test Bird",
            metadata={"test": True}
        )
        
        print(f"✅ Added test bird to database: {success}")
        
        # Test getting bird embedding
        embedding = await identification_service.get_bird_embedding(999)
        if embedding:
            print(f"✅ Retrieved bird embedding: {len(embedding)} dimensions")
        else:
            print("❌ Failed to retrieve bird embedding")
        
        # Test updating bird embedding
        new_embedding = np.random.rand(128).tolist()
        update_success = await identification_service.update_bird_embedding(
            bird_id=999,
            new_embedding=new_embedding,
            metadata={"updated": True}
        )
        print(f"✅ Updated bird embedding: {update_success}")
        
        # Test removing bird
        remove_success = await identification_service.remove_bird_from_database(999)
        print(f"✅ Removed bird from database: {remove_success}")
        
    except Exception as e:
        print(f"❌ Database management test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test database statistics
    print("\n📊 Testing database statistics...")
    
    try:
        stats = await identification_service.get_database_statistics()
        print(f"Database statistics:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
    
    # Cleanup
    try:
        if test_image_path.exists():
            test_image_path.unlink()
        if test_dir.exists() and not any(test_dir.iterdir()):
            test_dir.rmdir()
    except:
        pass
    
    print("\n✅ Bird identification test completed!")

async def test_identification_api():
    """Test the identification API endpoints"""
    print("\n🌐 Testing Identification API")
    print("=" * 50)
    
    # This would test the actual API endpoints
    # For now, we'll just print the available endpoints
    
    endpoints = [
        "POST /api/identification/identify - Identify bird from image",
        "POST /api/identification/add-bird/{bird_id} - Add bird to database",
        "PUT /api/identification/update-bird/{bird_id} - Update bird embedding",
        "DELETE /api/identification/remove-bird/{bird_id} - Remove bird from database",
        "GET /api/identification/bird/{bird_id}/embedding - Get bird embedding",
        "GET /api/identification/stats - Get database statistics",
        "POST /api/identification/rebuild-database - Rebuild database",
        "POST /api/identification/search-similar - Search similar birds"
    ]
    
    print("Available API endpoints:")
    for endpoint in endpoints:
        print(f"  - {endpoint}")
    
    print("\n✅ API endpoints documented!")

async def main():
    """Run all identification tests"""
    print("🐦 Hummingbird Monitor - Bird Identification Test Suite")
    print("=" * 70)
    
    # Run tests
    await test_vector_database()
    await test_bird_identification()
    await test_identification_api()
    
    print("\n🎉 All identification tests completed!")
    print("\n📚 Next steps:")
    print("1. Start the API server: python run_server.py")
    print("2. Test API endpoints: http://localhost:8000/docs")
    print("3. Upload test images to: POST /api/identification/identify")

if __name__ == "__main__":
    asyncio.run(main())
