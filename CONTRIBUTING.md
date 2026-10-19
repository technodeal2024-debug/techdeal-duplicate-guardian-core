# Contributing

Contributions that improve the read-only duplicate scanner are welcome: bug reports, test cases, documentation and carefully reviewed code.

## Safe reporting
- Search existing issues before opening a new report.
- Provide your OS, Python version, current commit, expected vs actual result and a small **synthetic** test dataset.
- Do not post private paths, unredacted scan reports, passwords, signing material or personal documents.
- Security issues should be disclosed privately following SECURITY.md.

## Development
1. Run: python -m pip install -e '.[test]'
2. Run: python -m pytest -q
3. Try a small local test folder with examples/basic_usage.py.
4. Open a focused pull request explaining safety impact and any platform-specific testing.

Do not add deletion, file moves, uploads or telemetry. Do not copy proprietary Android/Windows app code. You must have rights to submit contributions under MIT.
