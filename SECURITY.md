# Security Policy

## Supported Versions

The following versions of Wyzeapy are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Wyzeapy seriously. If you believe you have found a security vulnerability in this project, please report it to us responsibly.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please use one of the following methods:

1. **GitHub Private Vulnerability Reporting (Preferred):** Use GitHub's [private vulnerability reporting feature](https://github.com/SecKatie/wyzeapy/security/advisories/new) to submit your report directly through the repository.

2. **Email:** Send an email to [katie@mulliken.net](mailto:katie@mulliken.net) with the subject line "Wyzeapy Security Vulnerability Report".

### What to Include

Please include the following information in your report:

- A clear description of the vulnerability
- Steps to reproduce the issue
- Affected versions
- Potential impact of the vulnerability
- Any suggested fixes or mitigations (optional)

### What to Expect

After you submit a vulnerability report:

1. **Acknowledgment:** You will receive an acknowledgment of your report within 48 hours.

2. **Initial Assessment:** Within 7 days, we will provide an initial assessment of the vulnerability and an estimated timeline for a fix.

3. **Resolution Timeline:** We aim to resolve critical vulnerabilities within 30 days and other vulnerabilities within 90 days of the initial report.

4. **Disclosure:** We follow coordinated vulnerability disclosure practices. We will work with you to determine an appropriate disclosure timeline once a fix is available.

5. **Credit:** If you would like to be credited for the discovery, please let us know how you would like to be acknowledged.

### Scope

The following are considered in-scope for security vulnerability reports:

- Authentication and authorization issues
- Credential exposure or leakage
- Injection vulnerabilities
- Sensitive data exposure
- Security misconfigurations in the library code

The following are generally out of scope:

- Issues in third-party dependencies (please report these to the respective maintainers)
- Issues related to the Wyze API itself (please report these to Wyze)
- Social engineering attacks
- Denial of service attacks

## Security Best Practices for Users

When using Wyzeapy:

- Never commit credentials or API keys to version control
- Store sensitive configuration in environment variables or secure vaults
- Keep the library updated to the latest version
- Review the permissions and scopes requested by your integration

## Contact

For security-related inquiries, contact: [katie@mulliken.net](mailto:katie@mulliken.net)

For general questions and non-security issues, please use [GitHub Issues](https://github.com/SecKatie/wyzeapy/issues).
