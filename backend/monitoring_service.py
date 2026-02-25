import os
import json
import datetime
import logging

class MonitoringService:
    """Service for monitoring and logging RAG interactions."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        self.log_file = os.path.join(log_dir, "interactions.jsonl")
        
        # Configure logging
        self.logger = logging.getLogger("rag_monitor")
        self.logger.setLevel(logging.INFO)
        
    def log_interaction(self, 
                        query: str, 
                        response: str, 
                        source_type: str, 
                        sources: list, 
                        latency_ms: float = 0.0,
                        feedback: str = None):
        """
        Log a single chat user interaction.
        """
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": query,
            "response_snippet": response[:100] + "..." if len(response) > 100 else response,
            "source_type": source_type,
            "sources": sources,
            "latency_ms": round(latency_ms, 2),
            "feedback": feedback
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"Error logging interaction: {e}")

# Singleton
_monitoring_service = None

def get_monitoring_service():
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
