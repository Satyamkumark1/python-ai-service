import pandas as pd
from typing import List, Dict, Any

def load_sample_data() -> List[Dict[str, Any]]:
    """
    Load sample internship data for training and testing
    In production, this would connect to a database
    """
    sample_internships = [
        {
            "id": 1,
            "title": "Software Developer Intern",
            "description": "Develop web applications using Java and Spring Boot. Work on real projects with mentorship from senior developers.",
            "required_skills": ["Java", "Spring Boot", "SQL", "REST APIs"],
            "preferred_skills": ["Git", "Docker", "AWS"],
            "category": "IT",
            "location": "Bhubaneswar",
            "state": "Odisha",
            "organization": "Tech Solutions Ltd.",
            "education_requirement": "B.Tech"
        },
        {
            "id": 2,
            "title": "Data Science Intern",
            "description": "Work on machine learning projects using Python. Analyze data and build predictive models with real-world datasets.",
            "required_skills": ["Python", "Machine Learning", "Statistics", "Pandas"],
            "preferred_skills": ["TensorFlow", "SQL", "Data Visualization"],
            "category": "IT",
            "location": "Remote",
            "state": None,
            "organization": "Data Insights Inc.",
            "education_requirement": "B.Tech"
        },
        {
            "id": 3,
            "title": "Marketing Intern",
            "description": "Create digital marketing campaigns and social media content. Analyze campaign performance and suggest improvements.",
            "required_skills": ["Communication", "Social Media", "Content Writing"],
            "preferred_skills": ["SEO", "Analytics", "Creativity"],
            "category": "Marketing",
            "location": "Cuttack",
            "state": "Odisha",
            "organization": "Creative Minds Agency",
            "education_requirement": "B.A"
        },
        {
            "id": 4,
            "title": "Healthcare Intern",
            "description": "Support healthcare operations and patient care activities. Learn about hospital management and healthcare systems.",
            "required_skills": ["Communication", "Empathy", "Organization"],
            "preferred_skills": ["Medical Knowledge", "First Aid", "Record Keeping"],
            "category": "Healthcare",
            "location": "Bhubaneswar",
            "state": "Odisha",
            "organization": "City Hospital",
            "education_requirement": "B.Sc"
        },
        {
            "id": 5,
            "title": "Content Writing Intern",
            "description": "Create engaging content for blogs, social media, and marketing materials. Research topics and optimize content for SEO.",
            "required_skills": ["Writing", "Research", "Grammar"],
            "preferred_skills": ["SEO", "WordPress", "Social Media"],
            "category": "Content",
            "location": "Remote",
            "state": None,
            "organization": "Content Creators Co.",
            "education_requirement": "B.A"
        }
    ]
    
    return sample_internships

def create_sample_student() -> Dict[str, Any]:
    """
    Create a sample student profile for testing
    """
    return {
        "student_id": 202,
        "education_level": "B.A",
        "skills": ["Content Writing", "Social Media", "Creativity", "SEO"],
        "interests": ["Marketing", "Content"],
        "preferred_location": "Remote",
        "preferred_state": None,
        "is_first_gen_learner": False
    }