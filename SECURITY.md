# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. **Do NOT** open a public issue
2. Email the maintainers directly (or use GitHub Security Advisories)
3. Include detailed information about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Security Best Practices

### Environment Variables
- Never commit `.env` files to the repository
- Use `.env.example` as a template
- Keep API keys and tokens secure
- Rotate credentials regularly

### Database
- SQLite database files are excluded from Git via `.gitignore`
- Ensure proper file permissions on production systems
- Regular backups recommended

### API Security
- Use HTTPS in production
- Implement rate limiting
- Validate all user inputs
- Keep dependencies updated

### Telegram Bot
- Keep bot token secure
- Validate user permissions
- Implement command rate limiting

## Dependencies

Keep dependencies updated to receive security patches:

```bash
pip install --upgrade -r requirements.txt
```

## Disclosure Policy

We follow responsible disclosure practices and will:
- Acknowledge receipt of vulnerability reports within 48 hours
- Provide regular updates on the status
- Credit reporters (unless they prefer to remain anonymous)
- Release security patches as soon as possible
