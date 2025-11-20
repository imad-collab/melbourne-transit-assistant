# Contributing to the Real-Time Parking System

Thank you for your interest in contributing! Here's how to get started.

## Code of Conduct

Be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug already exists in Issues.
2. Use the bug report template.
3. Include environment details.
4. Provide reproducible steps.

### Suggesting Enhancements

1. Use the feature request or question template.
2. Explain the use case.
3. Provide examples if possible.

### Submitting Code

1. Fork the repository
   ```bash
   git clone https://github.com/yourusername/parking-realtime.git
   cd parking-realtime
   ```
2. Create a branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make changes
   - Follow PEP 8 style guide
   - Write clean, documented code
   - Add tests if applicable
4. Test locally
   ```bash
   python -m pytest
   ```
5. Commit changes
   ```bash
   git commit -m "Add: description of changes"
   ```
6. Push and create a PR
   ```bash
   git push origin feature/your-feature-name
   ```
7. Describe your PR
   - What problem does it solve?
   - How does it solve it?
   - Any breaking changes?

## Development Setup

```bash
git clone https://github.com/yourusername/parking-realtime.git
cd parking-realtime
pip install -r requirements.txt
pip install pytest black flake8
```

## Testing

```bash
pytest
```

## Code Style

- Follow PEP 8. Format with Black:
  ```bash
  black .
  ```
- Check with flake8:
  ```bash
  flake8 .
  ```

## Documentation

- Update `README.md` for user-facing changes
- Add docstrings to functions
- Update `CHANGELOG.md`

## Questions?

Open a GitHub Discussion or Issue.
