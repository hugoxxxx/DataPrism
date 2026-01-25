---
name: backend-api-security
description: Technical skill for implementing robust API security, authentication, and authorization patterns.
---

# Backend API Security Skill

This skill provides comprehensive guidelines and patterns for securing backend APIs and handling sensitive authentication logic. It is based on the `wshobson/agents` security-auditor workflows.

## Core Capabilities

- **Secure Authentication**: Implementation of OAuth2, OpenID Connect, and JWT (JSON Web Tokens) with proper signing and rotation.
- **Granular Authorization**: Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC) patterns.
- **API Hardening**: 
    - Rate limiting and throttling.
    - Input validation and sanitization to prevent injection (SQLi, NoSQLi).
    - Proper CORS (Cross-Origin Resource Sharing) and CSP (Content Security Policy) configuration.
- **Secret Management**: Best practices for storing and accessing API keys, certificates, and environment variables (e.g., HashiCorp Vault, AWS Secrets Manager).
- **Security Auditing**: SAST (Static Application Security Testing) and automated dependency scanning.

## Usage Guidelines

1. **Defense in Depth**: Never rely on a single security measure. Combine authentication, authorization, and validation.
2. **Principle of Least Privilege**: Ensure users and services only have the minimum permissions required.
3. **Fail Securely**: Systems should default to a secure state in case of an error.
4. **Encrypt at Rest and in Transit**: Use TLS for all API communications and encrypt sensitive data in the database.

## Example Prompts

- "Implement a JWT-based authentication flow for the ExifTool service."
- "Apply rate limiting to the metadata injection endpoint to prevent brute-force attacks."
- "Perform a security audit of the current Python backend and suggest hardening measures."
- "Configure secure CORS settings for the frontend-to-backend communication."
