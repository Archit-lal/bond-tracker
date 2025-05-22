# Bond Data Dashboard

A real-time bond data dashboard that aggregates information from NSE, BSE, and NSDL exchanges in India. This system automates the process of gathering comprehensive bond data and presents it in a user-friendly interface.

## Features

- **Real-time data updates**: Live streaming of bond transactions as they occur
- **Comprehensive bond information**: Details about bonds including ISIN, issuer, coupon rates, etc.
- **Transaction history**: Historical transaction data with prices, yields, and volumes
- **Visual analytics**: Charts and graphs to visualize market trends
- **Search and filtering**: Find specific bonds or transactions
- **Data from multiple sources**: Unified view of data from NSE, BSE, and NSDL

## System Architecture

The project follows a three-tier architecture:

1. **Data Acquisition Layer**
   - Web scrapers for NSE, BSE, and NSDL
   - Scheduled data retrieval
   - Error handling and retry mechanisms

2. **Data Processing Layer**
   - PostgreSQL database for structured data storage
   - Data normalization across sources
   - WebSocket service for real-time updates

3. **Presentation Layer**
   - React-based frontend with Material UI
   - Real-time dashboard with auto-updating data
   - Interactive charts and tables

## Technology Stack

### Backend
- **Programming Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Database**: PostgreSQL
- **Caching**: Redis
- **Task Queue**: Celery with Redis as broker
- **WebSockets**: FastAPI WebSockets

### Frontend
- **Framework**: React.js
- **UI Components**: Material-UI
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Routing**: React Router

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Development Environment**: Docker-based setup

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Installation and Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd bond-dashboard
   ```

2. Start the application using Docker Compose:
   ```
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

### Project Structure
```
bond-dashboard/
├── backend/               # Python backend code
│   ├── api/               # FastAPI routes and endpoints
│   ├── data_acquisition/  # Web scrapers for exchanges
│   ├── database/          # Database models and connection
│   └── utils/             # Utility functions and Celery setup
├── frontend/              # React frontend code
│   ├── public/            # Static assets
│   └── src/               # Source code
│       ├── components/    # React components
│       ├── hooks/         # Custom React hooks
│       ├── services/      # API and WebSocket services
│       └── utils/         # Utility functions
├── docker/                # Docker-related files
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

### Backend Development
To run the backend separately:
```
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### Frontend Development
To run the frontend separately:
```
cd frontend
npm install
npm start
```

## License

[MIT License](LICENSE)

## Acknowledgements

- NSE, BSE, and NSDL for providing the bond market data
- The open-source community for the amazing tools and libraries
