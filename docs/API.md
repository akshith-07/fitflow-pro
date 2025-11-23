# FitFlow Pro - API Documentation

## Base URL

Development: `http://localhost:8000`
Production: `https://api.fitflowpro.com`

## Authentication

All API requests (except auth endpoints) require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Getting a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## API Endpoints

### Authentication

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "member",
  "organization_id": "uuid"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123!
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Organizations

#### List Organizations
```http
GET /api/v1/organizations/?skip=0&limit=100
Authorization: Bearer <token>
```

#### Create Organization
```http
POST /api/v1/organizations/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Elite Fitness Gym",
  "slug": "elite-fitness",
  "contact_email": "info@elitefitness.com",
  "contact_phone": "+1234567890",
  "timezone": "America/New_York",
  "currency": "USD",
  "primary_color": "#6366f1"
}
```

#### Get Organization
```http
GET /api/v1/organizations/{organization_id}
Authorization: Bearer <token>
```

#### Update Organization
```http
PUT /api/v1/organizations/{organization_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Elite Fitness Gym & Spa",
  "primary_color": "#8b5cf6"
}
```

#### Delete Organization
```http
DELETE /api/v1/organizations/{organization_id}
Authorization: Bearer <token>
```

### Members

#### List Members
```http
GET /api/v1/members/?skip=0&limit=100&search=john&status=active
Authorization: Bearer <token>
```

Query Parameters:
- `skip` (int): Pagination offset
- `limit` (int): Items per page (max 100)
- `search` (string): Search by name, email, or member ID
- `status` (string): Filter by status (active, frozen, expired, cancelled)

#### Create Member
```http
POST /api/v1/members/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "uuid",
  "member_id": "MEM-001",
  "joined_at": "2024-01-15",
  "date_of_birth": "1990-05-20",
  "gender": "male",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1234567890",
  "fitness_goals": {
    "weight_loss": 10,
    "target_weight": 75,
    "goal": "Get fit for summer"
  },
  "tags": ["premium", "vip"]
}
```

#### Get Member
```http
GET /api/v1/members/{member_id}
Authorization: Bearer <token>
```

#### Update Member
```http
PUT /api/v1/members/{member_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "fitness_goals": {
    "weight_loss": 12,
    "target_weight": 73
  },
  "tags": ["premium", "vip", "active"]
}
```

#### Delete Member
```http
DELETE /api/v1/members/{member_id}
Authorization: Bearer <token>
```

## Response Format

### Success Response
```json
{
  "id": "uuid",
  "name": "Resource name",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created
- `204 No Content` - Resource deleted
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

- 60 requests per minute per user
- 1000 requests per hour per user

Rate limit headers in response:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642262400
```

## Pagination

List endpoints support pagination:

```http
GET /api/v1/members/?skip=0&limit=50
```

Response includes total count in header:
```
X-Total-Count: 250
```

## Filtering and Search

Most list endpoints support filtering:

```http
# Search
GET /api/v1/members/?search=john

# Filter by status
GET /api/v1/members/?status=active

# Filter by date range
GET /api/v1/check-ins/?start_date=2024-01-01&end_date=2024-01-31

# Combine filters
GET /api/v1/members/?status=active&search=john&skip=0&limit=20
```

## Field Selection

Reduce response payload by selecting specific fields:

```http
GET /api/v1/members/?fields=id,first_name,last_name,email
```

## Sorting

Sort results using the `sort` parameter:

```http
# Ascending
GET /api/v1/members/?sort=created_at

# Descending
GET /api/v1/members/?sort=-created_at

# Multiple fields
GET /api/v1/members/?sort=last_name,first_name
```

## Webhooks

Configure webhooks to receive real-time events:

### Webhook Events
- `member.created`
- `member.updated`
- `payment.successful`
- `payment.failed`
- `membership.expired`
- `class.booked`
- `check-in.created`

### Webhook Payload
```json
{
  "event": "payment.successful",
  "timestamp": "2024-01-15T10:30:00Z",
  "organization_id": "uuid",
  "data": {
    "payment_id": "uuid",
    "amount": 99.99,
    "currency": "USD",
    "member_id": "uuid"
  }
}
```

## Interactive API Docs

Visit `/docs` for interactive API documentation (Swagger UI)
Visit `/redoc` for alternative API documentation (ReDoc)

Example: `http://localhost:8000/docs`

## Code Examples

### Python
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "user@example.com", "password": "password123"}
)
token = response.json()["access_token"]

# Get members
headers = {"Authorization": f"Bearer {token}"}
members = requests.get(
    "http://localhost:8000/api/v1/members/",
    headers=headers
).json()
```

### JavaScript/TypeScript
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=user@example.com&password=password123'
});
const { access_token } = await loginResponse.json();

// Get members
const membersResponse = await fetch('http://localhost:8000/api/v1/members/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const members = await membersResponse.json();
```

### cURL
```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=user@example.com&password=password123" \
  | jq -r '.access_token')

# Get members
curl -X GET "http://localhost:8000/api/v1/members/" \
  -H "Authorization: Bearer $TOKEN"
```

## Support

For API support:
- Email: api-support@fitflowpro.com
- Documentation: https://docs.fitflowpro.com
- Status Page: https://status.fitflowpro.com
