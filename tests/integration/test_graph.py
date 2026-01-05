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
        initial_state = create_initial_state(brand="Brevo", llm_provider="gpt-4")
        print("   ✅ Initial state created")
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

    # Check search_results (should be filled by search_executor_node)
    if "search_results" in result:
        print(f"   ✅ search_results initialized: {len(result['search_results'])} entries")
        # Show search results if available
        if result["search_results"]:
            print(
                f"      First question results: {len(result['search_results'].get(list(result['search_results'].keys())[0], []))} results"
            )
            # Show first result details
            first_question = list(result["search_results"].keys())[0]
            first_results = result["search_results"][first_question]
            if first_results:
                print(f"      Example result: {first_results[0].get('title', 'N/A')[:50]}...")
    else:
        print("   ❌ search_results not initialized")

    # Check search_errors
    if "search_errors" in result:
        if result["search_errors"]:
            print(f"   ⚠️  search_errors: {len(result['search_errors'])} errors")
            for error in result["search_errors"][:3]:  # Show first 3 errors
                print(f"      - {error[:60]}...")
        else:
            print("   ✅ No search errors")

    # Check llm_responses (should be initialized by llm_simulator_node)
    if "llm_responses" in result:
        print(f"   ✅ llm_responses initialized: {len(result['llm_responses'])} entries")
        if result["llm_responses"]:
            # Show ALL LLM responses with full content
            print("\n   📝 LLM RESPONSES (Full Content):")
            print(f"   {'='*70}")
            for i, (question, response) in enumerate(result["llm_responses"].items(), 1):
                if response:
                    print(f"\n   Question {i}: {question}")
                    print(f"   {'-'*70}")
                    print(f"   LLM: {response.get('llm_name', 'N/A')}")
                    print(f"   Response ({len(response.get('response', ''))} chars):")
                    print(f"   {response.get('response', 'N/A')}")
                    print(f"\n   Sources cited ({len(response.get('sources', []))} URLs):")
                    for j, source in enumerate(response.get("sources", []), 1):
                        print(f"      {j}. {source}")
                    print(f"   {'='*70}")
    else:
        print("   ❌ llm_responses not initialized")

    # Check reputation_score (should be set by response_analyst_node)
    if "reputation_score" in result:
        score = result["reputation_score"]
        print(f"   ✅ reputation_score set: {score:.2f}/1.0")
        if score > 0.0:
            print("      🎉 Analysis completed successfully!")
    else:
        print("   ❌ reputation_score not set")

    # Check recommendations (should be set by response_analyst_node)
    if "recommendations" in result:
        recommendations = result["recommendations"]
        print(f"   ✅ recommendations set: {len(recommendations)} recommendations")
        if recommendations:
            print("\n   💡 RECOMMENDATIONS:")
            print(f"   {'='*70}")
            for i, rec in enumerate(recommendations[:5], 1):  # Show first 5
                priority_emoji = (
                    "🔴" if rec.get("priority") == "high" else "🟡" if rec.get("priority") == "medium" else "🟢"
                )
                print(f"   {i}. {priority_emoji} {rec.get('title', 'N/A')} [{rec.get('priority', 'N/A')} priority]")
                print(f"      {rec.get('description', 'N/A')[:80]}...")
            print(f"   {'='*70}")
    else:
        print("   ❌ recommendations not set")

    print("\n" + "-" * 50)
    print("🎉 Graph structure test completed!")
    print("\nFull result state keys:", list(result.keys()))


if __name__ == "__main__":
    test_graph_structure()
