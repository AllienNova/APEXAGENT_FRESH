# ApexAgent Development Workflow Guide

## Overview

This guide outlines the recommended development workflow for the ApexAgent project. Following these practices will ensure consistency, quality, and efficiency across the development team.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Development Workflow](#development-workflow)
3. [Code Quality Standards](#code-quality-standards)
4. [Testing Practices](#testing-practices)
5. [Pull Request Process](#pull-request-process)
6. [Release Process](#release-process)
7. [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites

- Docker and Docker Compose
- Node.js (v16+)
- Git
- IDE of choice (VSCode recommended)

### Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/AllienNova/ApexAgent.git
   cd ApexAgent
   ```

2. Run the setup script:
   ```bash
   ./src/devex/local_env/setup.sh
   ```

3. Configure your IDE:
   - For VSCode, install recommended extensions from `.vscode/extensions.json`
   - Configure linting and formatting settings

### Development Scripts

The project includes a comprehensive development script that simplifies common tasks:

```bash
# Start the development environment
./dev.sh start

# View logs
./dev.sh logs [service]

# Run tests
./dev.sh test [path]

# Lint code
./dev.sh lint [--fix]

# Generate code components
./dev.sh generate [component|service|model] NAME

# Database operations
./dev.sh db [reset|migrate|seed|shell]
```

## Development Workflow

### Feature Development Process

1. **Issue Creation**
   - Create an issue in the issue tracker
   - Add appropriate labels and milestone
   - Assign to yourself or request assignment

2. **Branch Creation**
   - Create a feature branch from `main`:
     ```bash
     git checkout -b feature/issue-123-short-description
     ```

3. **Local Development**
   - Start the development environment: `./dev.sh start`
   - Implement the feature with tests
   - Use feature flags for incomplete features that need to be merged

4. **Code Quality Checks**
   - Run linting: `./dev.sh lint --fix`
   - Run tests: `./dev.sh test`
   - Ensure all tests pass and code meets quality standards

5. **Commit Changes**
   - Use conventional commit messages:
     ```
     feat: add user authentication
     fix: resolve issue with event processing
     docs: update API documentation
     ```
   - Keep commits focused and atomic

6. **Pull Request**
   - Push branch and create a pull request
   - Fill out the PR template
   - Request reviews from appropriate team members

7. **Code Review**
   - Address review comments
   - Update PR as needed
   - Ensure CI checks pass

8. **Merge**
   - Squash and merge to `main`
   - Delete the feature branch

### Working with Feature Flags

Feature flags allow you to merge incomplete features without affecting production:

```javascript
// Import feature flag manager
import featureFlags from 'src/devex/feature_flags/feature_flag_manager';

// Check if a feature is enabled
if (featureFlags.isEnabled('newFeature')) {
  // New feature code
} else {
  // Old implementation
}

// In React components, use the hook
import { useFeatureFlag } from 'src/devex/feature_flags/feature_flag_manager';

function MyComponent() {
  const isNewFeatureEnabled = useFeatureFlag('newFeature');
  
  return isNewFeatureEnabled ? <NewFeature /> : <OldFeature />;
}
```

## Code Quality Standards

### Linting and Formatting

The project uses ESLint and Prettier for code quality:

- ESLint enforces code quality rules
- Prettier ensures consistent formatting
- Pre-commit hooks automatically check code

### Code Organization

- Follow the directory structure outlined in the architecture documentation
- Keep files focused on a single responsibility
- Use meaningful file and directory names

### Documentation

- Document all public APIs with JSDoc comments
- Keep README files up-to-date
- Document complex algorithms and business logic
- Update architecture documentation for significant changes

## Testing Practices

### Test Types

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete user flows

### Testing Guidelines

- Write tests before or alongside code (TDD/BDD)
- Aim for high test coverage (>80%)
- Test edge cases and error conditions
- Use descriptive test names that explain the expected behavior

### Example Test

```javascript
describe('UserService', () => {
  it('should create a new user with valid data', async () => {
    // Arrange
    const userData = { username: 'testuser', email: 'test@example.com' };
    
    // Act
    const result = await userService.createUser(userData);
    
    // Assert
    expect(result).toHaveProperty('id');
    expect(result.username).toBe(userData.username);
    expect(result.email).toBe(userData.email);
  });
  
  it('should throw an error when creating a user with invalid data', async () => {
    // Arrange
    const invalidData = { username: '' };
    
    // Act & Assert
    await expect(userService.createUser(invalidData)).rejects.toThrow();
  });
});
```

## Pull Request Process

### PR Template

All PRs should follow the template, which includes:

- Description of changes
- Related issue(s)
- Type of change (bugfix, feature, etc.)
- Checklist of completed items
- Testing instructions

### Review Process

1. Automated checks must pass (CI/CD pipeline)
2. At least one approval from a team member
3. All review comments must be addressed
4. PR must be up-to-date with the target branch

### Merge Strategy

- Squash and merge for feature branches
- Preserve commit history for release branches

## Release Process

### Release Preparation

1. Create a release branch: `release/vX.Y.Z`
2. Update version numbers and CHANGELOG.md
3. Run final tests and quality checks
4. Create a release PR

### Release Execution

1. Merge release PR to `main`
2. Tag the release: `git tag vX.Y.Z`
3. Push the tag: `git push origin vX.Y.Z`
4. CI/CD pipeline will build and deploy the release

### Post-Release

1. Update documentation if needed
2. Notify team and stakeholders
3. Monitor for any issues

## Troubleshooting

### Common Issues

#### Docker Compose Issues

**Problem**: Services fail to start
**Solution**: Check logs with `docker-compose logs` and ensure ports are not in use

#### Database Connection Issues

**Problem**: Application cannot connect to database
**Solution**: Ensure database service is running and credentials are correct

#### Test Failures

**Problem**: Tests fail inconsistently
**Solution**: Check for race conditions or environment dependencies

### Getting Help

- Check the troubleshooting guide in the documentation
- Ask in the team chat channel
- Create an issue with the "help wanted" label

### Debugging Tools

- Use the browser developer tools for frontend issues
- Use the integrated debugger in your IDE
- Check logs with `./dev.sh logs`
- Use the debug mode feature flag for additional logging
