# ALADDIN Backend API

Subscription Management System for ALADDIN iOS Application

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## 🔑 API Endpoints

### Device Registration
- `POST /api/auth/register-device` - Register device with free subscription
- `POST /api/auth/register-device-trial` - Register device with trial

### Subscription Management
- `GET /api/subscription/status` - Get current subscription status
- `POST /api/subscription/upgrade` - Upgrade subscription level
- `POST /api/subscription/cancel` - Cancel subscription

### Feature Access
- `POST /api/features/check` - Check feature access permissions

### Usage Tracking
- `POST /api/usage/track` - Track resource usage
- `POST /api/usage/reset` - Reset monthly counters

### Trial Management
- `GET /api/trial/status` - Get trial status

## 🔐 Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <jwt_token>
```

## 📊 Subscription Levels

| Level | Devices | AI Messages | Scans | Reports |
|-------|---------|-------------|-------|---------|
| FREE | 1 | 10 | 5 | 2 |
| TRIAL | 3 | 50 | 100 | 10 |
| PERSONAL | 3 | 100 | 50 | 10 |
| FAMILY | 5 | 200 | 100 | 20 |
| PREMIUM | 10 | Unlimited | Unlimited | Unlimited |

## 🏗️ Architecture

```
backend/
├── app/
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   ├── routers/         # API endpoints
│   └── core/           # Core functionality
├── main.py             # FastAPI app
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## 🧪 Testing

Run the server and test endpoints using the Swagger UI at `/docs`

### Example: Register Device
```bash
curl -X POST "http://localhost:8000/api/auth/register-device" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "test-device-123", "device_type": "ios"}'
```

## 🔧 Configuration

Environment variables (create `.env` file):
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./aladdin.db
```

## 📈 Monitoring

- Health checks: `/health`
- Request logging via middleware
- Usage tracking for all resources

## 🚀 Production Deployment

```bash
# Using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# Using Docker
docker build -t aladdin-backend .
docker run -p 8000:8000 aladdin-backend
```

## 📞 Support

For issues and questions, check the API documentation or contact the development team.