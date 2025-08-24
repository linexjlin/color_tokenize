# Color Tokenize API Documentation

## Overview

The Color Tokenize API provides endpoints for tokenizing text with different language models and visualizing tokens as colored HTML elements.

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Get Available Tokenization Modes

Retrieves a list of all available tokenization modes (models) from the `./tokenizers` directory.

#### Request
```http
GET /api/modes
```

#### Response
```json
{
  "modes": ["Qwen3", "deepseek_v3.1"],
  "count": 2
}
```

#### Example
```bash
curl http://localhost:5000/api/modes
```

### 2. Get Colored Tokenized HTML

Converts text into colored HTML tokens using a specified tokenization mode.

#### Request
```http
GET /api/tokenized?text={text}&mode={mode}
```

#### Parameters
| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| text      | string | Yes      | The text to tokenize |
| mode      | string | Yes      | The tokenization mode to use |

#### Response
```json
{
  "text": "Hello 世界!",
  "mode": "Qwen3",
  "html": "<span class=\"token\" style=\"background-color: #f5f5f5;\"><sup class=\"token-id\">1</sup>Hello</span><span class=\"token\" style=\"background-color: #e8f5e8;\"><sup class=\"token-id\">234</sup> 世界</span><span class=\"token\" style=\"background-color: #fff5f5;\"><sup class=\"token-id\">5</sup>!</span>"
}
```

#### Error Response
```json
{
  "error": "Missing required parameter: text"
}
```

#### Examples

**Basic usage:**
```bash
curl "http://localhost:5000/api/tokenized?text=Hello%20World&mode=Qwen3"
```

**With Chinese text:**
```bash
curl "http://localhost:5000/api/tokenized?text=你好，世界！&mode=deepseek_v3.1"
```

### 3. API Information

Provides basic information about the API.

#### Request
```http
GET /api
```

#### Response
```json
{
  "name": "Color Tokenize API",
  "version": "1.0.0",
  "endpoints": {
    "/api/modes": "GET - List available tokenization modes",
    "/api/tokenized": "GET - Get colored HTML tokens for text"
  }
}
```

## HTML Output Format

The `/api/tokenized` endpoint returns HTML with the following structure:

- Each token is wrapped in a `<span>` element with class `token`
- Each token has a background color calculated based on its ID
- Token IDs are displayed as superscripts above each token
- CSS classes provided:
  - `.token`: Main token container
  - `.token-id`: Superscript showing the token ID

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Missing or invalid parameters
- `404 Not Found`: Invalid mode specified
- `500 Internal Server Error`: Server-side errors

## Usage Example

### Python
```python
import requests

# Get available modes
response = requests.get('http://localhost:5000/api/modes')
modes = response.json()['modes']
print(f"Available modes: {modes}")

# Tokenize text
params = {
    'text': 'Hello, how are you?',
    'mode': modes[0]
}
response = requests.get('http://localhost:5000/api/tokenized', params=params)
result = response.json()
print(result['html'])
```

### JavaScript
```javascript
// Get available modes
fetch('http://localhost:5000/api/modes')
  .then(response => response.json())
  .then(data => {
    console.log('Available modes:', data.modes);
    
    // Tokenize text
    const params = new URLSearchParams({
      text: 'Hello, how are you?',
      mode: data.modes[0]
    });
    
    return fetch(`/api/tokenized?${params}`);
  })
  .then(response => response.json())
  .then(data => {
    console.log('HTML:', data.html);
    document.getElementById('output').innerHTML = data.html;
  });
```

## Running the API

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python app.py
```

3. The API will be available at `http://localhost:5000`

## Dependencies

- Flask 2.3.3
- tokenizers 0.15.0