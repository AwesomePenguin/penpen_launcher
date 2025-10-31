# Tests for PenPen Launcher Backend

This directory contains test files for the PenPen Launcher backend components.

## Running Tests

To run the backend tests:

```powershell
# Navigate to backend directory
cd backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_backend.py

# Run with detailed output
python tests/test_backend.py --verbose
```

## Test Files

- `test_backend.py` - Main backend component integration test
- `test_models.py` - Data model validation tests (future)
- `test_game_scanner.py` - Game scanning functionality tests (future)
- `test_process_manager.py` - Process management tests (future)
- `test_api.py` - API endpoint tests (future)

## Test Requirements

Tests require the following dependencies to be installed:
- All packages from `requirements.txt`
- Optional: `pytest` for advanced testing features

## Notes

- Tests are designed to work with or without `psutil` installed
- Some tests may require actual game installations for full validation
- Tests use mocking where appropriate to avoid system dependencies