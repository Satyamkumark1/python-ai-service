import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import re
from typing import List, Dict, Any
import joblib

class FeatureEngineer:
    """
    Transforms raw student and internship data into numerical features
    for machine learning models.
    """
    
    def __init__(self):
        # TF-IDF for text features
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,        # Limit vocabulary size
            stop_words='english',     # Remove common words
            ngram_range=(1, 2)        # Consider single words and pairs
        )
        
        # Dimensionality reduction
        self.svd = TruncatedSVD(n_components=50)  # Reduce to 50 features
        
    def preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text data by:
        1. Converting to lowercase
        2. Removing special characters  
        3. Removing extra spaces
        """
        if pd.isna(text):
            return ""
        
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)  # Remove special chars
        text = re.sub(r'\s+', ' ', text).strip()     # Remove extra spaces
        return text
    
    def create_student_features(self, student_data: Dict[str, Any]) -> tuple:
        """
        Convert student profile into feature vector
        Returns: (numeric_features, text_features)
        """
        features = []
        
        # 1. Education level encoding
        education_mapping = {
            'Class 12': 0, 'Diploma': 1, 'B.Tech': 2, 'B.Sc': 3, 
            'B.A': 4, 'M.Tech': 5, 'M.Sc': 6, 'Ph.D': 7
        }
        education_feature = education_mapping.get(
            student_data.get('education_level', 'Class 12'), 0
        )
        features.append(education_feature)
        
        # 2. Convert skills and interests to text
        skills_text = ' '.join(student_data.get('skills', []))
        skills_processed = self.preprocess_text(skills_text)
        
        interests_text = ' '.join(student_data.get('interests', []))
        interests_processed = self.preprocess_text(interests_text)
        
        # 3. Combined text features
        combined_text = f"{skills_processed} {interests_processed}"
        
        return np.array(features), combined_text
    
    def create_internship_features(self, internship_data: Dict[str, Any]) -> tuple:
        """
        Convert internship data into feature vector  
        Returns: (numeric_features, text_features)
        """
        features = []

        # 1. Education level encoding (to match student's numeric feature)
        education_mapping = {
            'Class 12': 0, 'Diploma': 1, 'B.Tech': 2, 'B.Sc': 3,
            'B.A': 4, 'M.Tech': 5, 'M.Sc': 6, 'Ph.D': 7
        }
        education_feature = education_mapping.get(
            internship_data.get('education_requirement', 'Class 12'), 0
        )
        features.append(education_feature)

        # 2. Text features from title, description, skills, category, and location
        title_text = self.preprocess_text(internship_data.get('title', ''))
        desc_text = self.preprocess_text(internship_data.get('description', ''))
        skills_text = ' '.join(internship_data.get('required_skills', []))
        skills_processed = self.preprocess_text(skills_text)

        category_text = self.preprocess_text(internship_data.get('category', ''))
        location_text = self.preprocess_text(internship_data.get('location', ''))

        combined_text = f"{title_text} {desc_text} {skills_processed} {category_text} {location_text}"

        return np.array(features), combined_text
    
    def fit(self, internships_data: List[Dict[str, Any]]):
        """
        Train the feature engineering pipeline on internship data
        """
        all_texts = []
        for internship in internships_data:
            _, text_features = self.create_internship_features(internship)
            all_texts.append(text_features)
        
        # 1. Fit TF-IDF vectorizer on internship text
        self.tfidf_vectorizer.fit(all_texts)
        
        # 2. Fit dimensionality reduction
        text_vectors = self.tfidf_vectorizer.transform(all_texts)
        self.svd.fit(text_vectors)
    
    def transform_student(self, student_data: Dict[str, Any]) -> np.ndarray:
        """
        Convert student data to feature vector for prediction
        """
        numeric_features, text_features = self.create_student_features(student_data)
        
        # Transform text features
        text_vector = self.tfidf_vectorizer.transform([text_features])
        text_reduced = self.svd.transform(text_vector)
        
        # Combine numeric and text features
        combined_features = np.concatenate([
            numeric_features.reshape(1, -1),  # Reshape to 2D
            text_reduced
        ], axis=1)
        
        return combined_features.flatten()
    
    def transform_internship(self, internship_data: Dict[str, Any]) -> np.ndarray:
        """
        Convert internship data to feature vector
        """
        numeric_features, text_features = self.create_internship_features(internship_data)
        
        # Transform text features
        text_vector = self.tfidf_vectorizer.transform([text_features])
        text_reduced = self.svd.transform(text_vector)
        
        # Combine features
        combined_features = np.concatenate([
            numeric_features.reshape(1, -1),
            text_reduced
        ], axis=1)
        
        return combined_features.flatten()
    
    def save(self, filepath: str):
        """Save the trained feature engineering pipeline"""
        joblib.dump({
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'svd': self.svd
        }, filepath)
    
    def load(self, filepath: str):
        """Load a trained feature engineering pipeline"""
        saved_data = joblib.load(filepath)
        self.tfidf_vectorizer = saved_data['tfidf_vectorizer']
        self.svd = saved_data['svd']