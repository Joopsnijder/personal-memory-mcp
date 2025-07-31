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


def test_flexible_categorization(temp_storage):
    """Test flexible categorization for new keys"""
    # Test automatic categorization
    temp_storage.store_personal_info("phone_number", "+31612345678")
    temp_storage.store_personal_info("new_project", "AI Coach Platform")
    temp_storage.store_personal_info("core_principle", "Always be helpful")
    
    # Verify they end up in appropriate categories
    personal_info = temp_storage.memory_data["personal_info"]
    
    # Phone should go to basic
    assert "basic" in personal_info
    assert "phone_number" in personal_info["basic"]
    
    # Project should go to innovations  
    assert "innovations" in personal_info
    assert "new_project" in personal_info["innovations"]
    
    # Principle should go to values_insights
    assert "values_insights" in personal_info
    assert "core_principle" in personal_info["values_insights"]


def test_misc_reorganization(temp_storage):
    """Test reorganizing items from misc category"""
    # Add some items that should stay in misc
    temp_storage.store_personal_info("misc.random_item", "stays here")
    temp_storage.store_personal_info("misc.unknown_thing", "also stays")
    
    # Add items that should be categorized
    temp_storage.store_personal_info("misc.email_backup", "test@example.com")
    temp_storage.store_personal_info("misc.ai_tool", "ChatGPT for writing")
    temp_storage.store_personal_info("misc.core_value", "Honesty")
    
    # Run reorganization
    result = temp_storage.reorganize_misc_items()
    
    assert result["status"] == "success"
    assert result["moved"] == 3
    assert result["remaining_in_misc"] == 2
    
    # Verify moves
    personal_info = temp_storage.memory_data["personal_info"]
    assert "email_backup" in personal_info["basic"]
    assert "ai_tool" in personal_info["innovations"]  
    assert "core_value" in personal_info["values_insights"]
    
    # Verify items stayed in misc
    assert "random_item" in personal_info["misc"]
    assert "unknown_thing" in personal_info["misc"]


def test_manual_item_move(temp_storage):
    """Test manually moving items between categories"""
    # Add test item
    temp_storage.store_personal_info("misc.test_item", "test value")
    
    # Move it manually
    result = temp_storage.move_personal_info_item("misc.test_item", "basic.moved_item")
    
    assert result["status"] == "success"
    assert result["value"] == "test value"
    
    # Verify move
    original = temp_storage.get_personal_info("misc.test_item")
    assert original["found"] is False
    
    new_location = temp_storage.get_personal_info("basic.moved_item")
    assert new_location["found"] is True
    assert new_location["value"] == "test value"


def test_interactive_categorization(temp_storage):
    """Test interactive categorization workflow"""
    # Add items that should trigger pending categorization
    temp_storage.store_personal_info("mystery_item", "Unknown category")
    temp_storage.store_personal_info("unclear_thing", "Needs categorization")
    
    # Check pending items
    pending = temp_storage.get_pending_categorization()
    assert pending["status"] == "success"
    assert pending["count"] == 2
    assert len(pending["pending_items"]) == 2
    
    # Verify pending item structure
    first_item = pending["pending_items"][0] 
    assert "key" in first_item
    assert "value" in first_item
    assert "timestamp" in first_item
    assert "suggested_category" in first_item
    assert "existing_categories" in first_item
    
    # Categorize one item
    result = temp_storage.categorize_pending_item("mystery_item", "personal")
    assert result["status"] == "success"
    assert result["remaining_pending"] == 1
    
    # Verify item was moved
    moved_item = temp_storage.get_personal_info("personal.mystery_item")
    assert moved_item["found"] is True
    assert moved_item["value"] == "Unknown category"
    
    # Verify it's no longer in misc
    misc_item = temp_storage.get_personal_info("misc.mystery_item")
    assert misc_item["found"] is False
    
    # Check updated pending list
    updated_pending = temp_storage.get_pending_categorization()
    assert updated_pending["count"] == 1
    
    # Clear remaining pending items
    clear_result = temp_storage.clear_pending_categorization()
    assert clear_result["status"] == "success"
    assert clear_result["cleared"] == 1
    
    # Verify no more pending items
    final_pending = temp_storage.get_pending_categorization()
    assert final_pending["count"] == 0
