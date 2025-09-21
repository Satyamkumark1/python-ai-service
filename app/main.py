from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

from .schemas.request_models import StudentRequest, FeedbackRequest, RetrainRequest, ResumeAnalyzeRequest
from .schemas.response_models import (
    RecommendationResponse, HealthResponse, ModelInfoResponse,
    TrainingResponse, ErrorResponse, FeedbackResponse,
    ResumeAnalyzeResponse, ResumeAnalyzeSuggestion
)
from .services.recommendation_services import RecommendationService

# Initialize FastAPI app
app = FastAPI(
    title="PM Internship AI Recommendation API",
    description="AI-powered internship recommendation system for PM Internship Scheme",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"]
)

# Initialize services
recommendation_service = RecommendationService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    print("🚀 Starting PM Internship AI Recommendation Service...")
    success = recommendation_service.initialize_model()
    if not success:
        print("❌ Failed to initialize model. Some endpoints may not work.")

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs"""
    return {"message": "PM Internship AI Recommendation API - Visit /docs for API documentation"}

@app.post("/recommendations/generate", 
          response_model=RecommendationResponse,
          responses={500: {"model": ErrorResponse}})
async def generate_recommendations(request: StudentRequest):
    """
    Generate personalized internship recommendations for a student
    """
    try:
        start_time = datetime.now()
        
        # Convert Pydantic model to dict for service
        student_data = request.dict()
        
        # Get recommendations
        recommendations = recommendation_service.get_recommendations(
            student_data, 
            top_n=5,
            request_id=request.request_id,
            send_callback=request.send_callback
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return RecommendationResponse(
            recommendations=recommendations,
            model_version="v1.0",
            generated_at=datetime.now().isoformat(),
            total_recommendations=len(recommendations)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {str(e)}"
        )

@app.post("/recommendations/feedback", response_model=FeedbackResponse,
          responses={500: {"model": ErrorResponse}})
async def provide_feedback(feedback: FeedbackRequest):
    """
    Provide feedback on recommendations to improve the AI model
    """
    try:
        success = recommendation_service.process_feedback(
            feedback.dict(),
            request_id=feedback.request_id,
            send_callback=feedback.send_callback
        )
        
        if success:
            return FeedbackResponse(message="Feedback received successfully. Thank you for helping us improve!")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process feedback"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback processing failed: {str(e)}"
        )

@app.post("/model/retrain", 
          response_model=TrainingResponse,
          responses={500: {"model": ErrorResponse}})
async def retrain_model(request: RetrainRequest = None):
    """
    Retrain the recommendation model with current data
    """
    try:
        force = request.force_retrain if request else False
        start_time = datetime.now()
        
        success = recommendation_service.retrain_model(
            force=force,
            request_id=request.request_id if request else None,
            send_callback=request.send_callback if request else True
        )
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        if success:
            return TrainingResponse(
                success=True,
                message="Model trained successfully",
                internships_count=len(recommendation_service.model.internship_data),
                training_time_seconds=training_time
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model training failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for service monitoring
    """
    model_info = recommendation_service.get_model_info()
    
    return HealthResponse(
        status="healthy",
        service="recommendation-engine",
        model_loaded=recommendation_service.model.is_trained,
        internships_count=model_info["internships_count"],
        timestamp=datetime.now().isoformat()
    )

@app.get("/model/info", response_model=ModelInfoResponse)
async def model_info():
    """
    Get information about the current AI model
    """
    model_info = recommendation_service.get_model_info()
    
    return ModelInfoResponse(**model_info)


def _analyze_resume_logic(req: ResumeAnalyzeRequest) -> ResumeAnalyzeResponse:
    text = (req.resume_text or "").strip()
    suggestions = []

    def add(cat, msg, severity="info"):
        suggestions.append(ResumeAnalyzeSuggestion(category=cat, message=msg, severity=severity))

    # Basic checks
    if len(text) < 400:
        add("Length", "Your resume appears short. Consider adding more details about projects, impact, and technologies.", "warn")
    if len(text) > 2000:
        add("Length", "Your resume may be too long. Aim for 1 page for students/early career.", "warn")

    # Contact info presence
    if ("@" not in text) and ("email" not in text.lower()):
        add("Contact", "Add a professional email at the top.", "critical")

    # Action verbs
    action_verbs = ["built", "developed", "designed", "implemented", "led", "optimized", "automated", "analyzed"]
    if not any(v in text.lower() for v in action_verbs):
        add("Language", "Use strong action verbs (e.g., built, developed, designed) in bullet points.")

    # Quantification
    import re
    has_numbers = re.search(r"\b\d+%?|\b\d+\b", text)
    if not has_numbers:
        add("Impact", "Quantify results (e.g., improved load time by 30%, reduced errors by 15%).")

    # Skills alignment
    if req.skills:
        missing_keywords = [s for s in req.skills if s.lower() not in text.lower()]
        if missing_keywords:
            add("Skills", f"Consider reflecting key skills in bullets where relevant: {', '.join(missing_keywords[:6])}.")

    # Interests alignment
    if req.interests:
        if not any(i.lower() in text.lower() for i in req.interests):
            add("Focus", f"Align your summary or projects with interests: {', '.join(req.interests[:3])}.")

    # Education
    if req.education_level and req.education_level.lower() not in text.lower():
        add("Education", "Include your degree level clearly in the Education section.")
    if req.college_name and req.college_name.lower() not in text.lower():
        add("Education", "Include your college/university name in Education.")

    # Simple scoring (heuristic)
    score = 70.0
    for s in suggestions:
        if s.severity == "critical":
            score -= 10
        elif s.severity == "warn":
            score -= 5

    score = max(0.0, min(100.0, score))
    return ResumeAnalyzeResponse(suggestions=suggestions, score=score, analyzed_at=datetime.now().isoformat())


@app.post("/resume/analyze", response_model=ResumeAnalyzeResponse, responses={500: {"model": ErrorResponse}})
async def analyze_resume(req: ResumeAnalyzeRequest):
    try:
        return _analyze_resume_logic(req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Resume analysis failed: {str(e)}")



@app.get("/internships/count")
async def get_internships_count():
    """
    Get count of internships in the model
    """
    model_info = recommendation_service.get_model_info()
    
    return {
        "internships_count": model_info["internships_count"],
        "timestamp": datetime.now().isoformat()
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=str(exc) if exc.status_code == 500 else None,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )