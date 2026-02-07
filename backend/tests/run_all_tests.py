"""
Master test runner for all RAG system tests
Runs all test suites and generates a diagnostic report
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_course_search_tool import run_all_tests as run_search_tool_tests
from test_ai_generator import run_all_tests as run_ai_generator_tests
from test_rag_integration import run_all_tests as run_integration_tests


def main():
    """Run all test suites and generate diagnostic report"""

    print("\n" + "="*70)
    print(" RAG CHATBOT DIAGNOSTIC TEST SUITE")
    print(" Testing all components to identify 'query failed' root cause")
    print("="*70 + "\n")

    total_passed = 0
    total_failed = 0

    # Run test suites
    print("\n[SUITE 1/3] CourseSearchTool Tests")
    print("-" * 70)
    passed, failed = run_search_tool_tests()
    total_passed += passed
    total_failed += failed

    print("\n\n[SUITE 2/3] AIGenerator Tool Calling Tests")
    print("-" * 70)
    passed, failed = run_ai_generator_tests()
    total_passed += passed
    total_failed += failed

    print("\n\n[SUITE 3/3] RAG Integration Tests")
    print("-" * 70)
    passed, failed = run_integration_tests()
    total_passed += passed
    total_failed += failed

    # Final report
    print("\n\n" + "="*70)
    print(" FINAL DIAGNOSTIC REPORT")
    print("="*70)
    print(f"\nTotal Tests Run: {total_passed + total_failed}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")

    if total_failed == 0:
        print("\n🎉 All tests passed! System is working correctly.")
    else:
        print("\n⚠️  ISSUES DETECTED - See failures above for details")
        print("\n🔍 LIKELY ROOT CAUSE:")
        print("   • MAX_RESULTS = 0 in backend/config.py (line 21)")
        print("   • This causes vector store to return 0 results for all searches")
        print("   • Results in 'No relevant content found' for every query")
        print("\n💡 RECOMMENDED FIX:")
        print("   Change config.py line 21 from:")
        print("      MAX_RESULTS: int = 0")
        print("   To:")
        print("      MAX_RESULTS: int = 5")

    print("\n" + "="*70 + "\n")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
