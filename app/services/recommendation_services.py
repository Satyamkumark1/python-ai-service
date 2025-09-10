import joblib
import os
from typing import List, Dict, Any
from datetime import datetime
from ..models.recommendation_model import RecommendationModel
from ..utils.data_loader import load_sample_data

class RecommendationService:
    """Service layer for recommendation operations"""
    
    def __init__(self):
        self.model = RecommendationModel()
        self.model_path = "trained_models/recommendation_model.joblib"
        self.model_version = "v1.0"
        self.last_trained = None
        
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
    
    def retrain_model(self, force: bool = False) -> bool:
        """Retrain the model with current data"""
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
            
            return True
            
        except Exception as e:
            print(f"❌ Model training failed: {e}")
            return False
    
    def get_recommendations(self, student_data: Dict[str, Any], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get recommendations for a student"""
        if not self.model.is_trained:
            raise ValueError("Model not trained. Please retrain the model first.")
        
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
                "location": internship.get('location', '')
            })
        
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
    
    def process_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Process user feedback on recommendations"""
        # In a real implementation, this would:
        # 1. Store feedback in database
        # 2. Use it for model improvement
        # 3. Update recommendation algorithms
        
        print(f"📝 Received feedback: {feedback_data}")
        # TODO: Implement feedback processing and model improvement
        return True