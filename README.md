# XAU Quant Platform

Multi-agent quantitative research platform for XAUUSD.

## Features

- Market data collection
- Regime detection
- Walk-forward optimization
- Monte Carlo testing
- Risk analytics
- Trade logging
- Performance reporting

## Installation

### Prerequisites
- Python 3.9 or higher
- pip or conda

### Setup

```bash
# Clone repository
git clone https://github.com/TopNotch87-prog/xau-quant-platform.git
cd xau-quant-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your settings:
```env
YFINANCE_API_KEY=your_key_here
DB_PATH=./data/
LOG_LEVEL=INFO
INITIAL_CAPITAL=10000
```

## Usage

```bash
python main.py
```

## Development

### Install development dependencies

```bash
pip install -r requirements-dev.txt
```

### Running tests

```bash
pytest --cov
```

### Code formatting and linting

```bash
# Format code
black .

# Check code style
flake8 .

# Type checking
mypy .
```

## Docker

Build and run using Docker:

```bash
# Build image
docker build -t xau-quant-platform .

# Run container
docker run -v $(pwd)/data:/app/data xau-quant-platform
```

## License

[Specify your license here]

## Contributing

Pull requests welcome! Please ensure all tests pass and code is formatted with Black.
