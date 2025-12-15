/**
 * Conversation Mode Detection Utility
 * Determines whether user input is medical or general conversation
 */

/**
 * Medical keywords that indicate medical consultation mode
 */
const MEDICAL_KEYWORDS = [
  // Symptoms
  'pain', 'ache', 'headache', 'fever', 'cough', 'cold', 'flu', 'nausea',
  'vomiting', 'diarrhea', 'constipation', 'rash', 'itching', 'swelling',
  'dizziness', 'fatigue', 'tired', 'weakness', 'sore', 'throat',
  'stomach', 'chest', 'back', 'neck', 'shoulder', 'knee', 'joint',
  'muscle', 'bone', 'skin', 'eye', 'ear', 'nose', 'mouth', 'tooth',
  'blood', 'pressure', 'heart', 'breathing', 'breath', 'lung', 'kidney',
  'liver', 'infection', 'inflammation', 'allergy', 'asthma', 'diabetes',
  'cancer', 'tumor', 'injury', 'burn', 'cut', 'wound', 'fracture',

  // Diseases/Conditions
  'disease', 'illness', 'condition', 'syndrome', 'disorder', 'problem',
  'issue', 'concern', 'sick', 'unwell', 'ailment',

  // Medical Actions
  'medicine', 'medication', 'drug', 'prescription', 'dosage', 'pill',
  'tablet', 'treatment', 'therapy', 'surgery', 'operation', 'procedure',
  'exam', 'test', 'checkup', 'diagnosis', 'doctor', 'hospital', 'clinic',
  'emergency', 'urgent', 'critical', 'serious', 'severe', 'mild',

  // Health Questions
  'should', 'can', 'do', 'is it', 'what if', 'help', 'advice', 'recommend',
  'suggest', 'cause', 'reason', 'why', 'how', 'when', 'where', 'which',

  // Medical Terms
  'symptom', 'diagnosis', 'prognosis', 'treatment', 'prevention',
  'cure', 'remedy', 'relief', 'recovery', 'healing'
];

/**
 * General conversation patterns that indicate friendly chat mode
 */
const FRIENDLY_PATTERNS = [
  // Greetings
  /^hi\b/i, /^hello\b/i, /^hey\b/i, /^good\s+(morning|afternoon|evening|day|night)/i,
  /^howdy\b/i, /^greetings\b/i, /^salutations\b/i,

  // Polite inquiries
  /^how\s+are\s+you/i, /^what'?s\s+up/i, /^how\s+have\s+you\s+been/i,
  /^how\s+do\s+you\s+do/i, /^nice\s+to\s+meet\s+you/i,

  // Friendly conversation starters
  /^tell\s+me\s+about/i, /^what\s+do\s+you\s+do/i, /^who\s+are\s+you/i,
  /^can\s+you\s+(help|tell|explain)/i, /^i\s+(need|want)\s+to/i,

  // Casual acknowledgments
  /^thanks?\b/i, /^thank\s+you/i, /^please/i, /^sorry/i, /^excuse\s+me/i,

  // Simple questions that aren't medical
  /^what\s+is/i, /^how\s+does/i, /^can\s+you/i, /^do\s+you/i,
  /^why\s+do/i, /^when\s+will/i, /^where\s+can/i, /^which\s+is/i
];

/**
 * Check if message contains medical-related content
 * @param {string} message - User message to analyze
 * @returns {boolean} True if message appears to be medical-related
 */
const containsMedicalContent = (message) => {
  const lowerMessage = message.toLowerCase();

  // Check for medical keywords
  const hasMedicalKeywords = MEDICAL_KEYWORDS.some(keyword =>
    lowerMessage.includes(keyword.toLowerCase())
  );

  // Check for medical question patterns
  const medicalQuestionPatterns = [
    /\b(what|how|why|when|where|which|should|can|do)\s+(is|are|do|does|should|can|will|would|could|may)\s+(this|that|it|symptom|pain|condition|treatment|medicine)/i,
    /\b(help|advice|suggestion|recommendation)\s+(for|with|about)\s+(pain|symptom|condition|treatment|medicine|health)/i,
    /\b(i\s+have|i'm|i\s+am|feeling|experiencing)\s+(pain|ache|fever|cough|nausea|rash|fatigue|tired)/i,
    /\b(medicine|medication|drug|pill|tablet|dosage|prescription)\s+(for|about|question)/i,
    /\b(take|use|need|want|give|recommend)\s+(medicine|medication|drug|pill|tablet|treatment)/i,
    /\b(symptom|pain|ache|fever|cough|cold|flu|infection|disease|sick|ill)\s+(of|for|with)/i
  ];

  const hasMedicalQuestion = medicalQuestionPatterns.some(pattern =>
    pattern.test(message)
  );

  // Additional check: if message contains medical terms with action words
  const actionWords = ['take', 'use', 'need', 'want', 'give', 'recommend', 'help', 'treat', 'cure'];
  const hasActionWithMedical = actionWords.some(action =>
    lowerMessage.includes(action) && MEDICAL_KEYWORDS.some(keyword =>
      lowerMessage.includes(keyword.toLowerCase())
    )
  );

  return hasMedicalKeywords || hasMedicalQuestion || hasActionWithMedical;
};

/**
 * Check if message is friendly/general conversation
 * @param {string} message - User message to analyze
 * @returns {boolean} True if message appears to be friendly conversation
 */
const isFriendlyConversation = (message) => {
  // Check for friendly patterns
  const hasFriendlyPattern = FRIENDLY_PATTERNS.some(pattern =>
    pattern.test(message.trim())
  );

  // Check for very short messages that are likely greetings
  const isShortGreeting = message.trim().length <= 20 &&
    (/^(hi|hello|hey|sup|yo|good\s+(morning|afternoon|evening|day|night))$/i).test(message.trim());

  return hasFriendlyPattern || isShortGreeting;
};

/**
 * Determine the conversation mode based on user message
 * @param {string} message - User message to analyze
 * @returns {string} 'medical' or 'general'
 */
export const detectConversationMode = (message) => {
  if (!message || typeof message !== 'string') {
    return 'general';
  }

  // First check if it's medical content
  if (containsMedicalContent(message)) {
    return 'medical';
  }

  // Then check if it's friendly conversation
  if (isFriendlyConversation(message)) {
    return 'general';
  }

  // Check for very short messages or unclear intent
  // If message is very short and doesn't clearly indicate medical intent,
  // default to general conversation
  const trimmedMessage = message.trim();
  if (trimmedMessage.length <= 10 && !containsMedicalContent(message)) {
    return 'general';
  }

  // For ambiguous cases, be more aggressive about detecting medical intent
  // Look for common medical prefixes/suffixes
  const medicalPrefixes = ['i have', 'i\'m', 'i am', 'feeling', 'experiencing', 'suffering from'];
  const hasMedicalPrefix = medicalPrefixes.some(prefix =>
    trimmedMessage.toLowerCase().startsWith(prefix)
  );

  if (hasMedicalPrefix) {
    return 'medical';
  }

  // Default to general for safety, but log for debugging
  console.log('Ambiguous message, defaulting to general:', trimmedMessage);
  return 'general';
};

/**
 * Get response type based on conversation mode
 * @param {string} mode - Conversation mode ('medical' or 'general')
 * @returns {string} Response type for UI rendering
 */
export const getResponseType = (mode) => {
  return mode === 'medical' ? 'structured' : 'conversational';
};

