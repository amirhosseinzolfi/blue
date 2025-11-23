# Contributing to AI Chatbot Platform

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/blue.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Install dependencies
python3 main.py install

# Copy environment configuration
cp .env.example config/.env

# Edit config/.env with your settings

# Run tests
python3 launcher.py test
```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

## Testing

- Test all interfaces (Chainlit, Telegram, Web, API) before submitting
- Ensure backward compatibility
- Add tests for new features

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Update documentation if needed

## Reporting Issues

- Use the GitHub issue tracker
- Provide detailed reproduction steps
- Include error messages and logs
- Specify your environment (OS, Python version, etc.)

## Questions?

Feel free to open an issue for questions or discussions.
