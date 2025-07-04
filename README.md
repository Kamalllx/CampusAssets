# Campus Assets

## 🚀 Project Overview

A comprehensive resource monitoring system designed for college labs and locations, enabling administrators to manage equipment inventory through multiple interfaces including manual CRUD operations, CSV/Excel uploads, and AI-powered natural language processing.

## 🛠️ Tech Stack

### Backend
- **Framework:** Python Flask
- **Database:** MongoDB Atlas
- **AI Integration:** Groq API (Free tier)
- **Authentication:** Firebase Authentication
- **File Processing:** pandas, openpyxl
- **Deployment:** Railway/PythonAnywhere

### Frontend
- **Framework:** Next.js
- **Deployment:** Vercel/Netlify
- **UI Components:** Tailwind CSS + Shadcn/UI

### Additional Services
- **Email Service:** Gmail SMTP for admin verification
- **File Storage:** Local/Cloud storage for CSV/Excel uploads

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   Flask API     │    │   MongoDB       │
│   Frontend      │◄──►│   Backend       │◄──►│   Atlas         │
│                 │    │                 │    │                 │
│ - Landing Page  │    │ - Auth Routes   │    │ - Users DB      │
│ - Dashboard     │    │ - CRUD API      │    │ - Resources DB  │
│ - Chat Interface│    │ - AI Processing │    │ - Sessions DB   │
│ - File Upload   │    │ - File Handler  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   External      │
                       │   Services      │
                       │                 │
                       │ - Groq AI       │
                       │ - Firebase Auth │
                       │ - Gmail SMTP    │
                       └─────────────────┘
```

## 🔐 Authentication Flow

### User Types
1. **Admin/Operator** - Full CRUD permissions (requires master email approval)
2. **Viewer/Normal User** - Read-only access (instant approval)

### Authentication Process
```
User Registration → Firebase Auth → Role Assignment → 
Admin? → Email Verification → Master Approval → Account Activation
Viewer? → Direct Account Activation
```

## 🎯 Core Features

### 📋 Resource Management
- **Fields:** SL No, Description, Service Tag, Identification Number, Procurement Date, Cost, Location, Department
- **Operations:** Create, Read, Update, Delete (Admin only)
- **Bulk Operations:** CSV/Excel upload with validation
- **Smart Filtering:** Location, Department, Cost range based

### 🤖 AI-Powered Features
1. **Natural Language CRUD Agent**
   - Accepts plain English instructions
   - Extracts required fields intelligently
   - Validates completeness before execution

2. **Smart Retrieval Chatbot**
   - Answers queries about resources
   - Uses advanced retrieval algorithms
   - Context-aware responses

### 📊 Data Export & Analytics
- **Export Formats:** CSV, Excel
- **Filter Options:** Location, Department, Date range, Cost range
- **Dashboard:** Visual analytics and insights

## 🗂️ Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "firebase_uid": "string",
  "email": "string",
  "role": "admin|viewer",
  "status": "pending|approved|rejected",
  "created_at": "datetime",
  "session_ids": ["string"]
}
```

### Resources Collection
```json
{
  "_id": "ObjectId",
  "sl_no": "string",
  "description": "string",
  "service_tag": "string",
  "identification_number": "string",
  "procurement_date": "date",
  "cost": "number",
  "location": "string",
  "department": "string",
  "created_by": "string",
  "updated_at": "datetime"
}
```

### Sessions Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "session_token": "string",
  "expires_at": "datetime",
  "created_at": "datetime"
}
```

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/verify-admin` - Admin verification
- `POST /api/auth/logout` - User logout

### Resources
- `GET /api/resources` - List all resources (with filtering)
- `POST /api/resources` - Create new resource (Admin only)
- `GET /api/resources/:id` - Get specific resource
- `PUT /api/resources/:id` - Update resource (Admin only)
- `DELETE /api/resources/:id` - Delete resource (Admin only)

### File Operations
- `POST /api/upload/csv` - Upload CSV/Excel file (Admin only)
- `GET /api/export/csv` - Export data as CSV
- `GET /api/export/excel` - Export data as Excel

### AI Features
- `POST /api/ai/natural-crud` - Natural language CRUD operations
- `POST /api/ai/chat` - Chat with AI assistant
- `GET /api/ai/chat/history` - Chat history

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/charts` - Chart data

## 🔧 Backend File Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models and schemas
├── auth.py               # Authentication handlers
├── resources.py          # Resource CRUD operations
├── ai_agent.py           # AI processing and chat
├── file_handler.py       # CSV/Excel processing
├── utils.py              # Utility functions
├── test.py               # Interactive CLI testing
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔄 Deployment Steps

### Backend (Railway/PythonAnywhere)
1. Set up MongoDB Atlas connection
2. Configure Firebase Authentication
3. Set up Groq API key
4. Configure Gmail SMTP
5. Deploy Flask application

### Frontend (Vercel/Netlify)
1. Set up Next.js application
2. Configure environment variables
3. Connect to backend API
4. Deploy application

## 🔐 Environment Variables

```env
# Database
MONGODB_URI=mongodb+srv://...

# Authentication
FIREBASE_CONFIG={}
FIREBASE_ADMIN_SDK={}

# AI
GROQ_API_KEY=your_groq_api_key

# Email
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
MASTER_EMAIL=master_verification@gmail.com

# Security
JWT_SECRET=your_jwt_secret
FLASK_SECRET_KEY=your_flask_secret
```

## 📝 Integration Steps

### Firebase Authentication Setup
1. Create Firebase project
2. Enable Authentication with Email/Password and Google OAuth
3. Generate service account key
4. Configure authentication rules

### MongoDB Atlas Setup
1. Create cluster
2. Set up database user
3. Configure network access
4. Get connection string

### Groq AI Setup
1. Sign up for free account
2. Generate API key
3. Configure rate limits

## 🧪 Testing Strategy

The `test.py` file will provide an interactive CLI to test all endpoints:
- Authentication flow testing
- CRUD operations testing
- File upload/download testing
- AI features testing
- Session management testing

