#!/bin/bash

# Portfolio Backend API Startup Script
# Charles Nwankpa - AI Product Engineer

set -e

echo "🚀 Starting Charles Nwankpa Portfolio Backend API..."

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is required"
    exit 1
fi

if [ -z "$JWT_SECRET" ]; then
    echo "❌ ERROR: JWT_SECRET environment variable is required"
    exit 1
fi

echo "✅ Environment variables validated"

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import asyncio
import asyncpg
import os
import sys

async def wait_for_db():
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = await asyncpg.connect(os.environ['DATABASE_URL'])
            await conn.execute('SELECT 1')
            await conn.close()
            print('✅ Database connection successful')
            return
        except Exception as e:
            retry_count += 1
            print(f'⏳ Database not ready (attempt {retry_count}/{max_retries})')
            if retry_count >= max_retries:
                print(f'❌ Failed to connect to database: {e}')
                sys.exit(1)
            await asyncio.sleep(2)

asyncio.run(wait_for_db())
"

# Run database migrations if needed
echo "📦 Checking database schema..."
python -c "
import asyncio
import asyncpg
import os

async def check_schema():
    try:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])
        
        # Check if leads table exists
        result = await conn.fetchval('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'leads'
            );
        ''')
        
        if not result:
            print('⚠️  Database schema not found. Please run migrations manually:')
            print('   psql \$DATABASE_URL -f migrations/001_initial_schema.sql')
        else:
            print('✅ Database schema verified')
            
        await conn.close()
    except Exception as e:
        print(f'⚠️  Could not verify database schema: {e}')

asyncio.run(check_schema())
"

# Start the application
echo "🌟 Starting FastAPI application..."

if [ "$ENVIRONMENT" = "development" ]; then
    echo "🔧 Development mode - auto-reload enabled"
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload --log-level debug
else
    echo "🚀 Production mode"
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-1} --log-level info
fi