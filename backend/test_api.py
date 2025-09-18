#!/usr/bin/env python3
"""
Quick API test script for Charles Nwankpa Portfolio Backend
Test basic functionality without full test suite
"""

import asyncio
import aiohttp
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

async def test_health_check():
    """Test health check endpoint."""
    print("🏥 Testing health check...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE}/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health check passed: {data['status']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status}")
                return False

async def test_cv_request():
    """Test CV request endpoint."""
    print("📄 Testing CV request...")
    
    test_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1-555-0123",
        "company": "Test Company",
        "role": "CTO",
        "purpose": "Testing the API",
        "consent": True,
        "website": ""  # Honeypot
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/api/request-cv",
            json=test_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ CV request successful: {data['request_id']}")
                return True
            elif response.status == 429:
                print("⚠️  Rate limit hit (expected in testing)")
                return True
            else:
                print(f"❌ CV request failed: {response.status}")
                text = await response.text()
                print(f"   Response: {text}")
                return False

async def test_invalid_cv_request():
    """Test CV request with invalid data."""
    print("🚫 Testing invalid CV request...")
    
    invalid_data = {
        "name": "",  # Invalid: empty name
        "email": "invalid-email",  # Invalid: bad email format
        "phone": "123",  # Invalid: too short
        "consent": False,  # Invalid: no consent
        "website": "spam"  # Honeypot triggered
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/api/request-cv",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 400:
                print("✅ Invalid request properly rejected")
                return True
            else:
                print(f"❌ Invalid request not handled: {response.status}")
                return False

async def test_admin_login():
    """Test admin login (will fail without proper setup)."""
    print("🔐 Testing admin login...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"  # Default password from migration
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/api/admin/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("✅ Admin login successful")
                return data.get("access_token")
            else:
                print(f"⚠️  Admin login failed: {response.status} (expected if no DB)")
                return None

async def test_docs_endpoint():
    """Test API documentation endpoint."""
    print("📚 Testing API docs...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE}/docs") as response:
            if response.status == 200:
                print("✅ API docs accessible")
                return True
            else:
                print(f"⚠️  API docs not accessible: {response.status}")
                return False

async def main():
    """Run all tests."""
    print("🚀 Charles Nwankpa Portfolio Backend API Test")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_docs_endpoint,
        test_cv_request,
        test_invalid_cv_request,
        test_admin_login
    ]
    
    results = []
    
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("📊 Test Summary")
    print("-" * 20)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    elif passed > 0:
        print("⚠️  Some tests passed. Check database connection and configuration.")
    else:
        print("❌ All tests failed. Check if API is running and properly configured.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")