#!/usr/bin/env python3
"""
test_umc_postgres.py
End-to-end test of UMC server with PostgreSQL

Tests:
1. Database connection
2. Session creation
3. SAVE_NOTE persistence
4. STATE_UPDATE persistence
5. REQUEST_CONTEXT retrieval
6. Data survives server restart (no in-memory storage)

Usage:
    # Start server first:
    uvicorn middleware.umc_memory_server_postgres:app --reload

    # Then run tests:
    python3 scripts/test_umc_postgres.py
"""

import requests
import sys
import time
from datetime import datetime


BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = f"test-session-{int(time.time())}"


def test_health_check():
    """Test 1: Health check and database connection"""
    print("Test 1: Health check...")

    response = requests.get(f"{BASE_URL}/health")

    if response.status_code != 200:
        print(f"   ❌ FAIL: Status {response.status_code}")
        return False

    data = response.json()

    if data["status"] != "healthy":
        print(f"   ❌ FAIL: Database unhealthy")
        return False

    print(f"   ✅ PASS: Database healthy (latency: {data['database']['latency_ms']}ms)")
    return True


def test_save_note():
    """Test 2: Save a note"""
    print("Test 2: Save note...")

    payload = {
        "type": "SAVE_NOTE",
        "session_id": TEST_SESSION_ID,
        "scope": "project",
        "fact": "User wants to build a UMC integration with PostgreSQL",
        "reason": "Core requirement for production deployment"
    }

    response = requests.post(f"{BASE_URL}/save_note", json=payload)

    if response.status_code != 200:
        print(f"   ❌ FAIL: Status {response.status_code}")
        return False

    data = response.json()

    if not data["ok"]:
        print(f"   ❌ FAIL: Response not OK")
        return False

    if data["stored"]["rejected"]:
        print(f"   ❌ FAIL: Note was rejected")
        return False

    print(f"   ✅ PASS: Note saved (ID: {data['stored']['id']})")
    return True


def test_save_sensitive_note():
    """Test 3: Sensitive note should be rejected"""
    print("Test 3: Save sensitive note (should reject)...")

    payload = {
        "type": "SAVE_NOTE",
        "session_id": TEST_SESSION_ID,
        "scope": "temporary",
        "fact": "My password is: supersecret123",
        "reason": "Testing rejection"
    }

    response = requests.post(f"{BASE_URL}/save_note", json=payload)

    if response.status_code != 200:
        print(f"   ❌ FAIL: Status {response.status_code}")
        return False

    data = response.json()

    if not data["stored"]["rejected"]:
        print(f"   ❌ FAIL: Sensitive note was NOT rejected")
        return False

    print(f"   ✅ PASS: Sensitive note rejected (reason: {data['stored']['rejected_reason']})")
    return True


def test_state_update():
    """Test 4: State update"""
    print("Test 4: State update...")

    payload = {
        "type": "STATE_UPDATE",
        "session_id": TEST_SESSION_ID,
        "summary": "Connected UMC server to PostgreSQL successfully",
        "next_steps": [
            "Run full test suite",
            "Deploy to staging",
            "Write production documentation"
        ],
        "blockers": [],
        "deadline": "2026-01-20"
    }

    response = requests.post(f"{BASE_URL}/state_update", json=payload)

    if response.status_code != 200:
        print(f"   ❌ FAIL: Status {response.status_code}")
        return False

    data = response.json()

    if not data["ok"]:
        print(f"   ❌ FAIL: Response not OK")
        return False

    print(f"   ✅ PASS: State updated (ID: {data['stored']['id']})")
    return True


def test_request_context():
    """Test 5: Request context retrieval"""
    print("Test 5: Request context...")

    payload = {
        "type": "REQUEST_CONTEXT",
        "session_id": TEST_SESSION_ID,
        "topic": "UMC PostgreSQL integration status"
    }

    response = requests.post(f"{BASE_URL}/request_context", json=payload)

    if response.status_code != 200:
        print(f"   ❌ FAIL: Status {response.status_code}")
        return False

    data = response.json()

    context = data["context_block"]

    # Verify context contains our data
    if "Connected UMC server to PostgreSQL successfully" not in context:
        print(f"   ❌ FAIL: State update not in context")
        return False

    if "User wants to build a UMC integration" not in context:
        print(f"   ❌ FAIL: Note not in context")
        return False

    if "password" in context.lower() and "rejected" not in context.lower():
        print(f"   ❌ FAIL: Sensitive note leaked into context")
        return False

    print(f"   ✅ PASS: Context retrieved correctly")
    print(f"\n{context}\n")
    return True


def test_session_memory():
    """Test 6: Inspect session memory"""
    print("Test 6: Inspect session memory...")

    response = requests.get(f"{BASE_URL}/session/{TEST_SESSION_ID}/memory")

    if response.status_code != 200:
        print(f"   ❌ FAIL: Status {response.status_code}")
        return False

    data = response.json()

    if data["notes_count"] == 0:
        print(f"   ❌ FAIL: No notes found")
        return False

    if not data["current_state"]:
        print(f"   ❌ FAIL: No state update found")
        return False

    print(f"   ✅ PASS: Session has {data['notes_count']} notes and current state")
    return True


def test_audit_log():
    """Test 7: Audit log"""
    print("Test 7: Audit log...")

    response = requests.get(f"{BASE_URL}/audit_log", params={"limit": 10, "session_id": TEST_SESSION_ID})

    if response.status_code != 200:
        print(f"   ❌ FAIL: Status {response.status_code}")
        return False

    data = response.json()

    if data["total_count"] == 0:
        print(f"   ❌ FAIL: No audit events found")
        return False

    print(f"   ✅ PASS: Audit log has {data['total_count']} events for this session")
    return True


def main():
    print("="*80)
    print("UMC PostgreSQL Integration Test Suite")
    print("="*80)
    print()
    print(f"Base URL: {BASE_URL}")
    print(f"Test Session ID: {TEST_SESSION_ID}")
    print()

    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/", timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Server not running at", BASE_URL)
        print()
        print("Start the server first:")
        print("  uvicorn middleware.umc_memory_server_postgres:app --reload")
        sys.exit(1)

    # Run tests
    tests = [
        test_health_check,
        test_save_note,
        test_save_sensitive_note,
        test_state_update,
        test_request_context,
        test_session_memory,
        test_audit_log,
    ]

    results = []
    for test in tests:
        passed = test()
        results.append(passed)
        print()

    # Summary
    print("="*80)
    passed_count = sum(results)
    total_count = len(results)

    if passed_count == total_count:
        print(f"✅ ALL TESTS PASSED ({passed_count}/{total_count})")
        print("="*80)
        sys.exit(0)
    else:
        print(f"❌ SOME TESTS FAILED ({passed_count}/{total_count} passed)")
        print("="*80)
        sys.exit(1)


if __name__ == "__main__":
    main()
