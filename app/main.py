from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime


app = FastAPI(
    title="EmployeeHub CRUD API",
    version="1.0.0",
    description="Interactive CRUD Dashboard built with FastAPI"
)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EmployeeHub CRUD Dashboard</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .card {
                background: rgba(255, 255, 255, 0.15);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.25);
                backdrop-filter: blur(10px);
                max-width: 700px;
                text-align: center;
            }

            h1 {
                font-size: 48px;
                margin-bottom: 10px;
            }

            p {
                font-size: 18px;
                line-height: 1.6;
            }

            .buttons {
                margin-top: 30px;
            }

            a {
                display: inline-block;
                margin: 10px;
                padding: 14px 24px;
                border-radius: 10px;
                text-decoration: none;
                background: white;
                color: #764ba2;
                font-weight: bold;
                transition: 0.3s;
            }

            a:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.25);
            }

            .badge {
                display: inline-block;
                margin-top: 20px;
                padding: 8px 16px;
                border-radius: 30px;
                background: rgba(255,255,255,0.2);
                font-size: 14px;
            }
        </style>
    </head>

    <body>
        <div class="card">
            <h1>EmployeeHub 🚀</h1>
            <p>
                Welcome to your FastAPI CRUD Dashboard.
                Yahan hum REST API, FastAPI, UI, Database aur CI/CD pipeline
                ek production-style project me seekhenge.
            </p>

            <div class="buttons">
                <a href="/docs">Open API Docs</a>
                <a href="/health">Check Health</a>
            </div>

            <div class="badge">
                Status: Running ✅
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "EmployeeHub API is running successfully",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/info")
def api_info():
    return {
        "project": "EmployeeHub CRUD Dashboard",
        "version": "1.0.0",
        "features": [
            "FastAPI",
            "REST API",
            "CRUD",
            "Interactive UI",
            "CI/CD Pipeline"
        ]
    }