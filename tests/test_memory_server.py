import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to Python path to import memory_server module
sys.path.insert(0, str(Path(__file__).parent.parent))
from memory_server import PersonalMemoryStorage


@pytest.fixture
def temp_storage():
    """Create a temporary storage file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_file = f.name

    storage = PersonalMemoryStorage(temp_file)
    yield storage

    # Cleanup
    Path(temp_file).unlink(missing_ok=True)


def test_store_and_get_personal_info(temp_storage):
    """Test storing and retrieving personal information"""
    result = temp_storage.store_personal_info("name", "John Doe")
    assert result["status"] == "success"

    retrieved = temp_storage.get_personal_info("name")
    assert retrieved["value"] == "John Doe"
    assert retrieved["found"] is True


def test_preferences(temp_storage):
    """Test preference storage and retrieval"""
    result = temp_storage.store_preference("food", "coffee", "cappuccino")
    assert result["status"] == "success"

    prefs = temp_storage.get_preferences("food")
    assert prefs["preferences"]["coffee"] == "cappuccino"


def test_memories(temp_storage):
    """Test memory storage and search"""
    result = temp_storage.add_memory("Had a great meeting today", ["work", "meeting"], "Office")
    assert result["status"] == "success"

    search_results = temp_storage.search_memories(query="meeting")
    assert len(search_results["memories"]) == 1
    assert "meeting" in search_results["memories"][0]["content"]


def test_goals(temp_storage):
    """Test goal management"""
    result = temp_storage.add_goal("Learn Spanish", "personal", "2024-12-31")
    assert result["status"] == "success"
    goal_id = result["goal_id"]

    goals = temp_storage.get_goals(status="active")
    assert len(goals["goals"]) == 1

    update_result = temp_storage.update_goal_status(goal_id, "completed")
    assert update_result["status"] == "success"


def test_hierarchical_personal_info(temp_storage):
    """Test hierarchical personal info storage and retrieval"""
    # Test dot notation storage
    result = temp_storage.store_personal_info("basic.name", "Jane Smith")
    assert result["status"] == "success"
    
    result = temp_storage.store_personal_info("book.title", "Test Book")
    assert result["status"] == "success"
    
    result = temp_storage.store_personal_info("innovations.formula_ai.concept", "AI Racing Game")
    assert result["status"] == "success"
    
    # Test hierarchical retrieval
    retrieved = temp_storage.get_personal_info("basic.name")
    assert retrieved["value"] == "Jane Smith"
    assert retrieved["found"] is True
    
    retrieved = temp_storage.get_personal_info("book.title")
    assert retrieved["value"] == "Test Book"
    assert retrieved["found"] is True
    
    retrieved = temp_storage.get_personal_info("innovations.formula_ai.concept")
    assert retrieved["value"] == "AI Racing Game"
    assert retrieved["found"] is True


def test_backward_compatibility(temp_storage):
    """Test backward compatibility with flat keys"""
    # Store using hierarchical structure
    temp_storage.store_personal_info("basic.name", "John Doe")
    temp_storage.store_personal_info("book.title", "My Book")
    
    # Retrieve using legacy flat keys should still work
    retrieved = temp_storage.get_personal_info("name")
    assert retrieved["value"] == "John Doe"
    assert retrieved["found"] is True
    
    # Store using legacy flat key
    result = temp_storage.store_personal_info("book_author", "Test Author")
    assert result["status"] == "success"
    
    # Should be retrievable both ways
    retrieved = temp_storage.get_personal_info("book_author")
    assert retrieved["value"] == "Test Author" 
    assert retrieved["found"] is True
    
    retrieved = temp_storage.get_personal_info("book.author")
    assert retrieved["value"] == "Test Author"
    assert retrieved["found"] is True


def test_migration_functionality(temp_storage):
    """Test that migration doesn't run on already hierarchical data"""
    # Create hierarchical structure
    temp_storage.store_personal_info("basic.name", "Test User")
    temp_storage.store_personal_info("book.title", "Test Book")
    
    # Verify structure is hierarchical
    personal_info = temp_storage.memory_data["personal_info"]
    assert "basic" in personal_info
    assert isinstance(personal_info["basic"], dict)
    assert personal_info["basic"]["name"] == "Test User"
    
    assert "book" in personal_info  
    assert isinstance(personal_info["book"], dict)
    assert personal_info["book"]["title"] == "Test Book"
