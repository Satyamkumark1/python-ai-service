import pandas as pd
import ast
import os
from typing import List, Dict, Any
from ..services.api_client import SpringBootAPIClient

def load_sample_data() -> List[Dict[str, Any]]:
    """
    Load internship data from Spring Boot backend API
    Falls back to CSV file if API is not available
    """
    # Try to load from Spring Boot API first
    try:
        api_client = SpringBootAPIClient()
        
        # Check if API is available
        if api_client.health_check():
            print("🌐 Spring Boot API is available, fetching internships...")
            internships = api_client.get_all_internships()
            print(f"📊 Loaded {len(internships)} internships from Spring Boot API")
            return internships
        else:
            print("⚠️  Spring Boot API is not available, falling back to CSV...")
            return _load_from_csv()
            
    except Exception as e:
        print(f"❌ Error connecting to Spring Boot API: {e}")
        print("🔄 Falling back to CSV file...")
        return _load_from_csv()

def _load_from_csv() -> List[Dict[str, Any]]:
    """
    Load internship data from CSV file as fallback
    """
    # Get the path to the CSV file relative to the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    csv_path = os.path.join(project_root, "data", "sample_internships.csv")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Convert DataFrame to list of dictionaries
        internships = []
        for _, row in df.iterrows():
            # Skip rows where id is not numeric (like header row)
            try:
                internship_id = int(row['id'])
            except (ValueError, TypeError):
                continue
                
            # Parse skills lists from string representation
            try:
                required_skills = ast.literal_eval(row['required_skills']) if pd.notna(row['required_skills']) else []
            except (ValueError, SyntaxError):
                # If parsing fails, split by comma and clean up
                required_skills = [skill.strip().strip("'\"") for skill in str(row['required_skills']).split(',')] if pd.notna(row['required_skills']) else []
            
            try:
                preferred_skills = ast.literal_eval(row['preferred_skills']) if pd.notna(row['preferred_skills']) else []
            except (ValueError, SyntaxError):
                # If parsing fails, split by comma and clean up
                preferred_skills = [skill.strip().strip("'\"") for skill in str(row['preferred_skills']).split(',')] if pd.notna(row['preferred_skills']) else []
            
            internship = {
                "id": internship_id,
                "title": str(row['title']),
                "description": str(row['description']),
                "required_skills": required_skills,
                "preferred_skills": preferred_skills,
                "category": str(row['category']),
                "location": str(row['location']),
                "state": str(row['state']) if pd.notna(row['state']) else None,
                "organization": str(row['organization']),
                "education_requirement": str(row['education_requirement'])
            }
            internships.append(internship)
        
        print(f"📊 Loaded {len(internships)} internships from CSV file")
        return internships
        
    except FileNotFoundError:
        print(f"❌ CSV file not found at {csv_path}")
        print("🔄 Falling back to hardcoded sample data...")
        return _get_fallback_data()
    except Exception as e:
        print(f"❌ Error loading CSV file: {e}")
        print("🔄 Falling back to hardcoded sample data...")
        return _get_fallback_data()

def _get_fallback_data() -> List[Dict[str, Any]]:
    """
    Fallback hardcoded data in case CSV loading fails
    """
    return [
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
        }
    ]

def load_student_data(student_id: int = None) -> Dict[str, Any]:
    """
    Load student data from Spring Boot backend API
    Falls back to sample data if API is not available
    """
    if student_id is None:
        return create_sample_student()
    
    # Try to load from Spring Boot API first
    try:
        api_client = SpringBootAPIClient()
        
        # Check if API is available
        if api_client.health_check():
            print(f"🌐 Spring Boot API is available, fetching student {student_id}...")
            student = api_client.get_student_by_id(student_id)
            if student:
                print(f"📊 Loaded student {student_id} from Spring Boot API")
                return student
            else:
                print(f"⚠️  Student {student_id} not found in API, using sample data...")
                return create_sample_student()
        else:
            print("⚠️  Spring Boot API is not available, using sample data...")
            return create_sample_student()
            
    except Exception as e:
        print(f"❌ Error connecting to Spring Boot API: {e}")
        print("🔄 Using sample student data...")
        return create_sample_student()

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