#!/usr/bin/env python
"""
API usage examples for the Shorties API.

This script demonstrates how to interact with the Shorties API using Python and requests.
"""

import requests
import json
import os

# Set the base URL for the API
BASE_URL = "http://localhost:5000/api/v1"

# Authentication
def register_user(username, email, password):
    """Register a new user"""
    url = f"{BASE_URL}/users/register/"
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": password
    }
    response = requests.post(url, json=payload)
    return response.json()

def login_user(username, password):
    """Login and get JWT tokens"""
    url = f"{BASE_URL}/auth/token/"
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=payload)
    return response.json()

def refresh_token(refresh_token):
    """Refresh an expired access token"""
    url = f"{BASE_URL}/auth/token/refresh/"
    payload = {
        "refresh": refresh_token
    }
    response = requests.post(url, json=payload)
    return response.json()

# User API
def get_user_profile(token):
    """Get the current user's profile"""
    url = f"{BASE_URL}/users/me/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def update_profile(token, display_name=None, bio=None, profile_picture=None):
    """Update user profile"""
    url = f"{BASE_URL}/users/me/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {}
    if display_name:
        payload["display_name"] = display_name
    if bio:
        payload["bio"] = bio
    
    files = {}
    if profile_picture:
        files = {
            "profile_picture": open(profile_picture, "rb")
        }
    
    if files:
        response = requests.patch(url, headers=headers, data=payload, files=files)
    else:
        response = requests.patch(url, headers=headers, json=payload)
    
    return response.json()

def search_users(token, query):
    """Search for users"""
    url = f"{BASE_URL}/users/search/?query={query}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Video API
def list_videos(token, page=1, for_following=False, trending=False, hashtag=None, user_id=None):
    """List videos with various filters"""
    url = f"{BASE_URL}/videos/?page={page}"
    
    if for_following:
        url += "&for_following=true"
    if trending:
        url += "&trending=true"
    if hashtag:
        url += f"&hashtag={hashtag}"
    if user_id:
        url += f"&user_id={user_id}"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_video(token, video_id):
    """Get a specific video"""
    url = f"{BASE_URL}/videos/{video_id}/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def upload_video(token, title, video_file, description=None, hashtags=None, is_private=False):
    """Upload a new video"""
    url = f"{BASE_URL}/videos/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    payload = {
        "title": title,
        "is_private": is_private
    }
    
    if description:
        payload["description"] = description
    if hashtags:
        payload["hashtags"] = hashtags
    
    files = {
        "video_file": open(video_file, "rb")
    }
    
    response = requests.post(url, headers=headers, data=payload, files=files)
    return response.json()

def delete_video(token, video_id):
    """Delete a video"""
    url = f"{BASE_URL}/videos/{video_id}/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.delete(url, headers=headers)
    return response.status_code

# Social API
def follow_user(token, user_id):
    """Follow a user"""
    url = f"{BASE_URL}/social/follows/toggle/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "to_user_id": user_id
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_followers(token):
    """Get current user's followers"""
    url = f"{BASE_URL}/social/follows/followers/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_following(token):
    """Get users that the current user follows"""
    url = f"{BASE_URL}/social/follows/following/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def like_content(token, object_type, object_id):
    """Like a video or comment"""
    url = f"{BASE_URL}/social/likes/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "object_type": object_type,  # "video" or "comment"
        "object_id": object_id
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def add_comment(token, video_id, text, parent_id=None):
    """Add a comment to a video"""
    url = f"{BASE_URL}/social/comments/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "video": video_id,
        "text": text
    }
    if parent_id:
        payload["parent"] = parent_id
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_comments(token, video_id):
    """Get comments for a video"""
    url = f"{BASE_URL}/social/comments/?video_id={video_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def share_video(token, video_id, platform):
    """Record a video share"""
    url = f"{BASE_URL}/social/shares/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "video": video_id,
        "platform": platform  # facebook, twitter, instagram, whatsapp, copy_link, other
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_notifications(token):
    """Get notifications for the current user"""
    url = f"{BASE_URL}/social/notifications/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def mark_notifications_read(token, notification_ids=None):
    """Mark notifications as read"""
    url = f"{BASE_URL}/social/notifications/mark-read/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {}
    if notification_ids:
        payload["notification_ids"] = notification_ids
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_unread_notification_count(token):
    """Get count of unread notifications"""
    url = f"{BASE_URL}/social/notifications/unread-count/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Example usage flow
def run_example():
    """Run a complete example flow"""
    print("Shorties API Example Usage")
    print("-" * 40)
    
    # 1. Register a new user
    print("Registering a new user...")
    register_response = register_user("testuser", "test@example.com", "password123")
    print(f"Register response: {json.dumps(register_response, indent=2)}")
    
    # 2. Login
    print("\nLogging in...")
    login_response = login_user("testuser", "password123")
    access_token = login_response.get("access")
    refresh_token = login_response.get("refresh")
    print(f"Login response: {json.dumps(login_response, indent=2)}")
    
    if not access_token:
        print("Failed to login, cannot continue example")
        return
    
    # 3. Get user profile
    print("\nGetting user profile...")
    profile = get_user_profile(access_token)
    print(f"User profile: {json.dumps(profile, indent=2)}")
    
    # 4. Update profile
    print("\nUpdating profile...")
    updated_profile = update_profile(access_token, display_name="Test User", bio="Just testing the API")
    print(f"Updated profile: {json.dumps(updated_profile, indent=2)}")
    
    # 5. Upload a video
    print("\nUploading a video...")
    # Replace with a real video file path
    video_path = "test_video.mp4"
    if os.path.exists(video_path):
        upload_response = upload_video(
            access_token, 
            "My First Test Video", 
            video_path,
            description="This is a test video",
            hashtags="test,api,example"
        )
        print(f"Upload response: {json.dumps(upload_response, indent=2)}")
        video_id = upload_response.get("id")
    else:
        print(f"Video file not found at {video_path}, skipping upload")
        # For this example, we'll simulate having a video ID
        video_id = 1
    
    # 6. List videos
    print("\nListing videos...")
    videos = list_videos(access_token)
    print(f"Videos: {json.dumps(videos, indent=2)}")
    
    # 7. Add a comment
    if video_id:
        print("\nAdding a comment...")
        comment = add_comment(access_token, video_id, "This is a test comment")
        print(f"Comment response: {json.dumps(comment, indent=2)}")
        
        # 8. Like the video
        print("\nLiking the video...")
        like_response = like_content(access_token, "video", video_id)
        print(f"Like response: {json.dumps(like_response, indent=2)}")
    
    # 9. Get notifications
    print("\nGetting notifications...")
    notifications = get_notifications(access_token)
    print(f"Notifications: {json.dumps(notifications, indent=2)}")
    
    # 10. Get unread notification count
    print("\nGetting unread notification count...")
    unread_count = get_unread_notification_count(access_token)
    print(f"Unread count: {json.dumps(unread_count, indent=2)}")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    run_example()