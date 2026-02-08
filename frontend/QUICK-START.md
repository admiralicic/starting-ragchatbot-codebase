# Quick Start: Frontend Code Quality

## 🚀 First Time Setup

```bash
cd frontend
npm install
```

## ✨ Daily Usage

### Before committing code
```bash
./check-quality.sh
```

### Fix formatting and linting issues
```bash
./fix-quality.sh
```

## 📝 NPM Scripts

```bash
npm run format        # Format code with Prettier
npm run lint          # Check code with ESLint
npm run quality:fix   # Fix all issues automatically
```

## 📚 Full Documentation

See [QUALITY.md](./QUALITY.md) for complete documentation including:
- Tool descriptions and configuration
- Editor integration guides
- Best practices
- Troubleshooting

## ❓ Common Issues

**Permission denied when running scripts?**
```bash
chmod +x check-quality.sh fix-quality.sh
```

**Dependencies not found?**
```bash
npm install
```

**Formatting conflicts?**
Run `./fix-quality.sh` to auto-fix most issues.
