# Shorties API Documentation

Shorties is a Django REST API backend for a short-form vertical video mobile app with video management, user profiles, and social features.

## API Overview

The API is organized around the following main resources:
- **Users**: User accounts, profiles, and settings
- **Videos**: Video uploads, metadata, and processing
- **Social**: Social interactions including likes, comments, follows, shares, and notifications

## Base URL

```
https://[your-domain]/api/v1/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. To authenticate, send a POST request to `/api/v1/auth/token/` with your username and password.

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

The response will contain access and refresh tokens:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Include the access token in the Authorization header for all authenticated requests:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

To refresh an expired access token, send a POST request to `/api/v1/auth/token/refresh/` with your refresh token:

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Users API

### Register a New User

```
POST /api/v1/users/register/
```

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword",
  "confirm_password": "securepassword"
}
```

### Get Current User Profile

```
GET /api/v1/users/me/
```

### Update User Profile

```
PATCH /api/v1/users/me/
```

**Request Body (example):**
```json
{
  "display_name": "John Doe",
  "bio": "Video creator and technology enthusiast"
}
```

### Update User Settings

```
PATCH /api/v1/users/settings/
```

**Request Body (example):**
```json
{
  "notification_enabled": true,
  "account_privacy": "public"
}
```

### Search Users

```
GET /api/v1/users/search/?query=john
```

## Videos API

### List Videos

```
GET /api/v1/videos/
```

Query parameters:
- `page`: Page number for pagination
- `for_following`: Set to "true" to show only videos from followed users
- `trending`: Set to "true" to show trending videos
- `hashtag`: Filter by hashtag name
- `user_id`: Filter by specific user ID

### Get Video Details

```
GET /api/v1/videos/{video_id}/
```

### Upload Video

```
POST /api/v1/videos/
```

**Request Body:**
- Multipart form data with:
  - `title`: Video title (string)
  - `description`: Video description (string, optional)
  - `hashtags`: Comma-separated hashtags (string, optional)
  - `video_file`: Video file (file upload)
  - `is_private`: Whether the video is private (boolean, default: false)

### Delete Video

```
DELETE /api/v1/videos/{video_id}/
```

### List Video Hashtags

```
GET /api/v1/videos/hashtags/
```

Query parameters:
- `trending`: Set to "true" to show trending hashtags
- `query`: Search hashtags by name

## Social API

### Follow/Unfollow User

```
POST /api/v1/social/follows/toggle/
```

**Request Body:**
```json
{
  "to_user_id": 123
}
```

### Get User Followers

```
GET /api/v1/social/follows/followers/
```

### Get User Following

```
GET /api/v1/social/follows/following/
```

### Like/Unlike Content

```
POST /api/v1/social/likes/
```

**Request Body:**
```json
{
  "object_type": "video",  // or "comment"
  "object_id": 123
}
```

### Comment on Video

```
POST /api/v1/social/comments/
```

**Request Body:**
```json
{
  "video": 123,
  "text": "Great video!",
  "parent": null  // Optional, for replies to comments
}
```

### List Comments for Video

```
GET /api/v1/social/comments/?video_id=123
```

### Record Share

```
POST /api/v1/social/shares/
```

**Request Body:**
```json
{
  "video": 123,
  "platform": "facebook"  // Options: facebook, twitter, instagram, whatsapp, copy_link, other
}
```

### Get Notifications

```
GET /api/v1/social/notifications/
```

### Mark Notifications as Read

```
POST /api/v1/social/notifications/mark-read/
```

**Request Body:**
```json
{
  "notification_ids": [1, 2, 3]  // Optional, if not provided, marks all as read
}
```

### Get Unread Notification Count

```
GET /api/v1/social/notifications/unread-count/
```

## Error Responses

The API uses standard HTTP status codes to indicate the success or failure of requests:

- `200 OK`: The request was successful
- `201 Created`: The resource was successfully created
- `400 Bad Request`: The request was invalid
- `401 Unauthorized`: Authentication is required
- `403 Forbidden`: The authenticated user does not have permission
- `404 Not Found`: The requested resource does not exist
- `500 Internal Server Error`: An error occurred on the server

Error responses include a JSON object with an error message:

```json
{
  "error": "Invalid request",
  "detail": "The provided data was invalid"
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse. Current rate limits:
- Authentication endpoints: 10 requests per minute
- Other endpoints: 60 requests per minute

Rate limit information is included in the response headers:
- `X-RateLimit-Limit`: The maximum number of requests allowed in the current period
- `X-RateLimit-Remaining`: The number of requests remaining in the current period
- `X-RateLimit-Reset`: The time when the current rate limit window resets

## Development Setup

1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Set up a PostgreSQL database
4. Update environment variables in `.env` file
5. Run migrations with `python manage.py migrate`
6. Start the server with `python manage.py runserver`

## Environment Variables

The following environment variables are required:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to "True" for development, "False" for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: PostgreSQL database URL
- `PGUSER`: PostgreSQL username
- `PGPASSWORD`: PostgreSQL password
- `PGHOST`: PostgreSQL host
- `PGPORT`: PostgreSQL port
- `PGDATABASE`: PostgreSQL database name