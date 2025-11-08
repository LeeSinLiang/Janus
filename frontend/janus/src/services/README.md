# API Service Documentation

## Overview

This directory contains the API service layer for communicating with the Django backend.

## Files

- `api.ts`: Main API service with fetch functions

## API Endpoint Configuration

### Environment Variables

Set up your `.env.local` file:

```bash
# Django backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Alternative for production
# NEXT_PUBLIC_API_URL=https://your-production-backend.com
```

### Default Configuration

If `NEXT_PUBLIC_API_URL` is not set, defaults to `http://localhost:8000`.

## Functions

### `fetchGraphData()`

Fetches graph data from the real Django backend.

**Endpoint**: `GET /api/graph`

**Returns**: `Promise<GraphResponse>`

**Example**:
```typescript
import { fetchGraphData } from '@/services/api';

const data = await fetchGraphData();
console.log(data.diagram);
console.log(data.metrics);
console.log(data.changes);
```

**Error Handling**:
```typescript
try {
  const data = await fetchGraphData();
} catch (error) {
  console.error('API Error:', error);
}
```

### `fetchGraphDataMock()`

Returns mock data for development and testing.

**Returns**: `Promise<GraphResponse>`

**Use Cases**:
- Development without backend running
- Testing frontend logic
- Demonstration purposes

**Example**:
```typescript
import { fetchGraphDataMock } from '@/services/api';

const mockData = await fetchGraphDataMock();
// Returns data matching sample_response.json
```

## Testing the API

### Test Mock Data

```typescript
// In your component or test file
import { fetchGraphDataMock } from '@/services/api';

async function testMock() {
  const data = await fetchGraphDataMock();
  console.log('Mock data:', data);
  console.log('Has changes:', data.changes);
  console.log('Number of metrics:', data.metrics.length);
}

testMock();
```

### Test Real Backend

1. Start your Django backend:
   ```bash
   python manage.py runserver
   ```

2. Test the endpoint manually:
   ```bash
   curl http://localhost:8000/api/graph
   ```

3. Test in frontend:
   ```typescript
   import { fetchGraphData } from '@/services/api';

   async function testBackend() {
     try {
       const data = await fetchGraphData();
       console.log('Backend data:', data);
     } catch (error) {
       console.error('Backend error:', error);
     }
   }

   testBackend();
   ```

## Customizing Mock Data

Edit `fetchGraphDataMock()` in `api.ts` to test different scenarios:

### Scenario 1: No Changes
```typescript
return {
  diagram: "...",
  metrics: [...],
  changes: false  // Graph won't rebuild
};
```

### Scenario 2: New Data Available
```typescript
return {
  diagram: "... new diagram ...",
  metrics: [... updated metrics ...],
  changes: true  // Graph will rebuild
};
```

### Scenario 3: Test Error Handling
```typescript
throw new Error('Simulated API error');
```

## Adding Authentication

If your backend requires authentication, update the fetch call:

```typescript
export async function fetchGraphData(): Promise<GraphResponse> {
  const response = await fetch(`${API_BASE_URL}${GRAPH_ENDPOINT}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`,  // Add auth
    },
    credentials: 'include',  // Send cookies
  });

  // ... rest of code
}

function getAuthToken(): string {
  // Get token from localStorage, cookies, or context
  return localStorage.getItem('authToken') || '';
}
```

## Adding More Endpoints

Follow this pattern to add new endpoints:

```typescript
const NEW_ENDPOINT = '/api/endpoint-name';

export async function fetchNewData(): Promise<NewDataType> {
  try {
    const response = await fetch(`${API_BASE_URL}${NEW_ENDPOINT}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    const data: NewDataType = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching new data:', error);
    throw error;
  }
}
```

## CORS Configuration

If you encounter CORS errors, ensure your Django backend has proper CORS headers:

```python
# Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js dev server
]

CORS_ALLOW_CREDENTIALS = True
```

## Network Monitoring

Monitor API calls in browser DevTools:
1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Watch for requests to `/api/graph`
5. Check request/response details
