#!/bin/bash

# IGDB Game Recommendation System - Local Development Setup Script
# This script sets up the local development environment

set -e

# Check for required tools
echo "Checking for required tools..."

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.9+ and try again."
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your IGDB API credentials."
fi

# Create directories if they don't exist
mkdir -p web-app/backend/db
mkdir -p web-app/frontend/pages
mkdir -p web-app/frontend/components
mkdir -p web-app/frontend/hooks
mkdir -p web-app/frontend/utils

# Create basic API files if they don't exist
mkdir -p web-app/backend/api
if [ ! -f web-app/backend/api/__init__.py ]; then
    echo "Creating basic API files..."
    touch web-app/backend/api/__init__.py
    
    # Create main.py if it doesn't exist
    if [ ! -f web-app/backend/api/main.py ]; then
        cat > web-app/backend/api/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="IGDB Game Recommendation API",
    description="API for game recommendations based on IGDB data",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the IGDB Game Recommendation API"}

@app.get("/health")
async def health():
    return {"status": "ok"}
EOF
    fi
fi

# Create basic Next.js files if they don't exist
if [ ! -f web-app/frontend/pages/index.js ] && [ ! -f web-app/frontend/pages/index.tsx ]; then
    echo "Creating basic Next.js files..."
    
    # Create index.tsx
    cat > web-app/frontend/pages/index.tsx << 'EOF'
import React from 'react';
import Head from 'next/head';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <Head>
        <title>IGDB Game Recommender</title>
        <meta name="description" content="Find your next favorite game" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="flex flex-col items-center justify-center min-h-screen py-2">
        <h1 className="text-4xl font-bold mb-8">
          Welcome to IGDB Game Recommender
        </h1>
        
        <p className="text-xl mb-4">
          Find your next favorite game based on intelligent recommendations
        </p>
        
        <div className="mt-8 p-6 border rounded-lg bg-gray-50">
          <p>API Status: Connecting...</p>
        </div>
      </main>
    </div>
  );
}
EOF
    
    # Create _app.tsx
    cat > web-app/frontend/pages/_app.tsx << 'EOF'
import '../styles/globals.css';
import type { AppProps } from 'next/app';

function MyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}

export default MyApp;
EOF
    
    # Create styles directory and globals.css
    mkdir -p web-app/frontend/styles
    cat > web-app/frontend/styles/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

html,
body {
  padding: 0;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen,
    Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
}

a {
  color: inherit;
  text-decoration: none;
}

* {
  box-sizing: border-box;
}
EOF
    
    # Create tailwind.config.js
    cat > web-app/frontend/tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF
    
    # Create postcss.config.js
    cat > web-app/frontend/postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF
    
    # Create tsconfig.json
    cat > web-app/frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
EOF
    
    # Create next-env.d.ts
    cat > web-app/frontend/next-env.d.ts << 'EOF'
/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/basic-features/typescript for more information.
EOF
fi

echo "Setup complete! You can now run the following command to start the local development environment:"
echo "cd web-app && docker-compose up -d"
echo ""
echo "Don't forget to add your IGDB API credentials to the .env file."
