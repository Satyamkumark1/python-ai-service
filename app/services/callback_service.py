import requests
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpringBootCallbackService:
    """Service for sending responses back to Spring Boot backend"""
    
    def __init__(self):
        self.config = Config()
        self.timeout = self.config.API_TIMEOUT
        
        # Headers for API requests
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add authentication if needed
        if self.config.SPRING_BOOT_API_KEY:
            self.headers['Authorization'] = f'Bearer {self.config.SPRING_BOOT_API_KEY}'
    
    def send_recommendations_callback(self, 
                                    student_id: int, 
                                    recommendations: list, 
                                    request_id: Optional[str] = None,
                                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send recommendations response back to Spring Boot backend
        
        Args:
            student_id: ID of the student who requested recommendations
            recommendations: List of recommendation objects
            request_id: Optional request ID for tracking
            metadata: Optional additional metadata
            
        Returns:
            bool: True if callback was successful, False otherwise
        """
        try:
            callback_url = self.config.get_recommendations_callback_url()
            
            # Prepare callback payload
            callback_payload = {
                "studentId": student_id,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
                "source": "ai-recommendation-service",
                "version": self.config.MODEL_VERSION
            }
            
            # Add optional fields
            if request_id:
                callback_payload["requestId"] = request_id
            
            if metadata:
                callback_payload["metadata"] = metadata
            
            logger.info(f"📤 Sending recommendations callback to: {callback_url}")
            logger.info(f"📊 Callback payload: {len(recommendations)} recommendations for student {student_id}")
            
            response = requests.post(
                callback_url,
                json=callback_payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            logger.info(f"✅ Successfully sent recommendations callback to Spring Boot")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to send recommendations callback: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error in recommendations callback: {e}")
            return False
    
    def send_feedback_callback(self, 
                             feedback_data: Dict[str, Any],
                             request_id: Optional[str] = None) -> bool:
        """
        Send feedback response back to Spring Boot backend
        
        Args:
            feedback_data: Feedback data from the user
            request_id: Optional request ID for tracking
            
        Returns:
            bool: True if callback was successful, False otherwise
        """
        try:
            callback_url = self.config.get_feedback_callback_url()
            
            # Prepare callback payload
            callback_payload = {
                "feedback": feedback_data,
                "timestamp": datetime.now().isoformat(),
                "source": "ai-recommendation-service",
                "version": self.config.MODEL_VERSION
            }
            
            # Add optional fields
            if request_id:
                callback_payload["requestId"] = request_id
            
            logger.info(f"📤 Sending feedback callback to: {callback_url}")
            
            response = requests.post(
                callback_url,
                json=callback_payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            logger.info(f"✅ Successfully sent feedback callback to Spring Boot")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to send feedback callback: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error in feedback callback: {e}")
            return False
    
    def send_model_training_callback(self, 
                                   training_result: Dict[str, Any],
                                   request_id: Optional[str] = None) -> bool:
        """
        Send model training result back to Spring Boot backend
        
        Args:
            training_result: Result of the model training
            request_id: Optional request ID for tracking
            
        Returns:
            bool: True if callback was successful, False otherwise
        """
        try:
            # Use recommendations callback endpoint for training results
            callback_url = self.config.get_recommendations_callback_url()
            
            # Prepare callback payload
            callback_payload = {
                "type": "model_training",
                "trainingResult": training_result,
                "timestamp": datetime.now().isoformat(),
                "source": "ai-recommendation-service",
                "version": self.config.MODEL_VERSION
            }
            
            # Add optional fields
            if request_id:
                callback_payload["requestId"] = request_id
            
            logger.info(f"📤 Sending model training callback to: {callback_url}")
            
            response = requests.post(
                callback_url,
                json=callback_payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            logger.info(f"✅ Successfully sent model training callback to Spring Boot")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to send model training callback: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error in model training callback: {e}")
            return False
    
    def is_callback_enabled(self) -> bool:
        """
        Check if callback functionality is enabled
        (i.e., Spring Boot API is available)
        """
        try:
            # Try to hit the base URL to check if Spring Boot is available
            response = requests.get(
                self.config.SPRING_BOOT_BASE_URL, 
                timeout=5
            )
            return response.status_code in [200, 404]  # 404 is ok if base URL doesn't have a root endpoint
        except:
            return False
    
    def send_health_status_callback(self, 
                                  health_data: Dict[str, Any]) -> bool:
        """
        Send health status to Spring Boot backend (for monitoring)
        
        Args:
            health_data: Health check data
            
        Returns:
            bool: True if callback was successful, False otherwise
        """
        try:
            callback_url = self.config.get_recommendations_callback_url()
            
            # Prepare callback payload
            callback_payload = {
                "type": "health_status",
                "healthData": health_data,
                "timestamp": datetime.now().isoformat(),
                "source": "ai-recommendation-service",
                "version": self.config.MODEL_VERSION
            }
            
            logger.info(f"📤 Sending health status callback to: {callback_url}")
            
            response = requests.post(
                callback_url,
                json=callback_payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            logger.info(f"✅ Successfully sent health status callback to Spring Boot")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to send health status callback: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error in health status callback: {e}")
            return False
