# Spring Boot API Integration Guide

This document explains how to integrate the PM Internship AI Recommendation API with your Spring Boot backend to fetch student profiles and internship data.

## 🌐 Overview

The system now supports fetching data from a Spring Boot backend API with automatic fallback to local CSV files if the API is unavailable. This provides a robust, production-ready solution that can work both with and without the Spring Boot backend.

## 🔧 Configuration

### Environment Variables

Set these environment variables to configure the Spring Boot API connection:

```bash
# Spring Boot API Configuration
SPRING_BOOT_BASE_URL=http://localhost:8080
INTERNSHIPS_ENDPOINT=/api/internships
STUDENTS_ENDPOINT=/api/students
RECOMMENDATIONS_CALLBACK_ENDPOINT=/api/recommendations/callback
FEEDBACK_CALLBACK_ENDPOINT=/api/feedback/callback
API_TIMEOUT=30

# Optional: API Authentication
SPRING_BOOT_API_KEY=your_api_key_here
```

### Default Configuration

If no environment variables are set, the system uses these defaults:
- **Base URL**: `http://localhost:8080`
- **Internships Endpoint**: `/api/internships`
- **Students Endpoint**: `/api/students`
- **Recommendations Callback**: `/api/recommendations/callback`
- **Feedback Callback**: `/api/feedback/callback`
- **Timeout**: 30 seconds

## 📡 API Endpoints Expected

Your Spring Boot backend should provide these endpoints:

### 1. Internships API

**GET** `/api/internships`
- Returns: Array of internship objects
- Example response:
```json
[
  {
    "id": 1,
    "title": "Software Developer Intern",
    "description": "Develop web applications using Java and Spring Boot",
    "requiredSkills": ["Java", "Spring Boot", "SQL"],
    "preferredSkills": ["Git", "Docker"],
    "category": "IT",
    "location": "Bhubaneswar",
    "state": "Odisha",
    "organization": "Tech Solutions Ltd.",
    "educationRequirement": "B.Tech",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
]
```

**GET** `/api/internships/{id}`
- Returns: Single internship object
- Same format as above

### 2. Students API

**GET** `/api/students`
- Returns: Array of student objects
- Example response:
```json
[
  {
    "id": 202,
    "name": "John Doe",
    "email": "john@example.com",
    "educationLevel": "B.Tech",
    "skills": ["Python", "Machine Learning", "Data Analysis"],
    "interests": ["IT", "Data Science"],
    "preferredLocation": "Remote",
    "preferredState": null,
    "isFirstGenLearner": false,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
]
```

**GET** `/api/students/{id}`
- Returns: Single student object
- Same format as above

### 3. Callback Endpoints (Required for Response Callbacks)

**POST** `/api/recommendations/callback`
- Receives: Recommendation responses from AI service
- Example payload:
```json
{
  "studentId": 202,
  "recommendations": [
    {
      "internship_id": 1,
      "score": 85.5,
      "reason": "Skills match",
      "title": "Software Developer Intern",
      "organization": "Tech Solutions Ltd.",
      "location": "Bhubaneswar"
    }
  ],
  "timestamp": "2024-01-01T00:00:00Z",
  "source": "ai-recommendation-service",
  "version": "v1.0",
  "requestId": "req_001",
  "metadata": {
    "total_recommendations": 5,
    "model_version": "v1.0",
    "top_n": 5
  }
}
```

**POST** `/api/feedback/callback`
- Receives: Feedback responses from AI service
- Example payload:
```json
{
  "feedback": {
    "student_id": 202,
    "internship_id": 1,
    "feedback": "LIKE",
    "comments": "Great opportunity!"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "source": "ai-recommendation-service",
  "version": "v1.0",
  "requestId": "feedback_001"
}
```

### 4. Health Check (Optional)

**GET** `/actuator/health`
- Returns: Health status
- Used to check if the API is available

## 🔄 Fallback Mechanism

The system implements a robust fallback mechanism:

1. **Primary**: Try to fetch data from Spring Boot API
2. **Secondary**: If API fails, fall back to local CSV files
3. **Tertiary**: If CSV fails, use hardcoded sample data

This ensures the system always works, even if the Spring Boot backend is unavailable.

## 🚀 Usage

### Starting the Application

1. **With Spring Boot Backend**:
   ```bash
   # Set environment variables
   export SPRING_BOOT_BASE_URL=http://your-spring-boot-server:8080
   
   # Start the application
   python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
   ```

2. **Without Spring Boot Backend** (uses CSV fallback):
   ```bash
   # Start the application (will automatically use CSV files)
   python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
   ```

### Testing the Integration

Run the test script to verify the integration:

```bash
python test_api_integration.py
```

This will:
- Test API connectivity
- Verify data fetching
- Test fallback mechanisms
- Validate data transformation

