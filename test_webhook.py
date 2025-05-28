#!/usr/bin/env python3
"""
Test script to simulate Slack URL verification challenge
"""
import requests
import json
import argparse

def test_url_verification(webhook_url):
    """
    Send a test URL verification challenge to the webhook URL
    """
    # Prepare the URL verification payload
    payload = {
        "type": "url_verification",
        "token": "verification_token",
        "challenge": "challenge_value"
    }
    
    # Send the request
    print(f"Sending URL verification challenge to {webhook_url}")
    response = requests.post(
        webhook_url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    # Print the response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Check if the response is correct
    try:
        response_json = response.json()
        if response_json.get("challenge") == "challenge_value":
            print("✅ URL verification successful!")
        else:
            print("❌ URL verification failed: Challenge value not returned correctly")
    except:
        print("❌ URL verification failed: Response is not valid JSON")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Slack URL verification")
    parser.add_argument("--url", default="http://localhost:8080/slack/events", 
                        help="Webhook URL to test (default: http://localhost:3000/slack/events)")
    args = parser.parse_args()
    
    test_url_verification(args.url)
