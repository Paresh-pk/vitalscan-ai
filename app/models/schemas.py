from pydantic import BaseModel, Field, conint, confloat
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

class RiskLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"

class Gender(int, Enum):
    MALE = 1
    FEMALE = 2

class ClinicalInput(BaseModel):
    # Demographics
    age: int = Field(..., ge=18, le=120, description="Age in years (NHANES: RIDAGEYR)")
    gender: Gender = Field(..., description="1=Male, 2=Female (NHANES: RIAGENDR)")
    
    # Measurements
    bmi: float = Field(..., ge=10, le=100, description="Body Mass Index (NHANES: BMXBMI)")
    systolic_bp: int = Field(..., ge=60, le=250, description="Systolic Blood Pressure (NHANES: BPXSY1)")
    
    # Labs (Optional - can be inferred or imputed in a real app, but required here for MVP)
    hba1c: float = Field(..., ge=3.0, le=20.0, description="Glycohemoglobin % (NHANES: LBXGH)")
    cholesterol: int = Field(..., ge=50, le=500, description="Total Cholesterol mg/dL (NHANES: LBXTC)")
    
    # Vitals (Preserved for ML Model)
    sleep_hours: float = Field(..., ge=0, le=24, description="Hours of sleep (Q10)")
    vigorous_activity: bool = Field(..., description="Exercise <3x/week? (Q9 reversed)")
    smoker_history: bool = Field(..., description="Smoker history")

    # 20-Question Screening Data
    q1_bp_history: bool = Field(..., description="Diagnosed High BP?")
    q2_diabetes_history: bool = Field(..., description="Diagnosed Diabetes?")
    q3_family_heart: bool = Field(..., description="Family History Heart Disease?")
    q4_dry_eyes: bool = Field(..., description="Dry/tired eyes?")
    q5_headaches: bool = Field(..., description="Frequent headaches?")
    q6_neck_pain: bool = Field(..., description="Neck/shoulder stiffness?")
    q7_back_pain: bool = Field(..., description="Lower back pain?")
    q8_sedentary: bool = Field(..., description="Sit >6h/day?")
    # Q9 is vig_activity (mapped above)
    # Q10 is sleep_hours (mapped above)
    q11_insomnia: bool = Field(..., description="Trouble falling asleep?")
    q12_overwhelmed: bool = Field(..., description="Feel overwhelmed?")
    q13_drained: bool = Field(..., description="Emotionally drained?")
    q14_anxious: bool = Field(..., description="Feel anxious/nervous?")
    q15_anhedonia: bool = Field(..., description="Little interest/pleasure?")
    q16_phone_bedtime: bool = Field(..., description="Phone before bed?")
    q17_internet_anxiety: bool = Field(..., description="Anxious without internet?")
    q18_breathlessness: bool = Field(..., description="Short of breath?")
    q19_fatigue: bool = Field(..., description="Frequent fatigue?")
    q20_diet: bool = Field(..., description="Processed food >4x/week?")

    # Digital Habits (Legacy fields mapped to new Qs or preserved for logic)
    daily_digital_hours: float = Field(8.0, description="Est. daily usage") 

    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "gender": 1,
                "bmi": 28.5,
                "systolic_bp": 130,
                "hba1c": 5.7,
                "cholesterol": 200,
                "vigorous_activity": False,
                "sleep_hours": 6.5,
                "smoker_history": True,
                "q1_bp_history": True,
                "q2_diabetes_history": False,
                "q3_family_heart": True,
                "q4_dry_eyes": True,
                "q5_headaches": True,
                "q6_neck_pain": True,
                "q7_back_pain": False,
                "q8_sedentary": True,
                "q11_insomnia": True,
                "q12_overwhelmed": True,
                "q13_drained": False,
                "q14_anxious": True,
                "q15_anhedonia": False,
                "q16_phone_bedtime": True,
                "q17_internet_anxiety": False,
                "q18_breathlessness": False,
                "q19_fatigue": True,
                "q20_diet": True
            }
        }

class DiseaseRisk(BaseModel):
    disease: str = Field(..., example="Type 2 Diabetes")
    risk_level: RiskLevel = Field(..., example="High")
    probability: float = Field(..., ge=0, le=1.0)
    contributing_factors: List[str] = Field(..., example=["High HbA1c", "Elevated BMI"])
    prevention_steps: List[str] = Field(..., example=["Aim for 150 mins activity/week"])

class AssessmentResponse(BaseModel):
    assessment_id: str
    timestamp: datetime
    risks: List[DiseaseRisk]
    disclaimer: str = "ESTIMATE ONLY. NOT A DIAGNOSIS. Consult a physician."

# Chat Models
class ChatMessage(BaseModel):
    message: str
    assessment_id: Optional[str] = None
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    timestamp: str

# Chat Models
class ChatMessage(BaseModel):
    message: str
    assessment_id: Optional[str] = None
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    timestamp: str
