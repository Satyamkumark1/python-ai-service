import joblib
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.recommendation_model import RecommendationModel
from ..utils.data_loader import load_sample_data, load_student_data
from .callback_service import SpringBootCallbackService

class RecommendationService:
    """Service layer for recommendation operations"""
    
    def __init__(self):
        self.model = RecommendationModel()
        self.model_path = "trained_models/recommendation_model.joblib"
        self.model_version = "v1.0"
        self.last_trained = None
        self.callback_service = SpringBootCallbackService()
        
    def initialize_model(self):
        """Initialize the model on service startup"""
        try:
            if os.path.exists(self.model_path):
                self.model.load(self.model_path)
                print("✅ Loaded pre-trained model")
                self.last_trained = datetime.now().isoformat()
                return True
            else:
                print("⚠️  No pre-trained model found. Training new model...")
                return self.retrain_model()
        except Exception as e:
            print(f"❌ Model initialization failed: {e}")
            return False
    
    def retrain_model(self, force: bool = False, 
                     request_id: Optional[str] = None,
                     send_callback: bool = True) -> bool:
        """Retrain the model with current data and optionally send callback to Spring Boot"""
        try:
            if not force and os.path.exists(self.model_path):
                print("✅ Model already exists. Use force=True to retrain.")
                return True
                
            print("🧠 Training new model...")
            start_time = datetime.now()
            
            # Load training data (in production, this would come from database)
            internships_data = load_sample_data()
            
            # Train model
            self.model.train(internships_data)
            # Ensure model directory exists
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.model.save(self.model_path)
            
            self.last_trained = datetime.now().isoformat()
            training_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ Model trained successfully in {training_time:.2f} seconds")
            print(f"📊 Trained on {len(internships_data)} internships")
            
            # Send callback to Spring Boot if enabled and callback service is available
            if send_callback and self.callback_service.is_callback_enabled():
                try:
                    training_result = {
                        "success": True,
                        "training_time_seconds": training_time,
                        "internships_count": len(internships_data),
                        "model_version": self.model_version,
                        "last_trained": self.last_trained
                    }
                    
                    callback_success = self.callback_service.send_model_training_callback(
                        training_result=training_result,
                        request_id=request_id
                    )
                    
                    if callback_success:
                        print(f"📤 Successfully sent model training callback to Spring Boot")
                    else:
                        print(f"⚠️  Failed to send model training callback to Spring Boot")
                        
                except Exception as e:
                    print(f"⚠️  Error sending model training callback: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Model training failed: {e}")
            
            # Send failure callback to Spring Boot if enabled
            if send_callback and self.callback_service.is_callback_enabled():
                try:
                    training_result = {
                        "success": False,
                        "error": str(e),
                        "model_version": self.model_version
                    }
                    
                    self.callback_service.send_model_training_callback(
                        training_result=training_result,
                        request_id=request_id
                    )
                except Exception as callback_error:
                    print(f"⚠️  Error sending training failure callback: {callback_error}")
            
            return False
    
    def get_recommendations(self, student_data: Dict[str, Any], top_n: int = 5, 
                          request_id: Optional[str] = None, 
                          send_callback: bool = True) -> List[Dict[str, Any]]:
        """Get recommendations for a student and optionally send callback to Spring Boot"""
        if not self.model.is_trained:
            raise ValueError("Model not trained. Please retrain the model first.")
        
        # If student_data contains a student_id, try to load from API
        if 'student_id' in student_data and student_data['student_id']:
            try:
                api_student_data = load_student_data(student_data['student_id'])
                # Merge API data with provided data (provided data takes precedence)
                merged_data = {**api_student_data, **student_data}
                student_data = merged_data
            except Exception as e:
                print(f"⚠️  Could not load student from API: {e}, using provided data")
        
        recommendations = self.model.recommend(student_data, top_n)
        
        # Format recommendations with additional info
        formatted_recommendations = []
        for internship_id, score, reason in recommendations:
            internship = self.model.internship_data[internship_id]
            formatted_recommendations.append({
                "internship_id": internship_id,
                "score": round(score * 100, 2),  # Convert to percentage
                "reason": reason,
                "title": internship.get('title', ''),
                "organization": internship.get('organization', ''),
                "location": internship.get('location', ''),
                "description": internship.get('description', ''),
                "required_skills": internship.get('required_skills', []),
                "preferred_skills": internship.get('preferred_skills', [])
            })
        
        # Send callback to Spring Boot if enabled and callback service is available
        if send_callback and self.callback_service.is_callback_enabled():
            try:
                student_id = student_data.get('student_id')
                if student_id:
                    # Prepare metadata for callback
                    metadata = {
                        "total_recommendations": len(formatted_recommendations),
                        "model_version": self.model_version,
                        "top_n": top_n,
                        "student_education": student_data.get('education_level'),
                        "student_skills": student_data.get('skills', []),
                        "student_interests": student_data.get('interests', [])
                    }
                    
                    # Send callback asynchronously (don't wait for response)
                    callback_success = self.callback_service.send_recommendations_callback(
                        student_id=student_id,
                        recommendations=formatted_recommendations,
                        request_id=request_id,
                        metadata=metadata
                    )
                    
                    if callback_success:
                        print(f"📤 Successfully sent recommendations callback to Spring Boot for student {student_id}")
                    else:
                        print(f"⚠️  Failed to send recommendations callback to Spring Boot for student {student_id}")
                        
            except Exception as e:
                print(f"⚠️  Error sending recommendations callback: {e}")
        
        return formatted_recommendations
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if not self.model.is_trained:
            return {
                "internships_count": 0,
                "feature_dimension": 0,
                "model_version": self.model_version,
                "last_trained": self.last_trained
            }
        
        return {
            "internships_count": len(self.model.internship_data),
            "feature_dimension": len(next(iter(self.model.internship_features.values()))) 
                                if self.model.internship_features else 0,
            "model_version": self.model_version,
            "last_trained": self.last_trained
        }
    
    def process_feedback(self, feedback_data: Dict[str, Any], 
                        request_id: Optional[str] = None,
                        send_callback: bool = True) -> bool:
        """Process user feedback on recommendations and optionally send callback to Spring Boot"""
        # In a real implementation, this would:
        # 1. Store feedback in database
        # 2. Use it for model improvement
        # 3. Update recommendation algorithms
        
        print(f"📝 Received feedback: {feedback_data}")
        
        # Send callback to Spring Boot if enabled and callback service is available
        if send_callback and self.callback_service.is_callback_enabled():
            try:
                callback_success = self.callback_service.send_feedback_callback(
                    feedback_data=feedback_data,
                    request_id=request_id
                )
                
                if callback_success:
                    print(f"📤 Successfully sent feedback callback to Spring Boot")
                else:
                    print(f"⚠️  Failed to send feedback callback to Spring Boot")
                    
            except Exception as e:
                print(f"⚠️  Error sending feedback callback: {e}")
        
        # TODO: Implement feedback processing and model improvement
        return True