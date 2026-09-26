# Contributing

SentinelOSINT is a defensive security-intelligence project. Contributions should improve reliability, analyst usability, source transparency, or documentation without enabling privacy-invasive collection or access-control bypass.

## Development

### API
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=. pytest -q
uvicorn main:app --reload --port 8000
```

### Web
```bash
cd apps/web
npm install
npm run lint
npm run build
npm run dev
```

## Pull requests

- keep changes focused and documented
- add or update tests for behavior changes
- keep synthetic data clearly marked
- preserve source attribution and verification states
- do not add credential scraping, private-account collection, doxxing, biometric identification, or access-control bypass features
- ensure CI passes before requesting review

For security concerns, see [SECURITY.md](SECURITY.md).
