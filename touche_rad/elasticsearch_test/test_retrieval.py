from function import search_by_text, search_by_support, search_by_attack, search_all
import json


def test_retrieval():
    # Example query
    query = "Should we ban social media for children under 16?"

    print("\n=== Testing Text Similarity Search ===")
    text_results = search_by_text(query, k=3)
    print(f"Found {len(text_results)} similar arguments:")
    for i, result in enumerate(text_results, 1):
        print(f"\nResult {i}:")
        print(json.dumps(result, indent=2))

    print("\n=== Testing Supporting Arguments Search ===")
    support_results = search_by_support(query, k=3)
    print(f"Found {len(support_results)} supporting arguments:")
    for i, result in enumerate(support_results, 1):
        print(f"\nResult {i}:")
        print(json.dumps(result, indent=2))

    print("\n=== Testing Attacking Arguments Search ===")
    attack_results = search_by_attack(query, k=3)
    print(f"Found {len(attack_results)} attacking arguments:")
    for i, result in enumerate(attack_results, 1):
        print(f"\nResult {i}:")
        print(json.dumps(result, indent=2))

    print("\n=== Testing Combined Search ===")
    all_results = search_all(query, k=2)
    print("Combined results summary:")
    print(f"Text similarity matches: {len(all_results['text_similarity'])}")
    print(f"Supporting arguments: {len(all_results['supporting'])}")
    print(f"Attacking arguments: {len(all_results['attacking'])}")


if __name__ == "__main__":
    test_retrieval()
