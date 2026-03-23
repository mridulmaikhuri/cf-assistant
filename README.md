# CF Assistant

A Codeforces problem recommendation system that helps competitive programmers discover problems tailored to their skill level and interests.

## Overview

CF Assistant connects to the Codeforces API to analyze user profiles and submission history, then recommends suitable problems based on rating, tags, and difficulty progression. The application consists of a FastAPI backend and a React TypeScript frontend.

## Project Structure

```
cf-assistant/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Application entry point
│   ├── api.py              # Codeforces API integration
│   ├── user.py             # User-related routes and logic
│   ├── recommender.py      # Problem recommendation engine
│   ├── requirements.txt    # Python dependencies
│   └── venv/               # Virtual environment
│
└── frontend/               # React TypeScript frontend
    ├── src/
    │   ├── App.tsx         # Main application component
    │   ├── main.tsx        # React entry point
    │   ├── index.css       # Global styles
    │   ├── pages/
    │   │   └── Problems.tsx # Problems display page
    │   ├── components/     # Reusable React components
    │   └── constants/
    │       └── config.ts   # Configuration constants
    ├── package.json        # Node.js dependencies
    ├── vite.config.ts      # Vite build configuration
    └── tsconfig.json       # TypeScript configuration
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.135.1
- **Server**: Uvicorn 0.41.0
- **HTTP Client**: Requests 2.32.5
- **Language**: Python 3

### Frontend
- **Library**: React 19.2.0
- **Language**: TypeScript 5.9.3
- **Build Tool**: Vite 7.3.1
- **Styling**: Tailwind CSS 4.2.1
- **Routing**: React Router DOM 7.13.1
- **Visualization**: Recharts 3.8.0
- **Components**: React Tooltip, React Calendar Heatmap

## Features

- **User Profile Lookup**: Fetch user information from Codeforces API
- **Submission History**: Analyze user's past submissions and solved problems
- **Smart Recommendations**: AI-powered problem recommendations based on:
  - Problem rating/difficulty
  - Problem tags and topics
  - User's current skill level
  - Problem-solving progression
- **Responsive UI**: Modern, user-friendly interface with Tailwind CSS
- **Caching**: Optimized API calls with intelligent caching (1-hour submission cache, 2-day problemset cache)

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   python main.py
   ```
   The API will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173` (or another port shown in terminal)

## Available Scripts

### Backend
- `python main.py` - Start the development server with hot reload

### Frontend
- `npm run dev` - Start Vite development server
- `npm run build` - Build for production (TypeScript compilation + Vite bundle)
- `npm run lint` - Run ESLint to check code quality
- `npm run preview` - Preview the production build locally

## API Endpoints

### User Routes
- `GET /user/problems/{handle}` - Get recommended problems for a use

## Configuration

Update the frontend configuration in [frontend/src/constants/config.ts](frontend/src/constants/config.ts):

```typescript
export const API_BASE_URL = "http://127.0.0.1:8000";
export const USER_HANDLE = "your_codeforces_handle";
```

## Caching Strategy

- **Submissions**: Cached for 1 hour to reduce API calls
- **Problemset**: Cached for 2 days to minimize load on Codeforces API
- **Recommendations**: Cached for 1 day to reduce processing time

## Future Enhancements

- Make the system adaptive so that it learns from user feedback
- Advanced filtering by tag combinations
- Problem difficulty progression tracking
- Submission analytics dashboard
- Problem solution suggestions
- User activity history

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please open an issue on the project repository.
