
# GitHub Issues Template - Release Blockers

## 🚨 Critical Issues (Must Fix Before Release)

### Issue 1: Security Vulnerability - MD5 Hash Usage
**Title**: Security: Fix MD5 hash usage in error_monitoring_system.py
**Labels**: security, critical, bug
**Priority**: 🔴 HIGH

**Description**:
MD5 hashing is being used for security purposes in `error_monitoring_system.py:67`, which is cryptographically weak and vulnerable to collision attacks.

**Acceptance Criteria**:
- [ ] Replace MD5 with SHA-256 or explicitly disable security usage
- [ ] Verify no other MD5 usage exists in codebase
- [ ] Run bandit scan to confirm fix

---

### Issue 2: Low Test Coverage
**Title**: Testing: Increase test coverage from 46% to ≥80%
**Labels**: testing, coverage, enhancement
**Priority**: 🔴 HIGH

**Description**:
Current test coverage is 46.00%, well below the target of 80%. Critical files have minimal or no coverage.

**Files to Focus On**:
- `universal_content_processor.py` (0% coverage)
- `working_universal_processor.py` (9.42% coverage)
- `wiki_downloader.py` (16.05% coverage)
- `wiki_integration.py` (14.10% coverage)

**Acceptance Criteria**:
- [ ] Achieve ≥80% overall test coverage
- [ ] All critical files have ≥70% coverage
- [ ] Add integration tests for main workflows

---

### Issue 3: Async Test Fixture Failures
**Title**: Testing: Fix 39 failing tests due to async fixture issues
**Labels**: testing, bug, async
**Priority**: 🔴 HIGH

**Description**:
39 tests are failing primarily due to async fixture configuration problems. Common error: `AttributeError: 'async_generator' object has no attribute`

**Affected Test Files**:
- `test_error_handling_systems.py`
- `test_enhanced_genre_mapper_integration.py`
- `test_wiki_downloader.py`
- `test_wiki_integration.py`

**Acceptance Criteria**:
- [ ] All 39 failing tests pass
- [ ] Async fixtures properly configured
- [ ] Test patterns consistent with async best practices

---

### Issue 4: Dependency Conflicts
**Title**: Dependencies: Resolve pydantic version conflicts
**Labels**: dependencies, bug
**Priority**: 🟡 MEDIUM

**Description**:
Pydantic version mismatch - installed 2.9.2 but fastmcp and mcp require ≥2.11.7

**Acceptance Criteria**:
- [ ] Update pyproject.toml to require pydantic ≥2.11.7
- [ ] Resolve any compatibility issues
- [ ] Test with updated dependencies

---

## ⚠️ Important Issues (Should Fix Before Release)

### Issue 5: Missing Documentation
**Title**: Documentation: Create CHANGELOG.md and release notes
**Labels**: documentation, enhancement
**Priority**: 🟡 MEDIUM

**Description**:
Missing CHANGELOG.md file and release notes for version 1.0.0

**Acceptance Criteria**:
- [ ] Create CHANGELOG.md with standard format
- [ ] Add release notes for v1.0.0
- [ ] Ensure all API documentation is complete

---

### Issue 6: Async Architecture Refinement
**Title**: Refactor: Improve async patterns and error handling
**Labels**: refactor, async, enhancement
**Priority**: 🟡 MEDIUM

**Description**:
Inconsistent async/await patterns and error handling throughout codebase

**Acceptance Criteria**:
- [ ] Consistent async patterns across all files
- [ ] Proper error handling for async operations
- [ ] Performance optimization for async calls

---

## 📋 Issue Creation Commands

For quick issue creation, use these GitHub CLI commands:

```bash
# Critical Issues
gh issue create --title "Security: Fix MD5 hash usage in error_monitoring_system.py" --body "MD5 hashing is being used for security purposes..." --label "security,critical,bug"

gh issue create --title "Testing: Increase test coverage from 46% to ≥80%" --body "Current test coverage is 46.00%..." --label "testing,coverage,enhancement"

gh issue create --title "Testing: Fix 39 failing tests due to async fixture issues" --body "39 tests are failing primarily due to async fixture configuration problems..." --label "testing,bug,async"

# Important Issues
gh issue create --title "Dependencies: Resolve pydantic version conflicts" --body "Pydantic version mismatch..." --label "dependencies,bug"

gh issue create --title "Documentation: Create CHANGELOG.md and release notes" --body "Missing CHANGELOG.md file..." --label "documentation,enhancement"
```

## 🎯 Priority Order
1. Security vulnerabilities
2. Test coverage improvement
3. Test failure fixes
4. Dependency resolution
5. Documentation
6. Async architecture refinement

**Estimated Timeline**: 3-4 weeks to address all critical issues
