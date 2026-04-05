#!/usr/bin/env python3
"""
Simple start script for the Finance Tracker application.

Usage:
    python run.py          # Start the server
    python run.py --seed   # Seed the database and start
"""

import sys
import uvicorn


def main():
    # Seed database if requested
    if "--seed" in sys.argv:
        from app.seed import seed_database
        seed_database()

    # Start the server
    print("\n🚀 Starting Finance Tracker...")
    print("   Dashboard:  http://localhost:8000")
    print("   API Docs:   http://localhost:8000/docs")
    print("   ReDoc:      http://localhost:8000/redoc\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
