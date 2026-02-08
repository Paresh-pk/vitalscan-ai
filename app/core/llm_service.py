import os
import json
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
from app.models.schemas import DiseaseRisk, RiskLevel

# Load environment variables
load_dotenv()

class LLMService:
    """
    Layer 2: Explanation & Prevention Engine.
    Uses Hugging Face (GLM-4) via OpenAI Client for dynamic advice.
    """
    
    def __init__(self):
        # Load API Key from Environment
        self.api_key = os.getenv("HF_TOKEN")
        self.base_url = "https://router.huggingface.co/v1"
        self.model_name = "Qwen/Qwen2.5-Coder-32B-Instruct"
        #self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"
        
        if self.api_key:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        else:
            print("WARNING: No HF_TOKEN found. Using template fallback.")

    def generate_explanation(self, risks: List[DiseaseRisk], user_profile: dict = None) -> List[DiseaseRisk]:
        """
        Enriches risk objects with LLM-generated advice.
        """
        # Create/Append to debug log
        def log_debug(msg):
            with open("server_debug.log", "a", encoding="utf-8") as f:
                f.write(f"\n[{pd.Timestamp.now()}] {msg}\n")

        if not self.api_key:
            log_debug("ERROR: API Key missing.")
            return self._template_fallback(risks)

        try:
            # 1. Build Prompt
            prompt = self._build_prompt(risks, user_profile)
            log_debug(f"PROMPT SENT:\n{prompt[:200]}...[truncated]...")
            
            # 2. Call Hugging Face API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a medical prevention advisor. Provide personalized, actionable health advice in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            
            raw_text = response.choices[0].message.content
            log_debug(f"RAW LLM RESPONSE:\n{raw_text[:300]}...[truncated]...")
            
            # 3. Parse JSON
            enriched_data = self._parse_llm_response(raw_text)
            log_debug(f"PARSED JSON KEYS: {list(enriched_data.keys())}")
            
            # 4. Merge with Original Risks
            for risk in risks:
                disease_name = risk.disease
                if disease_name in enriched_data:
                    risk.prevention_steps = enriched_data[disease_name].get("prevention_steps", risk.prevention_steps)
                    log_debug(f"✅ Enriched '{disease_name}' with {len(risk.prevention_steps)} steps.")
                else:
                    log_debug(f"⚠️ No LLM data for '{disease_name}', using template.")
            
            return risks
            
        except Exception as e:
            log_debug(f"❌ LLM CALL FAILED: {str(e)}")
            return self._template_fallback(risks)

    def _build_prompt(self, risks: List[DiseaseRisk], user_profile: dict) -> str:
        """
        Constructs a detailed prompt for the LLM.
        """
        risk_summary = "\n".join([
            f"- {r.disease}: {r.probability*100:.1f}% ({r.risk_level.value}) | Drivers: {', '.join(r.contributing_factors[:3])}"
            for r in risks
        ])
        
        profile_str = json.dumps(user_profile, indent=2) if user_profile else "Not provided"
        
        return f"""
        ### TASK: Generate Personalized Health Prevention Plans

        ### 1. USER PROFILE
        ```json
        {profile_str}
        ```

        ### 2. RISK ASSESSMENT RESULTS
        {risk_summary}

        ### 3. YOUR ROLE
        You are a **preventive health advisor**. For EACH disease above, generate **5 highly personalized, actionable prevention steps**.

        ### 4. PERSONALIZATION RULES
        1. **Reference Specific Data**: Use exact values from the user profile (e.g., "Your HbA1c is 5.8", "You sit 8h/day").
        2. **Micro-Habits**: Suggest small, realistic changes (e.g., "Walk 10 mins after dinner" not "Exercise 1h daily").
        3. **Prioritize High-Impact**: Focus on the top contributing factors.
        4. **Safety**: Do not diagnosis. Add simple caveats (e.g. "if knees allow").

        ### 5. OUTPUT FORMAT
        Return STRICT JSON only. The "prevention_steps" array must contain strings formatted like:
        "**[Action Name]**: [Detailed Instruction]. *Why*: [Rationale]. *Result*: [Outcome]."

        Example JSON Structure:
        {{
            "Type 2 Diabetes": {{
                "prevention_steps": [
                    "**Start Post-Meal Walks**: Walk for 10 mins after dinner. *Why*: Your HbA1c is 5.8 and you sit 8h/day. *Result*: Blunted glucose spike.",
                    "**Swap Latex Focus**: ...",
                    ... (5 items)
                ]
            }},
            ...
        }}
        """

    def _parse_llm_response(self, raw_text: str) -> dict:
        """
        Extracts JSON from LLM response (handles markdown code blocks).
        """
        try:
            # Strip markdown code fences
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0]
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0]
            
            return json.loads(raw_text.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {str(e)}")

    def _template_fallback(self, risks: List[DiseaseRisk]) -> List[DiseaseRisk]:
        """
        Fallback to generic templates if LLM fails.
        """
        templates = {
            "Type 2 Diabetes": [
                "**Monitor Blood Sugar**: Check fasting glucose monthly.",
                "**Increase Fiber**: Add beans, oats, vegetables to meals.",
                "**Walk After Meals**: 10-minute walks reduce glucose spikes.",
                "**Limit Sugary Drinks**: Replace soda with water or tea.",
                "**Annual Screening**: Get HbA1c tested yearly."
            ],
            "Hypertension": [
                "**Reduce Sodium**: Aim for <2,300mg/day (1 tsp salt).",
                "**DASH Diet**: Focus on fruits, vegetables, whole grains.",
                "**Regular Exercise**: 150 mins/week moderate activity.",
                "**Stress Management**: Try meditation or deep breathing.",
                "**Monitor BP**: Check blood pressure weekly at home."
            ],
            "Digital Eye Strain": [
                "**20-20-20 Rule**: Every 20 mins, look 20 feet away for 20 secs.",
                "**Blue Light Filters**: Use screen filters after sunset.",
                "**Proper Lighting**: Reduce glare, use task lighting.",
                "**Blink More**: Consciously blink to prevent dry eyes.",
                "**Eye Exams**: Annual checkup with optometrist."
            ]
        }
        
        for risk in risks:
            if risk.disease in templates:
                risk.prevention_steps = templates[risk.disease]
            else:
                risk.prevention_steps = [
                    "Consult a healthcare provider for personalized advice.",
                    "Maintain a healthy lifestyle with balanced diet and exercise.",
                    "Monitor symptoms and track changes over time.",
                    "Stay informed about your condition through reliable sources.",
                    "Schedule regular health checkups."
                ]
        
        return risks

    def chat(self, user_message: str, conversation_history: List[dict] = None, assessment_id: str = None) -> str:
        """
        Interactive chat with health assistant.
        Provides context-aware, personalized health advice.
        """
        if not self.api_key:
            return "I'm currently in offline mode. Please check back later for AI-powered assistance."
        
        try:
            # System prompt for health assistant
            system_prompt = """You are a knowledgeable and empathetic health assistant for VITALSCAN, an AI-powered preventive health platform.

Your role:
- Provide evidence-based, actionable health advice
- Explain health risks and prevention strategies in simple terms
- Be supportive and encouraging
- Use bullet points and clear formatting

Critical rules:
- NEVER diagnose medical conditions
- NEVER prescribe medications
- ALWAYS recommend consulting healthcare professionals for serious concerns
- Keep responses concise (2-3 paragraphs max)
- If asked about emergency symptoms, urge immediate medical attention

Tone: Professional yet friendly, like a knowledgeable health coach."""

            # Build conversation messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if available (limit to last 5 messages)
            if conversation_history:
                for msg in conversation_history[-5:]:
                    # Ensure proper role mapping
                    role = msg.get("role", "user")
                    if role == "assistant":
                        role = "assistant"  # Keep as is
                    elif role == "user":
                        role = "user"  # Keep as is
                    else:
                        continue  # Skip invalid roles
                    
                    messages.append({
                        "role": role,
                        "content": msg.get("content", "")
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call LLM with reduced token limit for stability
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=300  # Reduced from 500 for better reliability
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Log the full error for debugging
            error_msg = str(e)
            print(f"CHAT ERROR: {error_msg}")
            
            # Return user-friendly message
            if "400" in error_msg:
                return "I encountered an issue processing your request. Please try rephrasing your question or start a new conversation."
            else:
                return f"I'm having trouble connecting right now. Please try again in a moment."
