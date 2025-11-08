# Twitter Clone API

A bare-bones Twitter/X clone that mimics the Twitter API v2 response format. This allows the Janus backend to test and develop without hitting rate limits or waiting for 15-minute metric updates from the real Twitter API.

## Features

- ✅ Post text, images, or videos
- ✅ Like, comment, and retweet functionality
- ✅ Real-time metrics (no 15-minute delay)
- ✅ Twitter API v2 compatible response format
- ✅ Media upload support (images/videos)

## Models

### CloneTweet
- `tweet_id`: Auto-generated unique ID (snowflake-style)
- `text`: Tweet content (max 280 characters)
- `author`: ForeignKey to User (default user ID=1)
- `media_image`: Optional image upload
- `media_video`: Optional video upload
- `media_type`: 'text', 'image', or 'video'
- `created_at`: Timestamp
- `in_reply_to_tweet_id`: For threading/replies

### CloneLike
- Tracks likes on tweets
- Unique constraint: user can only like a tweet once

### CloneRetweet
- Tracks retweets
- Unique constraint: user can only retweet once

### CloneComment
- Tracks comments/replies on tweets
- No unique constraint (multiple comments allowed)

### CloneImpression
- Tracks views/impressions
- Auto-incremented on each tweet fetch

## API Endpoints

All endpoints are prefixed with `/clone/`

### POST /clone/2/tweets
Create a new tweet.

**Request:**
```json
{
  "text": "Hello world!",
  "media": <image_file>,  // optional
  "media_video": <video_file>  // optional
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": "1730123456789",
    "text": "Hello world!"
  }
}
```

### GET /clone/2/tweets
Get tweet(s) with metrics.

**Query Parameters:**
- `ids`: Comma-separated tweet IDs
- `tweet.fields`: Fields to include (e.g., "public_metrics,non_public_metrics")

**Request:**
```
GET /clone/2/tweets?ids=1730123456789&tweet.fields=public_metrics,non_public_metrics
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "1730123456789",
      "text": "Hello world!",
      "created_at": "2025-11-08T12:34:56.000Z",
      "author_id": "1",
      "public_metrics": {
        "retweet_count": 5,
        "reply_count": 3,
        "like_count": 12,
        "quote_count": 0
      },
      "non_public_metrics": {
        "impression_count": 234,
        "user_profile_clicks": 0
      }
    }
  ]
}
```

### POST /clone/2/tweets/like
Like a tweet.

**Request:**
```json
{
  "tweet_id": "1730123456789"
}
```

**Response:**
```json
{
  "success": true,
  "created": true
}
```

### POST /clone/2/tweets/retweet
Retweet a tweet.

**Request:**
```json
{
  "tweet_id": "1730123456789"
}
```

**Response:**
```json
{
  "success": true,
  "created": true
}
```

### POST /clone/2/tweets/comment
Comment on a tweet.

**Request:**
```json
{
  "tweet_id": "1730123456789",
  "text": "Great tweet!"
}
```

**Response:**
```json
{
  "success": true,
  "comment_id": 42,
  "text": "Great tweet!"
}
```

## Integration with Existing Endpoints

The existing Janus endpoints have been updated to use the clone API:

### POST /createXPost/
Now calls `http://localhost:8000/clone/2/tweets` instead of `https://api.x.com/2/tweets`

### POST /getXPostMetrics/
Now calls `http://localhost:8000/clone/2/tweets?ids=...` instead of the real Twitter API

This means:
- ✅ No Twitter API rate limits
- ✅ Instant metrics updates (no 15-minute delay)
- ✅ Full control over test data
- ✅ Works offline
- ✅ Same response format as Twitter API v2

## Media Upload

The clone supports actual file uploads for images and videos.

**Using cURL:**
```bash
curl -X POST http://localhost:8000/clone/2/tweets \
  -F "text=Check out this photo!" \
  -F "media=@/path/to/image.jpg"
```

**Using Postman:**
1. Set method to POST
2. Set URL to `http://localhost:8000/clone/2/tweets`
3. Go to Body tab
4. Select "form-data"
5. Add key "text" with value "Your tweet text"
6. Add key "media" with type "File", then select your image

Media files are stored in:
- Images: `backend/src/media/tweets/images/`
- Videos: `backend/src/media/tweets/videos/`

## Metrics Calculation

Metrics are calculated in real-time:

- **like_count**: Count of CloneLike objects
- **retweet_count**: Count of CloneRetweet objects
- **reply_count**: Count of CloneTweet objects with `in_reply_to_tweet_id` set
- **impression_count**: Count of CloneImpression objects (auto-incremented on each fetch)
- **quote_count**: Not implemented (always 0)

## Default User

The clone uses a single default user (ID=1) for simplicity. On first run, a user will be auto-created:
- Username: `default_user`
- Email: `default@example.com`

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
cd backend/src
python manage.py makemigrations twitter_clone
python manage.py migrate
```

3. (Optional) Create superuser for admin access:
```bash
python manage.py createsuperuser
```

4. Run server:
```bash
python manage.py runserver
```

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to:
- View all tweets
- Manually add/delete likes, retweets, comments
- Inspect impressions
- Manage test data

## Testing

You can test the clone API directly:

```bash
# Create a tweet
curl -X POST http://localhost:8000/clone/2/tweets \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from the clone!"}'

# Response: {"data": {"id": "1730123456789", "text": "Hello from the clone!"}}

# Get metrics
curl "http://localhost:8000/clone/2/tweets?ids=1730123456789&tweet.fields=public_metrics,non_public_metrics"

# Like the tweet
curl -X POST http://localhost:8000/clone/2/tweets/like \
  -H "Content-Type: application/json" \
  -d '{"tweet_id": "1730123456789"}'

# Get metrics again (like_count should be 1 now)
curl "http://localhost:8000/clone/2/tweets?ids=1730123456789&tweet.fields=public_metrics,non_public_metrics"
```

## Differences from Real Twitter API

**Simplified:**
- Single user instead of multi-user system
- Simplified authentication (no OAuth required)
- No quote tweets (quote_count always 0)
- Simplified snowflake ID generation
- No rate limiting

**Enhanced:**
- Real-time metrics (no 15-minute delay)
- Simpler API for testing
- Full control over test data

## Future Enhancements

Potential improvements:
- [ ] Multi-user support
- [ ] Quote tweets
- [ ] Tweet editing
- [ ] Hashtag extraction
- [ ] Mention support (@username)
- [ ] Tweet deletion
- [ ] Proper snowflake ID generation
- [ ] OAuth authentication
- [ ] Rate limiting simulation
