# Frontend Setup Instructions

## Prerequisites
- Node.js 16+ 
- npm or yarn

## Setup Steps

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Open in browser**
   ```
   http://localhost:3000
   ```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Environment Variables

Create a `.env` file in the frontend directory:

```bash
REACT_APP_API_URL=http://localhost:8000
```

## Features

- **Dashboard**: Real-time statistics and charts
- **Birds**: Manage individual bird profiles
- **Visits**: Track and analyze visit patterns
- **Alerts**: Monitor feeder status and notifications
- **Summaries**: View AI-generated daily reports
- **Settings**: Configure system preferences

## Development

The frontend is built with:
- React 18
- React Router for navigation
- React Query for data fetching
- Tailwind CSS for styling
- Lucide React for icons
- Recharts for data visualization
