# Sentri Retail Demo - Frontend

Next.js-based frontend for the Sentri Retail Demo application.

## Features

- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Authentication**: JWT-based login/logout
- **AI Assistant**: Interactive chat interface
- **Dashboard**: Real-time security insights
- **Scan Results**: Visual risk assessment display

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **State**: React hooks

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit .env.local with your configuration

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                 # Next.js App Router pages
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Home page (redirects)
│   ├── login/           # Login page
│   ├── assistant/       # AI Assistant page
│   └── dashboard/       # Dashboard page
├── components/          # React components
│   ├── HeaderStatus.tsx # Header with status
│   ├── ChatBox.tsx      # Chat interface
│   ├── ActionButtons.tsx# Scan action buttons
│   ├── ResultCard.tsx   # Scan result display
│   ├── InsightCard.tsx  # Guardian insights
│   └── ActivityTable.tsx# Activity log table
└── lib/                 # Utilities
    ├── api.ts           # API client
    ├── auth.ts          # Auth utilities
    ├── demoScenarios.ts # Demo data
    └── types.ts         # TypeScript types
```

## Environment Variables

See `.env.example` for required configuration.

## Demo Credentials

- **Staff**: demo@sentri.demo / demo123
- **HQ IT**: analyst@sentri.demo / analyst123
- **Admin**: admin@sentri.demo / admin123
