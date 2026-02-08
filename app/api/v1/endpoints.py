from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid

from app.models.schemas import ClinicalInput, AssessmentResponse
from app.core.ml_service import MLRiskEngine
from app.core.storage import LocalStorage

router = APIRouter()
storage = LocalStorage()

# Initialize ML Engine (Load logic once)
try:
    risk_engine = MLRiskEngine()
except Exception as e:
    print(f"WARNING: ML Engine failed to load: {e}")
    risk_engine = None

@router.post("/assess", response_model=AssessmentResponse)
async def assess_clinical_risk(input_data: ClinicalInput):
    """
    Perform population-level risk estimation using NHANES-trained models.
    """
    if not risk_engine:
        raise HTTPException(status_code=503, detail="Risk Engine not initialized. Models missing.")

    try:
        # 1. ML Inference
        risks = risk_engine.assess(input_data)
        
        # 2. Construct Response
        response = AssessmentResponse(
            assessment_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            risks=risks
        )
        
        # 3. Privacy-Preserving Store (Encrypted)
        storage.save_assessment(response)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

@router.post("/chat", response_model=dict)
async def chat_with_assistant(chat_msg: dict):
    """
    Chat with AI health assistant using LLM.
    """
    from app.models.schemas import ChatMessage, ChatResponse
    from app.core.llm_service import LLMService
    
    try:
        llm_service = LLMService()
        
        # Extract message and context
        user_message = chat_msg.get("message", "")
        assessment_id = chat_msg.get("assessment_id")
        history = chat_msg.get("conversation_history", [])
        
        # Get AI response
        ai_response = llm_service.chat(
            user_message=user_message,
            conversation_history=history,
            assessment_id=assessment_id
        )
        
        return {
            "response": ai_response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
