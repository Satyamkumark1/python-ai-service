#!/usr/bin/env python3
"""
Training script for the PM Internship Recommendation Model
Run this to train and test the AI model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.recommendation_model import RecommendationModel
from app.utils.data_loader import load_sample_data, create_sample_student
import joblib

def main():
    print("🚀 Training PM Internship Recommendation Model...")
    print("=" * 50)
    
    # 1. Load training data
    print("📊 Loading training data...")
    internships_data = load_sample_data()
    print(f"✅ Loaded {len(internships_data)} internships")
    
    # 2. Initialize and train model
    print("🧠 Training model...")
    model = RecommendationModel()
    model.train(internships_data)
    
    # 3. Save model
    os.makedirs("trained_models", exist_ok=True)
    model.save("trained_models/recommendation_model.joblib")
    print("💾 Model saved successfully")
    
    # 4. Test with sample student
    print("\n🧪 Testing model with sample student...")
    sample_student = create_sample_student()
    
    recommendations = model.recommend(sample_student, top_n=3)
    
    print("\n🎯 Sample Recommendations:")
    print("=" * 50)
    for i, (internship_id, score, reason) in enumerate(recommendations, 1):
        internship = model.internship_data[internship_id]
        print(f"{i}. {internship['title']} at {internship['organization']}")
        print(f"   📍 Location: {internship['location']}")
        print(f"   🎯 Score: {score:.2%}")
        print(f"   📝 Reason: {reason}")
        print(f"   🔧 Skills: {', '.join(internship['required_skills'][:3])}")
        print()
    
    print("✅ Model training and testing completed successfully!")

if __name__ == "__main__":
    main()