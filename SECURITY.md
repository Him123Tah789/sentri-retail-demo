# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Sentri Retail Demo, please report it by emailing security@example.com. All security vulnerabilities will be promptly addressed.

## Security Measures

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- Secure password hashing
- Session management

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

### Infrastructure Security
- Environment variable protection
- Secure Docker configurations
- Rate limiting
- CORS policy enforcement

### Development Security
- Dependency vulnerability scanning
- Code security analysis
- Secure coding practices
- Regular security updates

## Security Best Practices

When deploying this application:

1. **Environment Variables**: Never commit sensitive data to version control
2. **Database Security**: Use strong passwords and restrict access
3. **Network Security**: Implement proper firewall rules
4. **SSL/TLS**: Use HTTPS in production
5. **Monitoring**: Implement security logging and monitoring
6. **Updates**: Keep dependencies and base images updated

## Vulnerability Disclosure

We follow responsible disclosure practices:
- Report vulnerabilities privately first
- Allow reasonable time for fixes
- Coordinate public disclosure
- Credit reporters appropriately