"""
Flask Application - Medical Chatbot Backend API with Authentication
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from conversation_manager import conversation_manager, ConversationState
from medical_response_generator import MedicalResponseGenerator
from llm_providers import LLMProviderFactory
from auth_memory_store import auth_store
import config

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Authentication middleware
def require_auth(f):
    def wrapper(*args, **kwargs):
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        email = user_manager.validate_session(session_token)
        if not email:
            return jsonify({'success': False, 'error': 'Invalid session'}), 401

        # Add user email to request context
        request.user_email = email
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Authentication middleware
def require_auth(f):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not session_token:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        user = auth_store.validate_session(session_token)
        if not user:
            return jsonify({'success': False, 'error': 'Invalid session'}), 401

        # Add user to request context
        request.user = user
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Initialize medical response generator
try:
    medical_generator = MedicalResponseGenerator()
except Exception as e:
    print(f"Warning: Could not initialize medical generator: {e}")
    medical_generator = None

# Authentication Routes

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        result = auth_store.register_user(
            full_name=data.get('full_name'),
            date_of_birth=data.get('date_of_birth'),
            email=data.get('email'),
            password=data.get('password')
        )

        if result['success']:
            return jsonify({
                'success': True,
                'user': result['user'],
                'session_token': result['session_token'],
                'message': 'Registration successful'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user login"""
    try:
        data = request.json
        result = auth_store.authenticate_user(
            email=data.get('email'),
            password=data.get('password')
        )

        if result['success']:
            return jsonify({
                'success': True,
                'user': result['user'],
                'session_token': result['session_token'],
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        success = auth_store.logout_user(session_token)

        return jsonify({
            'success': success,
            'message': 'Logged out successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information"""
    return jsonify({
        'success': True,
        'user': request.user
    }), 200

# User Conversations Routes

@app.route('/api/user/conversations', methods=['GET'])
@require_auth
def get_user_conversations():
    """Get all conversations for the authenticated user"""
    try:
        conversations = auth_store.get_user_conversations(request.user['email'])
        return jsonify({
            'success': True,
            'conversations': conversations
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get conversations'
        }), 500

@app.route('/api/user/conversations', methods=['POST'])
@require_auth
def save_user_conversation():
    """Save a conversation for the authenticated user"""
    try:
        user_email = request.user['email']
        data = request.json
        conversation_data = data.get('conversation')

        if not conversation_data or not conversation_data.get('id'):
            return jsonify({
                'success': False,
                'error': 'Conversation data with ID is required'
            }), 400

        success = auth_store.save_conversation(user_email, conversation_data)
        if success:
            return jsonify({
                'success': True,
                'message': 'Conversation saved successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save conversation'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to save conversation'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Medical Chatbot Backend'
    })


@app.route('/api/conversation/start', methods=['POST'])
@require_auth
def start_conversation():
    """Start a new conversation session for authenticated user"""
    try:
        user_email = request.user['email']
        conversation_id = conversation_manager.create_conversation(user_email)

        # Save conversation to user's in-memory store
        conversation_data = {
            'id': conversation_id,
            'title': 'New Conversation',
            'messages': [],
            'age': None,
            'language': 'english',
            'created_at': conversation_manager.get_conversation(conversation_id)['created_at'],
            'updated_at': conversation_manager.get_conversation(conversation_id)['updated_at']
        }
        auth_store.save_conversation(user_email, conversation_data)

        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'message': 'Conversation started. Please select your age group.',
            'state': 'awaiting_age',
            'age_groups': config.Config.AGE_GROUPS
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/conversation/<conversation_id>/age', methods=['POST'])
@require_auth
def set_age(conversation_id):
    """Set age for a conversation"""
    try:
        user_email = request.user['email']
        data = request.json
        age = data.get('age')

        if not age:
            return jsonify({
                'success': False,
                'error': 'Age is required'
            }), 400

        success = conversation_manager.set_age(conversation_id, age)

        if not success:
            return jsonify({
                'success': False,
                'error': 'Invalid age group or conversation not found'
            }), 400

        # Update conversation in in-memory store
        conv = conversation_manager.get_conversation(conversation_id)
        auth_store.update_conversation_messages(conversation_id, conv['messages'], user_email)

        # Update conversation metadata
        conversation_data = auth_store.get_conversation(conversation_id, user_email)
        if conversation_data:
            conversation_data['age'] = age
            auth_store.save_conversation(user_email, conversation_data)

        response = {
            'success': True,
            'message': 'Age set successfully',
            'age': age,
            'state': conv['state'].value
        }

        # If language is also set, conversation is ready
        if conv['state'] == ConversationState.READY:
            response['message'] = 'Conversation ready. You can now describe your symptoms.'
            response['languages'] = list(config.Config.SUPPORTED_LANGUAGES.keys())
        else:
            response['message'] = 'Age set. Please select your preferred language.'
            response['languages'] = list(config.Config.SUPPORTED_LANGUAGES.keys())

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/conversation/<conversation_id>/language', methods=['POST'])
@require_auth
def set_language(conversation_id):
    """Set language for a conversation"""
    try:
        data = request.json
        language = data.get('language', 'english').lower()
        
        success = conversation_manager.set_language(conversation_id, language)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Invalid language or conversation not found'
            }), 400
        
        conv = conversation_manager.get_conversation(conversation_id)

        response = {
            'success': True,
            'message': 'Language set successfully',
            'language': language,
            'state': conv['state'].value
        }

        # Attempt to translate existing conversation messages to the selected language
        try:
            if medical_generator and conv and conv.get('messages'):
                # Use the generator's translator to get translated contents
                translated_contents = medical_generator.translate_messages(conv['messages'], language)
                # Update stored messages in conversation manager
                conversation_manager.translate_conversation(conversation_id, language, lambda msgs, lang: medical_generator.translate_messages(msgs, lang))
                # Build translated message objects to return
                translated_messages = []
                for i, m in enumerate(conv['messages']):
                    content = translated_contents[i]
                    # For assistant messages, try to parse into structured response if possible
                    if m.get('role') == 'assistant':
                        try:
                            parsed = medical_generator._parse_response(content)
                            # include disclaimer separately
                            parsed['disclaimer'] = medical_generator._get_disclaimer(language)
                            content_obj = parsed
                        except Exception:
                            content_obj = content
                        translated_messages.append({
                            'role': m.get('role'),
                            'content': content_obj,
                            'timestamp': m.get('timestamp')
                        })
                    else:
                        translated_messages.append({
                            'role': m.get('role'),
                            'content': content,
                            'timestamp': m.get('timestamp')
                        })
                response['translated_messages'] = translated_messages

        except Exception as e:
            # If translation fails, warn but do not change conversation state
            response['translation_warning'] = 'Translation failed; original messages preserved.'
        
        # If age is also set, conversation is ready
        if conv['state'] == ConversationState.READY:
            response['message'] = 'Conversation ready. You can now describe your symptoms.'
        else:
            response['message'] = 'Language set. Please select your age group.'
            response['age_groups'] = config.Config.AGE_GROUPS
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/conversation/<conversation_id>/chat', methods=['POST'])
@require_auth
def chat(conversation_id):
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        conv = conversation_manager.get_conversation(conversation_id)
        
        if not conv:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        # Check if age and language are set
        can_process, error_msg = conversation_manager.can_process_symptoms(conversation_id)
        
        if not can_process:
            # Handle initial setup messages
            if conv['state'] == ConversationState.INITIAL or conv['state'] == ConversationState.AWAITING_AGE:
                return jsonify({
                    'success': False,
                    'error': 'Please select your age group first',
                    'requires_age': True,
                    'age_groups': config.Config.AGE_GROUPS
                }), 400
            
            if conv['state'] == ConversationState.AWAITING_LANGUAGE:
                return jsonify({
                    'success': False,
                    'error': 'Please select your preferred language',
                    'requires_language': True,
                    'languages': list(config.Config.SUPPORTED_LANGUAGES.keys())
                }), 400
        
        # Add user message to history
        conversation_manager.add_message(conversation_id, 'user', message)
        
        # Generate medical response
        if not medical_generator:
            return jsonify({
                'success': False,
                'error': 'Medical response generator is not available. Please check LLM configuration.'
            }), 500
        
        history = conversation_manager.get_conversation_history(conversation_id)
        result = medical_generator.generate_medical_response(
            symptoms=message,
            age=conv['age'],
            language=conv['language'],
            conversation_history=history
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate response')
            }), 500
        
        # Add assistant response to history
        assistant_message = f"Summary: {result['response']['summary']}\n\nHome Care: {result['response']['home_care']}\n\nMedical Attention: {result['response']['medical_attention']}\n\nPossible Causes: {result['response']['possible_causes']}"
        conversation_manager.add_message(conversation_id, 'assistant', assistant_message)
        
        return jsonify({
            'success': True,
            'response': result['response'],
            'conversation_id': conversation_id
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/conversation/<conversation_id>/status', methods=['GET'])
@require_auth
def get_status(conversation_id):
    """Get conversation status"""
    try:
        conv = conversation_manager.get_conversation(conversation_id)
        
        if not conv:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'state': conv['state'].value,
            'age': conv['age'],
            'language': conv['language'],
            'message_count': len(conv['messages'])
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config/age-groups', methods=['GET'])
def get_age_groups():
    """Get available age groups"""
    return jsonify({
        'success': True,
        'age_groups': config.Config.AGE_GROUPS
    }), 200


@app.route('/api/config/languages', methods=['GET'])
def get_languages():
    """Get supported languages"""
    return jsonify({
        'success': True,
        'languages': config.Config.SUPPORTED_LANGUAGES,
        'default_language': config.Config.DEFAULT_LANGUAGE
    }), 200


@app.route('/api/config/llm-providers', methods=['GET'])
def get_llm_providers():
    """Get available LLM providers"""
    try:
        available = LLMProviderFactory.list_available_providers()
        current = config.Config.LLM_PROVIDER
        
        return jsonify({
            'success': True,
            'current_provider': current,
            'available_providers': available,
            'all_providers': list(LLMProviderFactory._providers.keys())
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config/switch-provider', methods=['POST'])
def switch_provider():
    """Switch LLM provider (admin function)"""
    try:
        data = request.json
        provider = data.get('provider')
        
        if not provider:
            return jsonify({
                'success': False,
                'error': 'Provider name is required'
            }), 400
        
        new_provider = LLMProviderFactory.switch_provider(provider)
        
        # Update global medical generator
        global medical_generator
        medical_generator = MedicalResponseGenerator()
        
        return jsonify({
            'success': True,
            'provider': provider,
            'message': f'Switched to {provider} provider'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Validate configuration
    try:
        config.Config.validate_config()
        print(f"Starting Medical Chatbot Backend with {config.Config.LLM_PROVIDER} provider...")
        app.run(
            host='0.0.0.0',
            port=config.Config.FLASK_PORT,
            debug=config.Config.FLASK_DEBUG
        )
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please check your .env file and ensure API keys are set correctly.")
    except Exception as e:
        print(f"Error starting server: {e}")

