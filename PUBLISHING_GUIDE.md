# Storm Agent - PyPI Publishing Guide

## 🎉 Package Status: READY FOR PUBLICATION

Your Storm Agent package has been successfully built and validated. Both distributions have **PASSED** all checks:
- ✅ `storm_agent-1.0.0-py3-none-any.whl` 
- ✅ `storm_agent-1.0.0.tar.gz`

## 📋 Prerequisites

Before publishing, you'll need:

1. **PyPI Account**: Create accounts at both:
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **API Tokens** (recommended over passwords):
   - TestPyPI: Generate token at https://test.pypi.org/manage/account/token/
   - PyPI: Generate token at https://pypi.org/manage/account/token/

## 🚀 Publishing Steps

### Step 1: Test Publication (Recommended)

First, publish to TestPyPI to verify everything works:

```bash
# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# When prompted, use:
# Username: __token__
# Password: your-testpypi-api-token
```

Test the installation from TestPyPI:
```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ storm-agent

# Test it works
python3 -c "from storm_agent import Agent; print('Storm Agent works!')"
```

### Step 2: Production Publication

Once tested, publish to production PyPI:

```bash
# Upload to PyPI
python3 -m twine upload dist/*

# When prompted, use:
# Username: __token__
# Password: your-pypi-api-token
```

## 🎯 Post-Publication

After successful publication:

1. **Verify Installation**:
   ```bash
   pip install storm-agent
   ```

2. **Test Import**:
   ```python
   from storm_agent import Agent, WebSearchAgent, DeepResearchAgent
   storm = Agent(name="Test Agent")
   print("Storm Agent is live on PyPI! 🌩️")
   ```

3. **Update Documentation**: Your package will be available at:
   - **PyPI Page**: https://pypi.org/project/storm-agent/
   - **Installation**: `pip install storm-agent`

## 🔧 Alternative: Using API Tokens in Configuration

For easier repeated uploads, configure your credentials:

```bash
# Create/edit ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = your-pypi-api-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-testpypi-api-token
```

Then simply run:
```bash
twine upload --repository testpypi dist/*  # For testing
twine upload dist/*                        # For production
```

## 🎉 Success!

Once published, users worldwide can install Storm Agent with:

```bash
pip install storm-agent
```

And start building powerful AI agents immediately! 🌩️

---

**Next Steps**: Consider setting up GitHub Actions for automated publishing on version tags.
