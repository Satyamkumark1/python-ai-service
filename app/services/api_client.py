import requests
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpringBootAPIClient:
    """Client for communicating with Spring Boot backend APIs"""
    
    def __init__(self):
        # Configuration for Spring Boot API endpoints
        self.base_url = os.getenv('SPRING_BOOT_BASE_URL', 'http://localhost:8080')
        self.internships_endpoint = os.getenv('INTERNSHIPS_ENDPOINT', '/api/internships')
        self.students_endpoint = os.getenv('STUDENTS_ENDPOINT', '/api/students')
        self.timeout = int(os.getenv('API_TIMEOUT', '30'))
        
        # Headers for API requests
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add authentication if needed
        api_key = os.getenv('SPRING_BOOT_API_KEY')
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def get_all_internships(self) -> List[Dict[str, Any]]:
        """
        Fetch all internships from Spring Boot backend
        """
        try:
            url = f"{self.base_url}{self.internships_endpoint}"
            logger.info(f"Fetching internships from: {url}")
            
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            internships = response.json()
            logger.info(f"Successfully fetched {len(internships)} internships from Spring Boot API")
            
            # Transform the data to match our expected format
            return self._transform_internships_data(internships)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch internships from Spring Boot API: {e}")
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing internships data: {e}")
            raise Exception(f"Data processing failed: {str(e)}")
    
    def get_internship_by_id(self, internship_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific internship by ID from Spring Boot backend
        """
        try:
            url = f"{self.base_url}{self.internships_endpoint}/{internship_id}"
            logger.info(f"Fetching internship {internship_id} from: {url}")
            
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            internship = response.json()
            return self._transform_internship_data(internship)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch internship {internship_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing internship data: {e}")
            return None
    
    def get_student_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific student profile by ID from Spring Boot backend
        """
        try:
            url = f"{self.base_url}{self.students_endpoint}/{student_id}"
            logger.info(f"Fetching student {student_id} from: {url}")
            
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            student = response.json()
            return self._transform_student_data(student)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch student {student_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing student data: {e}")
            return None
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """
        Fetch all students from Spring Boot backend
        """
        try:
            url = f"{self.base_url}{self.students_endpoint}"
            logger.info(f"Fetching students from: {url}")
            
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            students = response.json()
            logger.info(f"Successfully fetched {len(students)} students from Spring Boot API")
            
            # Transform the data to match our expected format
            return self._transform_students_data(students)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch students from Spring Boot API: {e}")
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing students data: {e}")
            raise Exception(f"Data processing failed: {str(e)}")
    
    def _transform_internships_data(self, internships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform internships data from Spring Boot API format to our expected format
        """
        transformed = []
        for internship in internships:
            transformed.append(self._transform_internship_data(internship))
        return transformed
    
    def _transform_internship_data(self, internship: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single internship from Spring Boot API format to our expected format
        """
        return {
            "id": internship.get("id"),
            "title": internship.get("title", ""),
            "description": internship.get("description", ""),
            "required_skills": self._parse_skills(internship.get("requiredSkills", [])),
            "preferred_skills": self._parse_skills(internship.get("preferredSkills", [])),
            "category": internship.get("category", ""),
            "location": internship.get("location", ""),
            "state": internship.get("state"),
            "organization": internship.get("organization", ""),
            "education_requirement": internship.get("educationRequirement", ""),
            "created_at": internship.get("createdAt"),
            "updated_at": internship.get("updatedAt")
        }
    
    def _transform_students_data(self, students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform students data from Spring Boot API format to our expected format
        """
        transformed = []
        for student in students:
            transformed.append(self._transform_student_data(student))
        return transformed
    
    def _transform_student_data(self, student: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single student from Spring Boot API format to our expected format
        """
        return {
            "student_id": student.get("id"),
            "name": student.get("name", ""),
            "email": student.get("email", ""),
            "education_level": student.get("educationLevel", ""),
            "skills": self._parse_skills(student.get("skills", [])),
            "interests": self._parse_skills(student.get("interests", [])),
            "preferred_location": student.get("preferredLocation", ""),
            "preferred_state": student.get("preferredState"),
            "is_first_gen_learner": student.get("isFirstGenLearner", False),
            "created_at": student.get("createdAt"),
            "updated_at": student.get("updatedAt")
        }
    
    def _parse_skills(self, skills_data) -> List[str]:
        """
        Parse skills data which could be a list, string, or comma-separated string
        """
        if isinstance(skills_data, list):
            return [str(skill).strip() for skill in skills_data if skill]
        elif isinstance(skills_data, str):
            if skills_data.startswith('[') and skills_data.endswith(']'):
                # Try to parse as JSON array
                try:
                    import json
                    return json.loads(skills_data)
                except:
                    pass
            # Split by comma
            return [skill.strip() for skill in skills_data.split(',') if skill.strip()]
        else:
            return []
    
    def health_check(self) -> bool:
        """
        Check if the Spring Boot API is accessible
        """
        try:
            # Try to hit a health endpoint or the base URL
            health_url = f"{self.base_url}/actuator/health"
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except:
            # If health endpoint doesn't exist, try the base URL
            try:
                response = requests.get(self.base_url, timeout=5)
                return response.status_code in [200, 404]  # 404 is ok if base URL doesn't have a root endpoint
            except:
                return False
