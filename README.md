# Python AI Service Documentation

## Overview
The Python AI Service is a microservice responsible for generating personalized internship recommendations for CareerLens users. It loads, trains, and serves a machine learning model, processes feedback, and communicates with the Spring Boot backend via callbacks.

---

## Main Components

### 1. RecommendationService
- **Purpose:** Main service layer for recommendation operations.
- **Responsibilities:**
  - Model initialization and training
  - Generating recommendations
  - Processing feedback
  - Sending callbacks to Spring Boot

#### Key Methods:
- `initialize_model()`
  - Loads a pre-trained model if available, otherwise trains a new one.
- `retrain_model(force=False, request_id=None, send_callback=True)`
  - Retrains the model with current data. Sends training result callback to Spring Boot if enabled.
- `get_recommendations(student_data, top_n=5, request_id=None, send_callback=True)`
  - Generates top-N recommendations for a student. Optionally sends callback to Spring Boot.
- `get_model_info()`
  - Returns metadata about the current model (internship count, feature dimension, version, last trained).
- `process_feedback(feedback_data, request_id=None, send_callback=True)`
  - Processes user feedback and sends callback to Spring Boot.

---

## Model Handling
- **Model:** `RecommendationModel` (imported from `app/models/recommendation_model.py`)
- **Persistence:** Model is saved/loaded from `trained_models/recommendation_model.joblib`.
- **Training Data:** Loaded via `load_sample_data()` (can be replaced with database integration in production).
- **Training:**
  - If no model exists, trains a new one.
  - Can be retrained on demand.
  - Training time and stats are logged and sent to backend.

---

## Recommendation Generation
- **Input:** Student profile data (dict), optionally merged with API data if `student_id` is provided.
- **Process:**
  - Model computes scores and reasons for each internship.
  - Top-N results are formatted with internship details.
- **Output:** List of recommended internships with scores, reasons, and metadata.
- **Callback:** If enabled, sends recommendations and metadata to Spring Boot for logging/analytics.

---

## Feedback Processing
- **Input:** Feedback data from user (dict)
- **Process:**
  - Logs feedback.
  - Sends feedback callback to Spring Boot.
  - (TODO) Can be used for model improvement in future.
- **Output:** Returns success status.

---

## Integration with Spring Boot
- **Callback Service:** `SpringBootCallbackService` handles HTTP callbacks to backend endpoints for:
  - Model training results
  - Recommendations
  - Feedback
- **Usage:** All major operations (training, recommendation, feedback) can send asynchronous callbacks to Spring Boot for monitoring and analytics.

---

## Directory Structure
```
python-ai-service/
  app/
    models/
      recommendation_model.py
    services/
      recommendation_services.py
      callback_service.py
    utils/
      data_loader.py
  trained_models/
    recommendation_model.joblib
```

---

## Example Workflow
1. **Startup:**
   - `initialize_model()` loads or trains the model.
2. **Recommendation Request:**
   - `get_recommendations(student_data)` returns top internships for a student.
   - Callback sent to backend if enabled.
3. **Feedback Submission:**
   - `process_feedback(feedback_data)` logs feedback and sends callback.
4. **Model Retraining:**
   - `retrain_model(force=True)` retrains the model and notifies backend.

---

## Actual Working of Python AI Service

### 1. Startup & Model Initialization
- When the service starts, `initialize_model()` is called.
- If a pre-trained model exists (`trained_models/recommendation_model.joblib`), it is loaded.
- If not, the service trains a new model using sample internship data (`load_sample_data()`), saves it, and sets metadata.

### 2. Handling Recommendation Requests
- The backend (Spring Boot) sends a request with student profile data.
- If a `student_id` is provided, the service tries to fetch additional data via API (`load_student_data`).
- The model computes scores and reasons for each internship using the student's data.
- The top-N internships are selected, formatted with details, and returned as recommendations.
- If enabled, a callback with recommendations and metadata is sent asynchronously to the backend for logging/analytics.

### 3. Feedback Processing
- When feedback is received, it is logged and a callback is sent to the backend.
- The feedback can be used for future model improvement (currently a TODO).

### 4. Model Retraining
- The model can be retrained on demand (e.g., via an API call or admin action).
- Retraining uses the latest internship data and updates the model file and metadata.
- A callback with training results is sent to the backend.

### 5. Integration with Backend
- All major operations (recommendation, feedback, training) can send HTTP callbacks to the Spring Boot backend for monitoring, analytics, or further processing.
- The callback service (`SpringBootCallbackService`) handles these HTTP requests.

### 6. Extensibility
- The service is designed to be extended:
  - Replace sample data loading with real database queries.
  - Implement feedback-driven model improvement.
  - Add new recommendation features or algorithms.

---

## How the Recommendation Algorithm Works

### 1. Data Preparation
- The model is trained on internship data loaded from sample files (or database in production).
- Each internship is represented by features such as title, organization, location, required skills, preferred skills, and description.
- Student data includes education level, skills, interests, and other profile attributes.

### 2. Feature Engineering
- Both internships and students are converted into feature vectors.
- Features may include skill matches, location preferences, education alignment, and interest overlap.
- The model computes similarity or relevance scores between student and internship vectors.

### 3. Scoring & Ranking
- For each internship, the model calculates a score based on how well the student's profile matches the internship requirements and preferences.
- The score is typically a weighted sum or similarity metric (e.g., cosine similarity, dot product, or custom logic).
- Each score is accompanied by a reason (e.g., "Excellent skill match and location preference").

### 4. Recommendation Selection
- Internships are ranked by their scores.
- The top-N internships are selected as recommendations for the student.

### 5. Output Formatting
- Each recommended internship includes:
  - Internship ID
  - Score (as a percentage)
  - Reason for recommendation
  - Internship details (title, organization, location, description, required/preferred skills)

### 6. Feedback Loop (Planned)
- User feedback on recommendations can be used to improve the model in future iterations (e.g., retraining, adjusting weights).

---

## Example
If a student has skills in Python and Data Analysis, and is interested in internships in Bangalore, the model will:
- Score internships higher if they require Python/Data Analysis and are located in Bangalore.
- Provide reasons like "Strong alignment with your skills and location preference".

---

## Summary
- The Python AI Service acts as a recommendation engine, serving requests from the backend, processing feedback, and maintaining its model lifecycle.
- It is modular, extensible, and integrated with the backend for analytics and monitoring.

---

## Extending the Service
- Replace `load_sample_data()` with database queries for production.
- Implement feedback-driven model improvement in `process_feedback()`.
- Add more features to the recommendation algorithm as needed.

---

## Contact
For support, contact the CareerLens backend team.
