# Contributing to Time Analysis

Thank you for your interest in contributing to Time Analysis! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/time_analysis.git
   cd time_analysis
   ```
3. **Set up the development environment**:
   ```bash
   make install-dev
   # or
   pip install -e ".[dev]"
   pre-commit install
   ```

## Development Workflow

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Run tests** to ensure everything works:
   ```bash
   make test
   ```

4. **Format and lint your code**:
   ```bash
   make format
   make lint
   make type-check
   ```

5. **Commit your changes** with a clear message:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Code Standards

### Python Style Guide

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use type hints for all functions
- Write docstrings for all public functions and classes

### Type Hints

All functions should have type hints:

```python
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """Process the input data.

    Args:
        data: Raw input data

    Returns:
        Processed data
    """
    ...
```

### Documentation

- Use Google-style docstrings
- Include examples for complex functions
- Update README.md if adding new features

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use pytest fixtures for common test data
- Test edge cases and error conditions

Example test structure:

```python
def test_feature():
    """Test description."""
    # Arrange
    input_data = create_test_data()

    # Act
    result = process_function(input_data)

    # Assert
    assert result == expected_output
```

## Pull Request Guidelines

### PR Title Format

Use clear, descriptive titles:
- `feat: Add CSV batch processing`
- `fix: Handle empty activity details`
- `docs: Update installation instructions`
- `test: Add tests for data loader`
- `refactor: Simplify processor logic`

### PR Description

Include:
- What changes were made
- Why the changes were needed
- How to test the changes
- Any breaking changes
- Related issues (if applicable)

### Before Submitting

Ensure your PR:
- [ ] Passes all tests (`make test`)
- [ ] Follows code style (`make format` and `make lint`)
- [ ] Has type hints (`make type-check`)
- [ ] Includes tests for new features
- [ ] Updates documentation if needed
- [ ] Has a clear, descriptive title
- [ ] Has a detailed description

## Reporting Issues

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps to reproduce the behavior
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - Python version
   - Operating system
   - Package versions
6. **Sample Data**: Minimal data to reproduce (if applicable)

## Feature Requests

For feature requests, please:

1. Check if the feature already exists or is planned
2. Describe the feature and its use case
3. Explain why it would be valuable
4. Provide examples if possible

## Development Commands

Quick reference for common development tasks:

```bash
# Install dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Clean build artifacts
make clean

# Build distribution
make build
```

## Code Review Process

1. All PRs require review before merging
2. Address reviewer feedback
3. Keep PRs focused on a single feature/fix
4. Squash commits if requested
5. Maintain a clean git history

## Questions?

If you have questions:
- Open an issue for discussion
- Check existing issues and PRs
- Review the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing!
