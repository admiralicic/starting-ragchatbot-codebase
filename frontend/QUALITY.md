# Frontend Code Quality Guide

This document describes the code quality tools and workflows for the frontend codebase.

## Tools

### Prettier
Prettier is an opinionated code formatter that ensures consistent code style across the project.

**Configuration:** `.prettierrc.json`
- Print width: 100 characters
- Indentation: 2 spaces
- Single quotes for strings
- Semicolons required
- Trailing commas in ES5-compatible positions

### ESLint
ESLint is a static code analysis tool for identifying problematic patterns in JavaScript code.

**Configuration:** `.eslintrc.json`
- ECMAScript 2021+ features
- Browser environment
- Enforces consistent indentation (2 spaces)
- Requires single quotes and semicolons
- Warns on unused variables
- Requires `const` for variables that don't change
- Prohibits `var` in favor of `let` and `const`

## Setup

Install the required dependencies:

```bash
cd frontend
npm install
```

## Usage

### Quick Scripts

Two convenience scripts are provided for easy quality checks:

#### Check Quality (No Changes)
```bash
./check-quality.sh
```
This will:
1. Install dependencies if needed
2. Check code formatting with Prettier
3. Lint JavaScript with ESLint

Use this in CI/CD pipelines or before committing.

#### Fix Quality Issues (Auto-Fix)
```bash
./fix-quality.sh
```
This will:
1. Install dependencies if needed
2. Auto-format all code with Prettier
3. Auto-fix linting issues with ESLint

Use this during development to automatically fix issues.

### NPM Scripts

You can also use the npm scripts directly:

```bash
# Format all files
npm run format

# Check formatting without changes
npm run format:check

# Lint JavaScript files
npm run lint

# Lint and auto-fix issues
npm run lint:fix

# Run all quality checks
npm run quality

# Run all quality fixes
npm run quality:fix
```

## Workflow

### During Development

1. Write your code
2. Run `./fix-quality.sh` or `npm run quality:fix` to auto-fix issues
3. Review the changes
4. Commit your code

### Before Committing

Run quality checks to ensure code meets standards:

```bash
./check-quality.sh
```

If issues are found, fix them with:

```bash
./fix-quality.sh
```

### In CI/CD

Add this to your CI pipeline:

```bash
cd frontend
npm install
npm run quality
```

## Files

- `.prettierrc.json` - Prettier configuration
- `.prettierignore` - Files to exclude from formatting
- `.eslintrc.json` - ESLint configuration
- `.eslintignore` - Files to exclude from linting
- `package.json` - NPM scripts and dependencies
- `check-quality.sh` - Script to check quality without changes
- `fix-quality.sh` - Script to auto-fix quality issues

## Best Practices

1. **Run quality checks before committing** - Use `./check-quality.sh` to ensure your code meets standards
2. **Auto-fix when possible** - Use `./fix-quality.sh` to automatically resolve formatting and linting issues
3. **Review auto-fixes** - Always review changes made by auto-fix tools before committing
4. **Configure your editor** - Set up your editor to run Prettier on save and show ESLint errors inline
5. **Don't disable rules** - Avoid using `eslint-disable` comments unless absolutely necessary

## Editor Integration

### VS Code

Install these extensions:
- [Prettier - Code formatter](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)
- [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)

Add to your `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "eslint.validate": ["javascript"],
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### WebStorm / IntelliJ

1. Enable Prettier: Settings → Languages & Frameworks → JavaScript → Prettier
2. Check "On save" and "On Reformat Code"
3. Enable ESLint: Settings → Languages & Frameworks → JavaScript → Code Quality Tools → ESLint
4. Select "Automatic ESLint configuration"

## Troubleshooting

### Dependencies not found
```bash
cd frontend
npm install
```

### Conflicting formatting
If Prettier and ESLint conflict, Prettier takes precedence for formatting. ESLint focuses on code quality.

### Script permission denied
Make scripts executable:
```bash
chmod +x check-quality.sh fix-quality.sh
```
