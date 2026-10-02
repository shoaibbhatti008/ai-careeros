# Contributing to AI CareerOS

Thank you for your interest in contributing!

## Code of Conduct

By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to Contribute

- Report bugs (use the bug report template)
- Suggest features (use the feature request template)
- Improve documentation
- Add or improve tests
- Implement new agents or tools
- Review pull requests
- Improve security (see [SECURITY.md](SECURITY.md))

## Development Setup

See [DEVELOPMENT.md](DEVELOPMENT.md).

```bash
git clone https://github.com/shoaibbhatti008/ai-careeros.git
cd ai-careeros
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r backend/requirements/development.txt
cp .env.example .env