import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import joblib
from .feature_engineering import FeatureEngineer

class RecommendationModel:
    """
    Main AI model for generating internship recommendations
    Uses content-based filtering with feature engineering
    """
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.internship_features = {}  # Stores feature vectors for each internship
        self.internship_data = {}      # Stores original internship data
        self.is_trained = False
        
    def train(self, internships_data: List[Dict[str, Any]]):
        """
        Train the recommendation model on internship data
        """
        print("🧠 Training recommendation model...")
        
        # 1. Fit feature engineering pipeline
        self.feature_engineer.fit(internships_data)
        
        # 2. Transform all internships to feature vectors
        self.internship_features = {}
        self.internship_data = {}
        
        for internship in internships_data:
            internship_id = internship['id']
            features = self.feature_engineer.transform_internship(internship)
            self.internship_features[internship_id] = features
            self.internship_data[internship_id] = internship
        
        self.is_trained = True
        print(f"✅ Model trained on {len(internships_data)} internships")
    
    def recommend(self, student_data: Dict[str, Any], top_n: int = 5) -> List[Tuple[int, float, str]]:
        """
        Generate recommendations for a student
        Returns: list of (internship_id, score, reason)
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # 1. Convert student to feature vector
        student_features = self.feature_engineer.transform_student(student_data)
        
        # 2. Calculate similarity with all internships
        similarities = []
        for internship_id, internship_features in self.internship_features.items():
            similarity = self._calculate_similarity(student_features, internship_features)
            reason = self._generate_reason(student_data, self.internship_data[internship_id], similarity)
            similarities.append((internship_id, similarity, reason))
        
        # 3. Sort by similarity and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    
    def _calculate_similarity(self, student_features: np.ndarray, internship_features: np.ndarray) -> float:
        """
        Calculate similarity score between student and internship
        Uses weighted combination of different factors
        """
        # 1. Cosine similarity for text features (skills, interests, description)
        cosine_sim = cosine_similarity(
            student_features[1:].reshape(1, -1),  # Skip first numeric feature
            internship_features[1:].reshape(1, -1)
        )[0][0]
        
        # 2. Education level match (first feature)
        education_match = 1.0 if student_features[0] == internship_features[0] else 0.5
        
        # 3. Combined score with weights
        final_score = (0.7 * cosine_sim) + (0.3 * education_match)
        
        # 4. Apply first-generation learner bonus
        # This would be implemented based on student_data
        
        return min(max(final_score, 0.0), 1.0)  # Ensure score between 0-1
    
    def _generate_reason(self, student_data: Dict[str, Any], 
                        internship_data: Dict[str, Any], 
                        similarity: float) -> str:
        """
        Generate human-readable explanation for the recommendation
        """
        reasons = []
        
        # 1. Skill matching
        student_skills = set(student_data.get('skills', []))
        internship_skills = set(internship_data.get('required_skills', []))
        common_skills = student_skills.intersection(internship_skills)
        
        if common_skills:
            reasons.append(f"Matches {len(common_skills)} required skills: {', '.join(list(common_skills)[:3])}")
        
        # 2. Interest matching
        student_interests = set(student_data.get('interests', []))
        if internship_data.get('category') in student_interests:
            reasons.append(f"Matches your interest in {internship_data['category']}")
        
        # 3. Location preference
        preferred_location = student_data.get('preferred_location')
        internship_location = internship_data.get('location')
        if preferred_location and internship_location:
            if preferred_location.lower() == internship_location.lower():
                reasons.append("Matches your preferred location")
            elif preferred_location.lower() in internship_location.lower():
                reasons.append("Partially matches your location preference")
        
        # 4. First-gen learner encouragement
        if student_data.get('is_first_gen_learner', False) and similarity > 0.7:
            reasons.append("Great opportunity for first-generation learners!")
        
        # 5. Education level match
        student_edu = student_data.get('education_level', '')
        internship_edu = internship_data.get('education_requirement', '')
        if student_edu and internship_edu and student_edu == internship_edu:
            reasons.append("Matches your education level")
        
        return ". ".join(reasons) if reasons else "Recommended based on your profile"
    
    def save(self, filepath: str):
        """Save the trained model to disk"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        joblib.dump({
            'internship_features': self.internship_features,
            'internship_data': self.internship_data,
            'feature_engineer': self.feature_engineer
        }, filepath)
        print(f"💾 Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load a trained model from disk"""
        saved_data = joblib.load(filepath)
        self.internship_features = saved_data['internship_features']
        self.internship_data = saved_data['internship_data']
        self.feature_engineer = saved_data['feature_engineer']
        self.is_trained = True
        print(f"📂 Model loaded from {filepath}")
        