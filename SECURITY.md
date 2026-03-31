# Security & Dependency Management

## npm Supply Chain Security

Due to recent npm ecosystem vulnerabilities and supply chain attacks, we follow strict dependency practices:

### Package Age Requirements

**All new npm packages must be at least 7 days old before integration.**

- Check package publish date: `npm view <package> time.created`
- Verify publish history: https://www.npmjs.com/package/<package>
- Wait for community security review & CVE discovery window
- Use `npm audit` before upgrading

### Current Dependencies

All packages in `frontend/package.json` are production-tested and stable:

- `react@^18.2.0` - Core UI framework
- `react-dom@^18.2.0` - DOM renderer
- `react-router-dom@^6.20.0` - Routing
- `axios@^1.6.0` - HTTP client
- `recharts@^2.10.0` - Charting library
- `@tanstack/react-query@^5.25.0` - Data fetching

### Security Best Practices

1. **Pin major versions** - Use `^` for patches/minors, but lock majors
2. **Review `package-lock.json`** - Commit lock file to git
3. **Run `npm audit` regularly** - Check for known vulnerabilities
4. **Audit transitive dependencies** - Use `npm ls` to inspect tree
5. **Update cautiously** - Test updates in isolated branch first
6. **Monitor CVE databases**:
   - GitHub Security Advisories
   - npm public advisories
   - Snyk vulnerability tracker

### Updating Dependencies

When adding or updating packages:

```bash
# Check age of package
npm view <package> time

# Add package (waits 7+ days before integrating)
npm install <package>

# Audit before committing
npm audit

# Review lock file changes
git diff package-lock.json

# Commit lock file with changes
git add package-lock.json package.json
git commit -m "Add <package> - published 7+ days ago, audit clean"
```

### Backend (Python)

Similar practices apply to Python packages in `backend/requirements.txt`:

- All packages from PyPI with established track records
- Consider using `pip-audit` for vulnerability scanning
- Lock versions in production: `pip freeze > requirements.lock`
- Review `pipdeptree` for dependency chains

## References

- [npm Security Best Practices](https://docs.npmjs.com/about-npm-security)
- [GitHub Security Advisories](https://github.com/advisories)
- [Snyk Vulnerability Database](https://snyk.io/vulnerability-scanner/)
