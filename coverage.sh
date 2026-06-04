#!/bin/bash
# Coverage script for the biomedical research agent

set -e

echo "📊 Running comprehensive test coverage analysis..."

# Ensure we're in the project directory
cd "$(dirname "$0")"

# Clean up previous coverage reports
rm -rf htmlcov/
rm -rf coverage.xml
rm -rf .coverage

# Run tests with coverage
echo "🧪 Running unit tests with coverage..."
python -m pytest tests/unit/ \
    --cov=src/unit \
    --cov-report=term-missing \
    --cov-report=html:htmlcov/unit \
    --cov-report=xml \
    --cov-fail-under=85

echo "🔗 Running integration tests with coverage..."
python -m pytest tests/integration/ \
    --cov=src/integration \
    --cov-report=term-missing \
    --cov-report=html:htmlcov/integration \
    --cov-report=xml \
    --cov-fail-under=80

echo "🚀 Running E2E tests with coverage..."
python -m pytest tests/e2e/ \
    --cov=src/e2e \
    --cov-report=term-missing \
    --cov-report=html:htmlcov/e2e \
    --cov-report=xml \
    --cov-fail-under=75

echo "🛡️ Running security tests with coverage..."
python -m pytest tests/security/ \
    --cov=src/security \
    --cov-report=term-missing \
    --cov-report=html:htmlcov/security \
    --cov-report=xml \
    --cov-fail-under=90

# Generate combined coverage report
echo "📈 Generating combined coverage report..."
python -m coverage combine
python -m coverage report --show-missing
python -m coverage html --directory=htmlcov/combined

# Create coverage summary
echo "📋 Creating coverage summary..."
cat > coverage-summary.md << EOF
# Coverage Summary

## Test Coverage Overview

| Module | Coverage | Status |
|--------|----------|--------|
| Unit Tests | $(python -m coverage report --include=src/unit* | grep -o '[0-9]*\%' | head -1) | ✅ |
| Integration Tests | $(python -m coverage report --include=src/integration* | grep -o '[0-9]*\%' | head -1) | ✅ |
| E2E Tests | $(python -m coverage report --include=src/e2e* | grep -o '[0-9]*\%' | head -1) | ✅ |
| Security Tests | $(python -m coverage report --include=src/security* | grep -o '[0-9]*\%' | head -1) | ✅ |

## Detailed Reports

- **HTML Reports**: htmlcov/combined/index.html
- **XML Reports**: coverage.xml
- **Text Reports**: See output above

## Next Steps

1. Review detailed HTML reports for specific file coverage
2. Address any missing lines in low-coverage files
3. Ensure all critical paths are tested
4. Maintain coverage targets for production code

EOF

echo "✅ Coverage analysis complete!"
echo "📊 View HTML reports: open htmlcov/combined/index.html"
echo "📋 View summary: cat coverage-summary.md"