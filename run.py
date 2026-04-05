#!/usr/bin/env python3
import sys
import uvicorn


def main():
    if "--seed" in sys.argv:
        from app.seed import seed_database
        seed_database()

    print("\nStarting Finance Tracker...")
    print("Dashboard: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
