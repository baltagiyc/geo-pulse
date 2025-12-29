"""
Integration test: Test that the graph structure works end-to-end.

This is an integration test because it tests multiple components together:
- Graph creation
- State initialization
- Node execution flow
- State modifications

This is a manual test script, not a pytest test (we'll convert it later).
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.graph.graph import create_audit_graph, create_initial_state


def test_graph_structure():
    """Test that the graph compiles and executes correctly."""
    
    print("🧪 Testing Graph Structure...")
    print("-" * 50)
    
    # 1. Test graph creation
    print("1. Creating graph...")
    try:
        graph = create_audit_graph()
        print("   ✅ Graph created successfully")
    except Exception as e:
        print(f"   ❌ Error creating graph: {e}")
        return
    
    # 2. Test initial state creation
    print("\n2. Creating initial state...")
    try:
        initial_state = create_initial_state(brand="Nike", llm_provider="gpt-4")
        print(f"   ✅ Initial state created")
        print(f"      - brand: {initial_state['brand']}")
        print(f"      - llm_provider: {initial_state['llm_provider']}")
        print(f"      - questions: {initial_state['questions']} (empty, as expected)")
    except Exception as e:
        print(f"   ❌ Error creating initial state: {e}")
        return
    
    # 3. Test graph execution
    print("\n3. Executing graph...")
    try:
        result = graph.invoke(initial_state)
        print("   ✅ Graph executed successfully")
    except Exception as e:
        print(f"   ❌ Error executing graph: {e}")
        return
    
    # 4. Verify state was modified by nodes
    print("\n4. Verifying state modifications...")
    
    # Check questions (should be filled by question_generator_node)
    if result.get("questions"):
        print(f"   ✅ questions filled: {len(result['questions'])} questions")
        print(f"      {result['questions']}")
    else:
        print("   ❌ questions not filled")
    
    # Check search_results (should be initialized by search_executor_node)
    if "search_results" in result:
        print(f"   ✅ search_results initialized: {len(result['search_results'])} entries")
    else:
        print("   ❌ search_results not initialized")
    
    # Check llm_responses (should be initialized by llm_simulator_node)
    if "llm_responses" in result:
        print(f"   ✅ llm_responses initialized: {len(result['llm_responses'])} entries")
    else:
        print("   ❌ llm_responses not initialized")
    
    # Check reputation_score (should be set by response_analyst_node)
    if "reputation_score" in result:
        print(f"   ✅ reputation_score set: {result['reputation_score']}")
    else:
        print("   ❌ reputation_score not set")
    
    print("\n" + "-" * 50)
    print("🎉 Graph structure test completed!")
    print("\nFull result state keys:", list(result.keys()))


if __name__ == "__main__":
    test_graph_structure()

