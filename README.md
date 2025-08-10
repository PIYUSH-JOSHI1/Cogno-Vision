# Learning Disability Support Platform

A comprehensive, multi-role Flask web application providing AI-powered support for children with learning disabilities: Dyslexia, Dyscalculia, Dysgraphia, and Dyspraxia. Includes dashboards for doctors, parents, and children, with CSV-based data storage and modern UI.

---

## Features

### 🧠 Dyslexia Support
- AI-powered text simplification
- Text-to-speech with adjustable settings
- Phonics games and sound matching
- Reading progress tracking
- Dyslexia-friendly fonts and formatting

### 🧮 Dyscalculia Support
- Adaptive math problem generation
- Visual math problems with objects
- Number line visualization
- Pattern recognition games
- Step-by-step problem solving

### ✍️ Dysgraphia Support
- Writing analysis and feedback
- Letter formation practice
- Creative writing prompts
- Handwriting improvement tools
- Spelling and grammar assistance

### 🏃 Dyspraxia Support
- Balance training exercises
- Coordination games
- Live camera movement tracking
- Motor skills assessment
- Real-time feedback system

### 👨‍⚕️ Doctor Dashboard
- Login/signup for doctors
- View all patients and their full activity history
- Download patient and all-patient reports as CSV
- Modern, card-based UI with sidebar navigation

### 👨‍👩‍👧 Parent & Child Dashboards
- Separate logins for parents and children
- Progress tracking and activity summaries
- Accessible, child-friendly design

---

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Data Storage**: CSV files (no database required)
- **AI/ML**: NLTK, Transformers, Torch
- **Computer Vision**: OpenCV, MediaPipe
- **Deployment**: Gunicorn, Render-ready

---

## Project Structure

```
├── app.py                # Main Flask app
├── wsgi.py               # WSGI entry point for production
├── config.py             # Configuration (env vars, secrets)
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment config
├── Procfile              # Gunicorn start command
├── blueprints/           # Flask blueprints (doctor, auth, etc.)
├── modules/              # Feature modules (dyslexia, dashboard, etc.)
├── models/               # Data models (user, progress)
├── data/                 # CSV data files (progress, users, etc.)
├── templates/            # Jinja2 HTML templates
├── static/               # Static files (CSS, JS, uploads)
└── ...
```

---

## Installation & Local Development

1. **Clone the repository:**
	```bash
	git clone <repository-url>
	cd cognoflask-main
	```
2. **Create a virtual environment:**
	```bash
	python -m venv venv
	# On Windows:
	venv\Scripts\activate
	# On Mac/Linux:
	source venv/bin/activate
	```
3. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```
4. **Run the application:**
	```bash
	python app.py
	```
5. **Open your browser:**
	Go to [http://localhost:5000](http://localhost:5000)

---

## Demo Accounts

**Child Account:**
- Username: `demo_child`
- Password: `demo123`
- Email: `child@demo.com`

**Parent Account:**
- Username: `demo_parent`
- Password: `demo123`
- Email: `parent@demo.com`

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License.
# Learning Disability Support Platform

A comprehensive Flask-based web application providing AI-powered support for children with learning disabilities including Dyslexia, Dyscalculia, Dysgraphia, and Dyspraxia.

## Features

### 🧠 Dyslexia Support
- AI-powered text simplification
- Text-to-speech with adjustable settings
- Phonics games and sound matching
- Reading progress tracking
- Dyslexia-friendly fonts and formatting

### 🧮 Dyscalculia Support
- Adaptive math problem generation
- Visual math problems with objects
- Number line visualization
- Pattern recognition games
- Step-by-step problem solving

### ✍️ Dysgraphia Support
- Writing analysis and feedback
- Letter formation practice
- Creative writing prompts
- Handwriting improvement tools
- Spelling and grammar assistance

### 🏃 Dyspraxia Support
- Balance training exercises
- Coordination games
- Live camera movement tracking
- Motor skills assessment
- Real-time feedback system

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Storage**: CSV files (no database required)
- **AI/ML**: NLTK for text processing
- **Computer Vision**: OpenCV for movement tracking
- **Responsive Design**: Custom CSS Grid and Flexbox

## Installation

1. Clone the repository:
\`\`\`bash
git clone <repository-url>
cd learning-disability-platform
\`\`\`

2. Create a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Run the application:
\`\`\`bash
python app.py
\`\`\`

5. Open your browser and navigate to `http://localhost:5000`

## Quick Login

The platform includes demo accounts for quick testing:

**Child Account:**
- Username: `demo_child`
- Password: `demo123`
- Email: `child@demo.com`

**Parent Account:**
- Username: `demo_parent`
- Password: `demo123`
- Email: `parent@demo.com`

## File Structure

\`\`\`
learning-disability-platform/
├── app.py                          # Main Flask application
├── utils/
│   └── file_manager.py            # CSV file management utilities
├── modules/                       # Feature modules
│   ├── auth.py                   # Authentication system
│   ├── dyslexia.py              # Dyslexia support features
│   ├── dyscalculia.py           # Dyscalculia support features
│   ├── dysgraphia.py            # Dysgraphia support features
│   ├── dyspraxia.py             # Dyspraxia support features
│   └── dashboard.py             # Main dashboard
├── templates/                    # HTML templates
│   ├── base.html               # Base template with sidebar
│   ├── index.html              # Landing page
│   ├── auth/                   # Authentication templates
│   ├── dashboard/              # Dashboard templates
│   ├── dyslexia/              # Dyslexia feature templates
│   ├── dyscalculia/           # Dyscalculia feature templates
│   ├── dysgraphia/            # Dysgraphia feature templates
│   └── dyspraxia/             # Dyspraxia feature templates
├── data/                       # CSV data storage
│   ├── users/                 # User data
│   ├── dyslexia/             # Dyslexia progress data
│   ├── dyscalculia/          # Dyscalculia progress data
│   ├── dysgraphia/           # Dysgraphia progress data
│   └── dyspraxia/            # Dyspraxia progress data
├── static/                     # Static files
│   ├── uploads/              # User uploads
│   └── user_data/            # User-specific data
└── requirements.txt           # Python dependencies
\`\`\`

## Data Storage

All user data and progress is stored in CSV files within the `data/` directory:

- **User Management**: `data/users/users.csv`
- **Progress Tracking**: Individual CSV files for each module
- **Game Scores**: Stored in module-specific CSV files
- **AI Model Data**: Cached in `data/ai_models/`

## Features in Detail

### Responsive Design
- Mobile-first approach
- Collapsible sidebar navigation
- Touch-friendly interface
- Adaptive layouts for all screen sizes

### AI-Powered Features
- Text simplification using NLTK
- Difficulty level detection
- Adaptive problem generation
- Writing pattern analysis

### Camera Integration
- Real-time movement tracking
- Balance assessment
- Coordination exercises
- Privacy-focused (no data stored)

### Progress Tracking
- Comprehensive analytics
- Performance trends
- Personalized recommendations
- Export capabilities

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Privacy & Security

- All data stored locally in CSV files
- No external data transmission
- Camera access only when explicitly granted
- User data remains on your server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository.

## Acknowledgments

- OpenDyslexic font for improved readability
- NLTK for natural language processing
- OpenCV for computer vision capabilities
- Font Awesome for icons
