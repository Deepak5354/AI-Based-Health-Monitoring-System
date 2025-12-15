# Medical Chatbot Frontend

A modern React-based frontend for the Medical Chatbot Backend, featuring a ChatGPT-like interface.

## Features

- 🎨 **ChatGPT-like UI** - Clean, modern interface with dark theme
- 💬 **Real-time Chat** - Interactive conversation interface
- 👤 **Age Selection** - Mandatory age group selection with modal
- 🌐 **Multi-language Support** - Support for 13 Indian languages with top-right dropdown
- 📋 **Structured Responses** - Medical responses displayed in organized sections (A-D)
- ⚠️ **Prominent Disclaimers** - Clear medical disclaimers
- 📚 **Conversation History** - Left sidebar with intelligent conversation naming
- ⚙️ **Settings Panel** - Right-side panel to change age and language anytime
- 📱 **Responsive Design** - Works on desktop and mobile devices

## Prerequisites

- Node.js 16+ and npm/yarn
- Backend server running on `http://localhost:5000`

## Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   The app will open at `http://localhost:3000`

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── AgeSelector.js          # Age selection modal
│   │   ├── AgeSelector.css
│   │   ├── LanguageSelector.js     # Language selection modal
│   │   ├── LanguageSelector.css
│   │   ├── MedicalResponse.js      # Structured medical response display
│   │   ├── MedicalResponse.css
│   │   ├── MessageBubble.js        # Chat message component
│   │   ├── MessageBubble.css
│   │   ├── ChatInput.js            # Message input component
│   │   └── ChatInput.css
│   ├── services/
│   │   └── api.js                  # API service layer
│   ├── App.js                      # Main app component
│   ├── App.css
│   ├── index.js                    # Entry point
│   └── index.css
├── package.json
└── README.md
```

## Usage Flow

1. **Start Conversation**
   - App automatically initializes a conversation on load
   - Age selector modal appears if age is not set

2. **Set Age (Required)**
   - User must select an age group from the dropdown
   - After setting age, language selector may appear

3. **Set Language (Optional)**
   - User can select preferred language from top-right dropdown
   - Defaults to English if skipped
   - Can be changed anytime during conversation

4. **Chat**
   - User can describe symptoms
   - Responses are displayed in structured format:
     - (A) Brief Summary of Symptoms
     - (B) Home Care Recommendations
     - (C) When to Seek Medical Attention
     - (D) Possible Causes
   - Disclaimer is prominently displayed

5. **Manage Conversations**
   - View conversation history in left sidebar
   - Click conversations to switch between them
   - Each conversation has an intelligent, unique title
   - Start new conversations with "New Chat" button

6. **Change Settings**
   - Click "Settings" in left sidebar to open right panel
   - Change age group or language at any time
   - Settings persist for the current conversation

## API Integration

The frontend integrates with the backend API using the `api.js` service layer. All API calls are handled through this service.

**Base URL:** `http://localhost:5000`

## Customization

### Change API Base URL

Edit `src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000'; // Change this
```

### Styling

All styles are in CSS files. The main theme colors are:
- Background: `#343541`
- Sidebar: `#202123`
- Messages: `#40414f`
- Primary: `#10a37f` (green)
- Text: `#ececf1`

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Troubleshooting

### CORS Errors
- Ensure backend CORS is enabled (already configured)
- Check that backend is running on `http://localhost:5000`

### API Connection Failed
- Verify backend server is running
- Check `API_BASE_URL` in `src/services/api.js`
- Check browser console for errors

### Age/Language Not Setting
- Check browser console for API errors
- Verify conversation ID is being stored
- Ensure backend endpoints are responding correctly

## License

This project is for educational and informational purposes only.

