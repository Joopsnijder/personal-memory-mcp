#!/usr/bin/env python3
"""
Personal Memory MCP Server
A simple MCP server using FastMCP for storing personal information locally.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP


# Storage class for managing personal memory data
class PersonalMemoryStorage:
    def __init__(self, storage_file: str = "/Users/joopsnijder/Library/Mobile Documents/com~apple~CloudDocs/personal-memory/personal_memory.json"):
        self.storage_file = Path(storage_file)
        # Ensure the directory exists
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory_data = self._load_memory()
        # Migrate to hierarchical structure if needed
        self._migrate_personal_info_structure()

    def _load_memory(self) -> Dict[str, Any]:
        """Load memory data from storage file"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return self._initialize_memory()
        return self._initialize_memory()

    def _initialize_memory(self) -> Dict[str, Any]:
        """Initialize empty memory structure"""
        return {
            "personal_info": {},
            "preferences": {},
            "memories": [],
            "relationships": {},
            "goals": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

    def _save_memory(self):
        """Save memory data to storage file"""
        self.memory_data["last_updated"] = datetime.now().isoformat()
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(self.memory_data, f, indent=2, ensure_ascii=False)

    def _migrate_personal_info_structure(self):
        """Migrate flat personal_info structure to hierarchical structure"""
        personal_info = self.memory_data.get("personal_info", {})
        
        # Check if already migrated (has hierarchical structure)
        hierarchical_categories = ["basic", "career", "book", "work_roles", "innovations", "communication", "values_insights"]
        if any(k in hierarchical_categories and isinstance(v, dict) for k, v in personal_info.items()):
            # Already hierarchical, no migration needed
            return
            
        # Create hierarchical structure mapping
        hierarchical_mapping = {
            "basic": [
                "name", "woonplaats", "linkedin_profile", "email_infosupport", "email_aigency"
            ],
            "career": [
                "job_title", "full_job_roles", "career_background", "expertise", 
                "expertise_areas", "research_interests"
            ],
            "book": [
                "book_title", "book_subtitle", "book_isbn", "book_publisher", "book_year",
                "book_edition", "book_format", "book_language", "book_category", 
                "book_summary", "book_learning_outcomes", "book_keywords", 
                "book_managementboek_url", "book_publisher_full", "book_boom_url",
                "book_topics_detailed"
            ],
            "work_roles": [
                "aigency_work", "research_center_focus", "dnb_coaching_role", 
                "edih_advisory_role", "ai_governance_board_role", "raise_program_role"
            ],
            "innovations": [
                "formula_ai_creator", "formula_ai_concept", "formula_ai_goals", 
                "formula_ai_mechanics", "formula_ai_drs_package", "formula_ai_target_audience",
                "ai_experiment_canvas_creator", "ai_experiment_canvas_structure", 
                "ai_ideation_workshop_concept", "ai_design_week_process", "workshop_client_testimonials"
            ],
            "communication": [
                "podcast_details", "writing_style", "communication_preferences", 
                "critical_attitudes", "positive_attitudes", "personal_projects"
            ],
            "values_insights": [
                "core_values", "key_insights", "methods_frameworks"
            ]
        }
        
        # Build new hierarchical structure
        new_structure = {}
        migrated_keys = set()
        
        for category, keys in hierarchical_mapping.items():
            category_data = {}
            for key in keys:
                if key in personal_info:
                    # Handle book keys by removing book_ prefix for cleaner structure
                    if key.startswith("book_"):
                        clean_key = key[5:]  # Remove "book_" prefix
                        category_data[clean_key] = personal_info[key]
                    else:
                        category_data[key] = personal_info[key]
                    migrated_keys.add(key)
            
            if category_data:
                new_structure[category] = category_data
        
        # Handle special cases for innovations subcategories
        if "innovations" in new_structure:
            innovations_data = new_structure["innovations"]
            formula_ai_data = {}
            ai_canvas_data = {}
            
            # Group Formula AI related items
            for key in list(innovations_data.keys()):
                if key.startswith("formula_ai_"):
                    clean_key = key[11:]  # Remove "formula_ai_" prefix
                    formula_ai_data[clean_key] = innovations_data.pop(key)
                elif key.startswith("ai_experiment_canvas_"):
                    clean_key = key[21:]  # Remove "ai_experiment_canvas_" prefix
                    ai_canvas_data[clean_key] = innovations_data.pop(key)
                elif key in ["ai_experiment_canvas_creator"]:
                    ai_canvas_data["creator"] = innovations_data.pop(key)
                elif key in ["formula_ai_creator"]:
                    formula_ai_data["creator"] = innovations_data.pop(key)
            
            # Add other workshop/design related items to ai_canvas
            for key in ["ai_ideation_workshop_concept", "ai_design_week_process", "workshop_client_testimonials"]:
                if key in innovations_data:
                    ai_canvas_data[key] = innovations_data.pop(key)
            
            if formula_ai_data:
                new_structure["innovations"]["formula_ai"] = formula_ai_data
            if ai_canvas_data:
                new_structure["innovations"]["ai_experiment_canvas"] = ai_canvas_data
            
            # Remove empty innovations if no other data
            if not innovations_data and "formula_ai" in new_structure["innovations"] or "ai_experiment_canvas" in new_structure["innovations"]:
                new_structure["innovations"] = {k: v for k, v in new_structure["innovations"].items() if k not in innovations_data}
        
        # Add any remaining unmapped keys to a misc category
        remaining_keys = set(personal_info.keys()) - migrated_keys
        if remaining_keys:
            misc_data = {key: personal_info[key] for key in remaining_keys}
            new_structure["misc"] = misc_data
        
        # Update the personal_info with new structure
        if new_structure:
            self.memory_data["personal_info"] = new_structure
            self._save_memory()
            print(f"Migrated personal_info structure with {len(migrated_keys)} keys organized into {len(new_structure)} categories")

    def _get_hierarchical_value(self, key: str) -> tuple[Any, bool]:
        """Get value from hierarchical structure, supporting both flat and dot notation"""
        personal_info = self.memory_data.get("personal_info", {})
        
        # Check for direct key first (flat access)
        if key in personal_info:
            return personal_info[key], True
            
        # Check for dot notation (e.g., "book.title", "basic.name", "innovations.formula_ai.concept") 
        if "." in key:
            parts = key.split(".")
            current_dict = personal_info
            
            # Navigate through all parts
            for part in parts:
                if isinstance(current_dict, dict) and part in current_dict:
                    current_dict = current_dict[part]
                else:
                    break
            else:
                # Successfully found the value
                return current_dict, True
        
        # Try to find in legacy flat structure by searching all categories
        for category_name, category_data in personal_info.items():
            if isinstance(category_data, dict):
                # Search for legacy keys (e.g., "book_title" -> "title" in book category)
                if key in category_data:
                    return category_data[key], True
                    
                # Search for keys with prefixes removed
                for stored_key, stored_value in category_data.items():
                    if key == f"{category_name}_{stored_key}" or key == f"book_{stored_key}":
                        return stored_value, True
        
        return None, False

    def _set_hierarchical_value(self, key: str, value: Any) -> bool:
        """Set value in hierarchical structure, supporting both flat and dot notation"""
        personal_info = self.memory_data.setdefault("personal_info", {})
        
        # Handle dot notation (e.g., "book.title", "basic.name", "innovations.formula_ai.concept")
        if "." in key:
            parts = key.split(".")
            current_dict = personal_info
            
            # Navigate through all parts except the last one
            for part in parts[:-1]:
                if part not in current_dict:
                    current_dict[part] = {}
                elif not isinstance(current_dict[part], dict):
                    current_dict[part] = {}
                current_dict = current_dict[part]
            
            # Set the final value
            current_dict[parts[-1]] = value
            return True
            
        # Handle legacy flat keys by mapping to appropriate categories
        legacy_mappings = {
            # Basic info
            "name": "basic.name",
            "woonplaats": "basic.woonplaats", 
            "linkedin_profile": "basic.linkedin_profile",
            "email_infosupport": "basic.email_infosupport",
            "email_aigency": "basic.email_aigency",
            
            # Career info
            "job_title": "career.job_title",
            "full_job_roles": "career.full_job_roles",
            "career_background": "career.career_background",
            "expertise": "career.expertise",
            "expertise_areas": "career.expertise_areas", 
            "research_interests": "career.research_interests",
        }
        
        # Map book_ prefixed keys
        if key.startswith("book_"):
            clean_key = key[5:]  # Remove "book_" prefix
            return self._set_hierarchical_value(f"book.{clean_key}", value)
            
        # Map formula_ai_ prefixed keys  
        if key.startswith("formula_ai_"):
            clean_key = key[11:]  # Remove "formula_ai_" prefix
            return self._set_hierarchical_value(f"innovations.formula_ai.{clean_key}", value)
            
        # Map ai_experiment_canvas_ prefixed keys
        if key.startswith("ai_experiment_canvas_"):
            clean_key = key[21:]  # Remove "ai_experiment_canvas_" prefix  
            return self._set_hierarchical_value(f"innovations.ai_experiment_canvas.{clean_key}", value)
        
        # Check legacy mappings
        if key in legacy_mappings:
            return self._set_hierarchical_value(legacy_mappings[key], value)
            
        # For unmapped keys, try to infer category or use misc
        # This allows for flexible addition of new categories
        suggested_category = self._suggest_category_for_key(key)
        if suggested_category:
            return self._set_hierarchical_value(f"{suggested_category}.{key}", value)
            
        # If no suggestion, store in misc category
        if "misc" not in personal_info:
            personal_info["misc"] = {}
        elif not isinstance(personal_info["misc"], dict):
            personal_info["misc"] = {}
            
        personal_info["misc"][key] = value
        return True

    def _suggest_category_for_key(self, key: str) -> str:
        """Suggest appropriate category for a new key based on naming patterns"""
        key_lower = key.lower()
        
        # Basic/contact related
        if any(pattern in key_lower for pattern in ['email', 'phone', 'address', 'contact', 'location']):
            return "basic"
            
        # Career related
        if any(pattern in key_lower for pattern in ['job', 'work', 'career', 'role', 'position', 'company']):
            return "career"
            
        # Book related
        if key_lower.startswith('book_') or any(pattern in key_lower for pattern in ['publication', 'isbn', 'publisher']):
            return "book"
            
        # Innovation/project related  
        if any(pattern in key_lower for pattern in ['project', 'innovation', 'tool', 'framework', 'canvas']):
            return "innovations"
            
        # Communication related
        if any(pattern in key_lower for pattern in ['communication', 'style', 'preference', 'podcast', 'speaking']):
            return "communication"
            
        # Values/insights related
        if any(pattern in key_lower for pattern in ['value', 'insight', 'principle', 'belief', 'method']):
            return "values_insights"
            
        # No clear category suggestion
        return None

    def store_personal_info(self, key: str, value: Any) -> Dict[str, Any]:
        """Store personal information with hierarchical support"""
        success = self._set_hierarchical_value(key, value)
        if success:
            self._save_memory()
            return {"status": "success", "message": f"Stored {key}", "data": {key: value}}
        else:
            return {"status": "error", "message": f"Failed to store {key}"}

    def get_personal_info(self, key: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve personal information with hierarchical support"""
        if key:
            value, found = self._get_hierarchical_value(key)
            return {"key": key, "value": value, "found": found}
        return {"personal_info": self.memory_data.get("personal_info", {})}

    def store_preference(self, category: str, preference: str, value: Any) -> Dict[str, Any]:
        """Store a preference"""
        if category not in self.memory_data["preferences"]:
            self.memory_data["preferences"][category] = {}
        self.memory_data["preferences"][category][preference] = value
        self._save_memory()
        return {
            "status": "success",
            "message": f"Stored preference {category}.{preference}",
        }

    def get_preferences(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve preferences"""
        if category:
            return {
                "category": category,
                "preferences": self.memory_data["preferences"].get(category, {}),
                "found": category in self.memory_data["preferences"],
            }
        return {"preferences": self.memory_data["preferences"]}

    def add_memory(
        self, content: str, tags: List[str] = None, context: str = None
    ) -> Dict[str, Any]:
        """Add a memory entry"""
        memory_entry = {
            "id": len(self.memory_data["memories"]) + 1,
            "content": content,
            "tags": tags or [],
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }
        self.memory_data["memories"].append(memory_entry)
        self._save_memory()
        return {
            "status": "success",
            "memory_id": memory_entry["id"],
            "memory": memory_entry,
        }

    def search_memories(
        self, query: str = None, tags: List[str] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """Search memories by content or tags"""
        results = []
        for memory in self.memory_data["memories"]:
            match = False
            if query and query.lower() in memory["content"].lower():
                match = True
            if tags and any(tag.lower() in [t.lower() for t in memory["tags"]] for tag in tags):
                match = True
            if not query and not tags:  # Return all if no filters
                match = True
            if match:
                results.append(memory)

        # Sort by timestamp (newest first) and limit results
        results = sorted(results, key=lambda x: x["timestamp"], reverse=True)[:limit]
        return {
            "memories": results,
            "count": len(results),
            "total_memories": len(self.memory_data["memories"]),
        }

    def store_relationship(
        self, name: str, relationship_type: str, details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Store information about a relationship"""
        relationship_data = {
            "type": relationship_type,
            "details": details or {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }
        self.memory_data["relationships"][name] = relationship_data
        self._save_memory()
        return {
            "status": "success",
            "message": f"Stored relationship with {name}",
            "relationship": relationship_data,
        }

    def get_relationships(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve relationship information"""
        if name:
            relationship = self.memory_data["relationships"].get(name)
            return {
                "name": name,
                "relationship": relationship,
                "found": relationship is not None,
            }
        return {"relationships": self.memory_data["relationships"]}

    def add_goal(
        self,
        goal: str,
        category: str = "general",
        deadline: str = None,
        priority: str = "medium",
    ) -> Dict[str, Any]:
        """Add a goal"""
        goal_entry = {
            "id": len(self.memory_data["goals"]) + 1,
            "goal": goal,
            "category": category,
            "deadline": deadline,
            "priority": priority,
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        self.memory_data["goals"].append(goal_entry)
        self._save_memory()
        return {"status": "success", "goal_id": goal_entry["id"], "goal": goal_entry}

    def get_goals(self, status: str = None, category: str = None) -> Dict[str, Any]:
        """Retrieve goals with optional filtering"""
        filtered_goals = []
        for goal in self.memory_data["goals"]:
            if status and goal["status"] != status:
                continue
            if category and goal["category"] != category:
                continue
            filtered_goals.append(goal)
        return {"goals": filtered_goals, "count": len(filtered_goals)}

    def update_goal_status(self, goal_id: int, status: str) -> Dict[str, Any]:
        """Update goal status"""
        for goal in self.memory_data["goals"]:
            if goal["id"] == goal_id:
                old_status = goal["status"]
                goal["status"] = status
                goal["updated_at"] = datetime.now().isoformat()
                self._save_memory()
                return {
                    "status": "success",
                    "message": f"Goal {goal_id} status updated from {old_status} to {status}",
                    "goal": goal,
                }
        return {"status": "error", "message": f"Goal {goal_id} not found"}

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memory"""
        goal_stats = {}
        for goal in self.memory_data["goals"]:
            status = goal["status"]
            goal_stats[status] = goal_stats.get(status, 0) + 1

        return {
            "total_personal_info_items": len(self.memory_data["personal_info"]),
            "total_memories": len(self.memory_data["memories"]),
            "total_relationships": len(self.memory_data["relationships"]),
            "total_goals": len(self.memory_data["goals"]),
            "goal_breakdown": goal_stats,
            "preference_categories": len(self.memory_data["preferences"]),
            "created_at": self.memory_data["created_at"],
            "last_updated": self.memory_data["last_updated"],
            "storage_file": str(self.storage_file.absolute()),
        }


# Initialize storage and FastMCP server
storage = PersonalMemoryStorage()
mcp = FastMCP("Personal Memory Server")


@mcp.tool()
def store_personal_info(key: str, value: str) -> dict:
    """Store personal information with a key-value pair"""
    return storage.store_personal_info(key, value)


@mcp.tool()
def get_personal_info(key: str = None) -> dict:
    """Retrieve personal information"""
    return storage.get_personal_info(key)


@mcp.tool()
def store_preference(category: str, preference: str, value: str) -> dict:
    """Store a preference in a specific category (e.g., food, music, work)"""
    return storage.store_preference(category, preference, value)


@mcp.tool()
def get_preferences(category: str = None) -> dict:
    """Retrieve preferences, optionally filtered by category"""
    return storage.get_preferences(category)


@mcp.tool()
def add_memory(content: str, tags: List[str] = None, context: str = None) -> dict:
    """Add a memory entry with optional tags and context"""
    return storage.add_memory(content, tags or [], context)


@mcp.tool()
def search_memories(query: str = None, tags: List[str] = None, limit: int = 10) -> dict:
    """Search memories by content or tags"""
    return storage.search_memories(query, tags, limit)


@mcp.tool()
def store_relationship(name: str, relationship_type: str, details: dict = None) -> dict:
    """Store information about a relationship with someone"""
    return storage.store_relationship(name, relationship_type, details or {})


@mcp.tool()
def get_relationships(name: str = None) -> dict:
    """Retrieve relationship information"""
    return storage.get_relationships(name)


@mcp.tool()
def add_goal(
    goal: str, category: str = "general", deadline: str = None, priority: str = "medium"
) -> dict:
    """Add a personal goal with category and optional deadline"""
    return storage.add_goal(goal, category, deadline, priority)


@mcp.tool()
def get_goals(status: str = None, category: str = None) -> dict:
    """Retrieve goals with optional filtering by status or category"""
    return storage.get_goals(status, category)


@mcp.tool()
def update_goal_status(goal_id: int, status: str) -> dict:
    """Update the status of a goal (active, completed, paused, cancelled)"""
    return storage.update_goal_status(goal_id, status)


@mcp.tool()
def get_memory_stats() -> dict:
    """Get statistics and overview of all stored memory data"""
    return storage.get_memory_stats()


def main():
    """Main function to run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
