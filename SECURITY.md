# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |
| < 0.1   | ❌        |

## Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Report privately via one of:

1. GitHub Security Advisories:  
   https://github.com/shoaibbhatti008/ai-careeros/security/advisories/new
2. Email: `shoaibbhatti008@users.noreply.github.com`

Include:
- A clear description of the issue
- Steps to reproduce
- Affected versions / components
- Potential impact
- Any suggested fix or mitigation

## Response Timeline

- **Acknowledgement:** within 72 hours
- **Initial assessment:** within 7 days
- **Fix or mitigation plan:** within 30 days for confirmed issues

## Scope

**In scope:**
- Authentication and authorization flaws
- IDOR / broken access control
- Prompt-injection bypasses that lead to unsafe actions
- Tool-permission bypasses
- Approval-workflow bypasses
- Data leakage across users
- RAG ownership-filter bypasses
- Injection flaws (SQLi, XSS, CSRF, command injection)
- Insecure file upload handling
- Secret exposure
- Agent loops / resource exhaustion

**Out of scope:**
- Social engineering
- Physical attacks
- Denial of service via volumetric attacks
- Issues in third-party dependencies without a proven exploit path

## Security Design Principles

AI CareerOS is designed with the following non-negotiable rules:

1. **No arbitrary code execution.** Agents cannot run shell, Python, or JavaScript.
2. **No secret access.** Agents cannot read `.env`, API keys, SSH keys, or cookies.
3. **No cross-user access.** Every query enforces ownership at the database level.
4. **No direct execution of AI output.** All outputs are validated and authorized.
5. **No sensitive action without approval.** Emails, applications, and destructive
   actions require explicit human approval.
6. **Untrusted external content.** Websites, PDFs, DOCX, job descriptions, and
   search results are treated as untrusted and screened for prompt injection.
7. **Bounded execution.** Every workflow has step, tool-call, and time limits.
8. **Full audit trail.** Agent, tool, and approval events are logged with trace IDs.

## Safe Harbor

We will not pursue legal action against researchers who:
- Act in good faith
- Avoid privacy violations and service disruption
- Report findings promptly and privately
- Do not exploit findings beyond what is necessary to demonstrate the issue

## Acknowledgements

We thank security researchers who help keep AI CareerOS and its users safe.