# RV Capital Bond Data Platform

A full-stack application for tracking and analyzing bond market data from NSE and BSE exchanges.

## Features

- Real-time bond data scraping from NSE and BSE
- Historical data analysis
- Automated data updates
- Modern web interface
- RESTful API

## Tech Stack

- **Frontend**: React.js
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Containerization**: Docker
- **Web Scraping**: Selenium

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Chrome/Chromium (for web scraping)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rv-capital.git
   cd rv-capital
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Start the application:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

## Project Structure

```
rv-capital/
├── backend/
│   ├── api/
│   ├── database/
│   ├── utils/
│   └── main.py
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NSE India for bond market data
- BSE India for bond market data 