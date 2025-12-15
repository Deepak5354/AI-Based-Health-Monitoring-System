"""
Medical Response Generator - Creates structured medical responses
"""
from typing import Dict, Optional
from llm_providers import LLMProviderFactory
import config

class MedicalResponseGenerator:
    """Generates structured medical responses using LLM"""
    
    def __init__(self):
        self.llm_provider = LLMProviderFactory.get_provider()
    
    def get_system_prompt(self, language: str = 'english') -> str:
        """Get system prompt for medical chatbot"""
        base_prompt = """You are a medical assistant chatbot that provides informational medical guidance. 
Your role is to help users understand their symptoms and provide general health information.

IMPORTANT GUIDELINES:
1. You are NOT a replacement for professional medical advice. Always emphasize consulting healthcare professionals.
2. Provide information that is educational and informative, not diagnostic.
3. Be clear about limitations and when professional medical attention is required.
4. Consider age-appropriate recommendations for medications and treatments.
5. Provide responses in a structured format as requested.

RESPONSE FORMAT:
For every symptom-based query, you MUST provide responses in the following structured format:

(A) Brief Summary of the Symptoms
- Provide a concise explanation of the symptoms provided by the user.

(B) Home Care Recommendations
- Suggest safe, general remedies or actions the user can perform at home.
- Include age-appropriate recommendations.

(C) When to Seek Medical Attention
- Clearly state warning signs or conditions that require consultation with a healthcare professional.
- Be specific about emergency situations.

(D) Possible Causes
- List common or likely causes related to the reported symptoms.
- Explain that these are possibilities, not definitive diagnoses.

Always include a disclaimer that this information is for informational purposes only and does not replace professional medical advice."""

        # Add language-specific instructions if needed
        if language != 'english':
            base_prompt += f"\n\nIMPORTANT: Provide all responses in {config.Config.SUPPORTED_LANGUAGES.get(language, language)} language."
        
        return base_prompt
    
    def generate_medical_response(
        self, 
        symptoms: str, 
        age: str, 
        language: str = 'english',
        conversation_history: list = None
    ) -> Dict[str, any]:
        """Generate structured medical response"""
        
        # Build the user prompt
        user_prompt = f"""User Age Group: {age}
User Reported Symptoms: {symptoms}

Please provide medical guidance in the following structured format:

(A) Brief Summary of the Symptoms
(B) Home Care Recommendations (age-appropriate)
(C) When to Seek Medical Attention
(D) Possible Causes

Remember to:
- Consider the age group when recommending medications or treatments
- Provide age-appropriate dosage information if suggesting any medications
- Emphasize when professional medical consultation is necessary
- Include appropriate disclaimers"""

        # Add conversation context if available
        if conversation_history:
            context = "\n\nPrevious conversation context:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                context += f"{msg['role']}: {msg['content']}\n"
            user_prompt = context + user_prompt
        
        try:
            system_prompt = self.get_system_prompt(language)
            response = self.llm_provider.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            # Parse response into structured format
            structured_response = self._parse_response(response)
            
            # Add disclaimer
            structured_response['disclaimer'] = self._get_disclaimer(language)
            
            return {
                'success': True,
                'response': structured_response,
                'raw_response': response
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response into structured format"""
        structured = {
            'summary': '',
            'home_care': '',
            'medical_attention': '',
            'possible_causes': ''
        }
        
        # Try to extract sections using markers
        sections = {
            'summary': ['(A)', 'Brief Summary', 'Summary of the Symptoms'],
            'home_care': ['(B)', 'Home Care', 'Home Care Recommendations'],
            'medical_attention': ['(C)', 'When to Seek Medical Attention', 'Seek Medical Attention'],
            'possible_causes': ['(D)', 'Possible Causes', 'Causes']
        }
        
        lines = response.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line_upper = line.upper()
            
            # Check if this line starts a new section
            found_section = False
            for section_name, markers in sections.items():
                for marker in markers:
                    if marker.upper() in line_upper:
                        # Save previous section
                        if current_section:
                            structured[current_section] = '\n'.join(current_content).strip()
                        
                        # Start new section
                        current_section = section_name
                        current_content = [line]
                        found_section = True
                        break
                
                if found_section:
                    break
            
            if not found_section and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            structured[current_section] = '\n'.join(current_content).strip()
        
        # If parsing failed, return raw response in summary
        if not any(structured.values()):
            structured['summary'] = response
        
        return structured
    
    def _get_disclaimer(self, language: str = 'english') -> str:
        """Get appropriate disclaimer in the selected language"""
        disclaimers = {
            'english': "⚠️ IMPORTANT DISCLAIMER: This information is for informational purposes only and does not constitute medical advice, diagnosis, or treatment. Always consult with a qualified healthcare professional for proper medical evaluation and treatment. Do not delay seeking professional medical advice because of information received from this chatbot.",
            'hindi': "⚠️ महत्वपूर्ण अस्वीकरण: यह जानकारी केवल सूचनात्मक उद्देश्यों के लिए है और चिकित्सा सलाह, निदान या उपचार का गठन नहीं करती है। उचित चिकित्सा मूल्यांकन और उपचार के लिए हमेशा एक योग्य स्वास्थ्य देखभाल पेशेवर से परामर्श करें।",
            'bengali': "⚠️ গুরুত্বপূর্ণ অস্বীকার: এই তথ্য শুধুমাত্র তথ্যগত উদ্দেশ্যে এবং চিকিৎসা পরামর্শ, রোগ নির্ণয় বা চিকিৎসা গঠন করে না। সঠিক চিকিৎসা মূল্যায়ন এবং চিকিৎসার জন্য সর্বদা একজন যোগ্য স্বাস্থ্যসেবা পেশাদারের সাথে পরামর্শ করুন।",
            'telugu': "⚠️ ముఖ్యమైన నిరాకరణ: ఈ సమాచారం సమాచార ప్రయోజనాల కోసం మాత్రమే మరియు వైద్య సలహా, రోగ నిర్ధారణ లేదా చికిత్సను ఏర్పరుస్తుంది. సరైన వైద్య మూల్యాంకనం మరియు చికిత్స కోసం ఎల్లప్పుడూ అర్హత కలిగిన ఆరోగ్య సంరక్షణ నిపుణుడిని సంప్రదించండి।",
            'tamil': "⚠️ முக்கியமான மறுப்பு: இந்த தகவல் தகவல் நோக்கங்களுக்காக மட்டுமே மற்றும் மருத்துவ ஆலோசனை, நோயறிதல் அல்லது சிகிச்சையை உருவாக்காது। சரியான மருத்துவ மதிப்பீடு மற்றும் சிகிச்சைக்காக எப்போதும் தகுதிவாய்ந்த சுகாதார பராமரிப்பு நிபுணரைக் கலந்தாலோசிக்கவும்।",
            'marathi': "⚠️ महत्त्वाचे नकार: ही माहिती केवळ माहितीच्या हेतूसाठी आहे आणि वैद्यकीय सल्ला, निदान किंवा उपचार तयार करत नाही। योग्य वैद्यकीय मूल्यांकन आणि उपचारासाठी नेहमी पात्र आरोग्य सेवा व्यावसायिकांशी सल्लामसलत करा।"
        }
        
        return disclaimers.get(language.lower(), disclaimers['english'])

    def translate_messages(self, messages: list, target_language: str) -> list:
        """Translate a list of message dicts to the target language using the LLM provider.

        messages: list of dicts with keys: role, content
        Returns: list of translated content strings in same order
        """
        if not messages:
            return []

        try:
            # Build a JSON translation request to ensure structured output
            conversation_text = ''
            for i, m in enumerate(messages):
                role = m.get('role', 'user')
                content = m.get('content', '')
                conversation_text += f"INDEX:{i} ROLE:{role}\n{content}\n---\n"

            system_prompt = (
                "You are a professional translator specialized in medical conversations. \n"
                "Translate the following conversation into the requested language while preserving exact medical meaning, dosages, warnings, structure, and any disclaimers. \n"
                "Do NOT add, remove, or change medical guidance; only translate.\n"
                "Return a strict JSON array where each element is an object: {\"index\": <index>, \"role\": \"user|assistant\", \"content\": \"translated text\"}.\n"
                "If a message contains structured lists or sections, preserve their formatting in the translated text.\n"
            )

            user_prompt = f"Target Language: {target_language}\n\nConversation:\n{conversation_text}\n\nReturn only a JSON array as described above."

            response = self.llm_provider.generate_response(prompt=user_prompt, system_prompt=system_prompt)

            # Try to parse JSON from the model output
            import json
            try:
                parsed = json.loads(response)
            except Exception:
                # Attempt to extract JSON substring
                import re
                m = re.search(r"(\[\s*\{.*\}\s*\])", response, re.S)
                if not m:
                    raise ValueError("Could not parse translation output as JSON")
                parsed = json.loads(m.group(1))

            # Build list of translated texts according to indices
            translated = [None] * len(messages)
            for item in parsed:
                idx = int(item.get('index'))
                text = item.get('content', '')
                translated[idx] = text

            # Fill any None entries with original content (fallback)
            for i, t in enumerate(translated):
                if t is None:
                    translated[i] = messages[i].get('content', '')

            return translated

        except Exception as e:
            # On any failure, return original contents as a safe fallback
            return [m.get('content', '') for m in messages]