## 📊 Data Flow

```
Request for Recommendations
           ↓
    Check if student_id provided
           ↓
    Try to fetch from Spring Boot API
           ↓
    [Success] Use API data + merge with request data
           ↓
    [Failure] Use request data only
           ↓
    Generate recommendations using ML model
           ↓
    Return formatted recommendations
           ↓
    [If callback enabled] Send response back to Spring Boot
```

## 🔄 Callback Functionality

The AI service can automatically send responses back to your Spring Boot backend:

### Callback Types

1. **Recommendations Callback**: Sends generated recommendations back to Spring Boot
2. **Feedback Callback**: Sends user feedback back to Spring Boot  
3. **Model Training Callback**: Sends training results back to Spring Boot
4. **Health Status Callback**: Sends health status for monitoring

### Callback Control

You can control callbacks using request parameters:

```json
{
  "student_id": 202,
  "education_level": "B.Tech",
  "skills": ["Python", "Machine Learning"],
  "request_id": "unique_request_id",
  "send_callback": true
}
```

- **`request_id`**: Optional unique identifier for tracking
- **`send_callback`**: Boolean to enable/disable callbacks (default: true)

### Callback Payload Structure

All callbacks include:
- **`timestamp`**: When the callback was sent
- **`source`**: Always "ai-recommendation-service"
- **`version`**: Model version
- **`requestId`**: Request tracking ID (if provided)

## 🔍 Monitoring

### Health Check Endpoint

**GET** `/health`
- Returns system health including:
  - API connectivity status
  - Number of internships loaded
  - Model training status

### Model Info Endpoint

**GET** `/model/info`
- Returns detailed model information:
  - Internships count
  - Feature dimensions
  - Model version
  - Last training time

## 🛠️ Development

### Adding New API Endpoints

To add support for new Spring Boot endpoints:

1. **Update `api_client.py`**:
   ```python
   def get_new_data(self):
       url = f"{self.base_url}/api/new-endpoint"
       response = requests.get(url, headers=self.headers, timeout=self.timeout)
       return response.json()
   ```

2. **Update `data_loader.py`**:
   ```python
   def load_new_data():
       try:
           api_client = SpringBootAPIClient()
           return api_client.get_new_data()
       except:
           return fallback_data()
   ```

### Custom Data Transformation

If your Spring Boot API returns data in a different format, update the transformation methods in `api_client.py`:

```python
def _transform_custom_data(self, data):
    return {
        "id": data.get("customId"),
        "title": data.get("customTitle"),
        # ... map your fields
    }
```

## 🔒 Security

### API Authentication

The system supports Bearer token authentication:

```bash
export SPRING_BOOT_API_KEY=your_jwt_token_here
```

The token will be automatically included in all API requests as:
```
Authorization: Bearer your_jwt_token_here
```

### HTTPS Support

For production, use HTTPS:

```bash
export SPRING_BOOT_BASE_URL=https://your-secure-api.com
```

## 📝 Logging

The system provides detailed logging for debugging:

- **API Connection**: Logs when connecting to Spring Boot API
- **Data Loading**: Logs number of records loaded
- **Fallback**: Logs when falling back to CSV or sample data
- **Errors**: Logs API errors and fallback triggers

## 🎯 Production Deployment

### Environment Setup

1. **Set production environment variables**:
   ```bash
   SPRING_BOOT_BASE_URL=https://your-production-api.com
   SPRING_BOOT_API_KEY=your_production_token
   API_TIMEOUT=60
   ```

2. **Deploy with proper error handling**:
   - The system will automatically fall back to CSV files if the API is unavailable
   - Monitor logs for API connectivity issues
   - Set up alerts for API failures

### Performance Considerations

- **Caching**: Consider implementing caching for frequently accessed data
- **Rate Limiting**: Be aware of API rate limits
- **Timeout**: Adjust `API_TIMEOUT` based on your API response times
- **Connection Pooling**: The system uses requests library with connection reuse

## 🆘 Troubleshooting

### Common Issues

1. **API Not Available**:
   - Check if Spring Boot server is running
   - Verify the base URL is correct
   - Check network connectivity

2. **Authentication Errors**:
   - Verify API key is correct
   - Check if token has expired
   - Ensure proper authorization headers

3. **Data Format Issues**:
   - Verify API response format matches expected schema
   - Check data transformation methods
   - Review error logs for parsing issues

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
```

This will provide detailed information about API calls and data processing.

## 📞 Support

For issues or questions about the Spring Boot integration:

1. Check the logs for error messages
2. Run the test script to verify connectivity
3. Review the API endpoint documentation
4. Check the fallback mechanism is working correctly

The system is designed to be robust and will continue working even if the Spring Boot backend is temporarily unavailable.
