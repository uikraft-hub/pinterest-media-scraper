# Usage Guide

A comprehensive guide on how to use the Repository Blueprint template to create professional, well-structured repositories for your projects.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Step-by-Step Setup](#step-by-step-setup)
- [Customization Guide](#customization-guide)
- [Making It Your Default Template](#making-it-your-default-template)
- [Repository Structure](#repository-structure)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Repository Blueprint is a comprehensive template designed to jumpstart your development projects with professional structure, documentation, and community standards compliance. It includes:

- **Professional README.md** with consistent styling and improved layout
- **GitHub Templates** for issues and pull requests
- **Community Standards** including Code of Conduct, Contributing guidelines, and Security policy
- **Asset Management** with organized folder structure for images and screenshots
- **License and Documentation** following open-source best practices

## Quick Start

### Method 1: Use as GitHub Template

1. **Navigate to the repository**: Go to [ukr-projects/repo-blueprint](https://github.com/ukr-projects/repo-blueprint)
2. **Click "Use this template"**: Look for the green button at the top of the repository
3. **Create new repository**: Fill in your repository name and description
4. **Choose visibility**: Select public or private based on your needs
5. **Create repository**: Click "Create repository from template"

### Method 2: Clone and Modify

```bash
# Clone the repository
git clone https://github.com/ukr-projects/repo-blueprint.git your-project-name

# Navigate to the project directory
cd your-project-name

# Remove the original git history
rm -rf .git

# Initialize a new git repository
git init

# Add your remote origin
git remote add origin https://github.com/yourusername/your-project-name.git
```

## Step-by-Step Setup

### 1. Initial Setup

After cloning or using the template, follow these steps:

```bash
# Navigate to your project directory
cd your-project-name

# Install dependencies (if applicable to your project type)
# This step varies based on your project (Node.js, Python, etc.)
```

### 2. Customize Project Information

Update the following files with your project-specific information:

#### README.md (in docs folder)
- Replace project name and description
- Update installation instructions
- Modify usage examples
- Update contact information
- Change repository URLs

#### Package Files
Update relevant package files based on your project type:
- `package.json` (Node.js projects)
- `requirements.txt` (Python projects)
- `Cargo.toml` (Rust projects)
- `go.mod` (Go projects)

### 3. Update Documentation

#### docs/CONTRIBUTING.md
- Modify contribution guidelines specific to your project
- Update development setup instructions
- Adjust coding standards and conventions

#### docs/CODE_OF_CONDUCT.md
- Review and customize if needed
- Update contact information for reporting issues

#### docs/SECURITY.md
- Update security policy for your project
- Modify vulnerability reporting process
- Add project-specific security considerations

### 4. Configure GitHub Templates

#### .github/ISSUE_TEMPLATE/
- **bug_report.md**: Customize bug report template
- **feature_request.md**: Modify feature request template
- Add additional templates if needed

#### .github/PULL_REQUEST_TEMPLATE.md
- Update PR checklist items
- Modify review criteria
- Add project-specific requirements

### 5. Update Assets

#### assets/ folder
- Replace `repo-blueprint-banner.jpg` with your project banner
- Replace `repo-blueprint-logo.png` with your project logo
- Add project-specific screenshots to `screenshots/` folder
- Update image references in documentation

## Customization Guide

### Project Branding

1. **Logo and Banner**:
   ```bash
   # Replace with your project assets
   cp your-logo.png assets/repo-blueprint-logo.png
   cp your-banner.jpg assets/repo-blueprint-banner.jpg
   ```

2. **Color Scheme**: Update HTML styling in README.md to match your brand colors

3. **Project Information**: Update all instances of:
   - Project name
   - Repository URLs
   - Contact information
   - License details (if different from MIT)

### Technology-Specific Customization

#### For Node.js Projects
```bash
# Add package.json
npm init -y

# Update with project dependencies
npm install your-dependencies
```

#### For Python Projects
```bash
# Create requirements.txt
pip freeze > requirements.txt

# Add setup.py or setup.cfg if needed
```

#### For Other Languages
- Add appropriate configuration files
- Update build scripts
- Modify CI/CD workflows if needed

## Making It Your Default Template

### Option 1: GitHub Template Repository

1. **Fork the repository** to your account
2. **Customize** it with your preferred defaults
3. **Mark as template** in repository settings
4. **Use for new projects** via "Use this template" button

### Option 2: Local Template System

Create a local template system for offline use:

```bash
# Create a templates directory
mkdir ~/project-templates
cd ~/project-templates

# Clone the blueprint
git clone https://github.com/ukr-projects/repo-blueprint.git

# Create a setup script
cat > setup-new-project.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

PROJECT_NAME=$1
cp -r repo-blueprint "$PROJECT_NAME"
cd "$PROJECT_NAME"
rm -rf .git
git init
echo "Project $PROJECT_NAME created successfully!"
EOF

chmod +x setup-new-project.sh
```

Usage:
```bash
# Create new project from template
~/project-templates/setup-new-project.sh my-new-project
```

### Option 3: GitHub CLI Template

Use GitHub CLI for quick template usage:

```bash
# Install GitHub CLI if not already installed
# Then create repositories from template
gh repo create my-new-project --template ukr-projects/repo-blueprint
```

## Repository Structure

```
your-project/
├── .github/                    # GitHub-specific files
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   │   ├── bug_report.md      # Bug report template
│   │   └── feature_request.md # Feature request template
│   └── PULL_REQUEST_TEMPLATE.md # PR template
├── assets/                     # Project assets
│   ├── logo.png               # Project logo
│   ├── banner.jpg             # Project banner
│   └── screenshots/           # Project screenshots
├── docs/                       # Documentation
│   ├── CODE_OF_CONDUCT.md     # Code of conduct
│   ├── CONTRIBUTING.md        # Contribution guidelines
│   ├── README.md              # Main documentation
│   └── SECURITY.md            # Security policy
├── src/                        # Source code (add as needed)
├── tests/                      # Test files (add as needed)
├── LICENSE                     # License file
└── README.md                   # Root README (can link to docs/README.md)
```

## Best Practices

### Documentation
- Keep README.md updated with current project status
- Use clear, concise language in all documentation
- Include code examples and usage instructions
- Maintain changelog for version tracking

### GitHub Templates
- Regularly review and update issue templates
- Ensure PR template reflects current workflow
- Test templates with dummy issues/PRs

### Assets Management
- Use high-quality images for better presentation
- Optimize image sizes for faster loading
- Maintain consistent branding across all assets

### Version Control
- Use semantic versioning for releases
- Write descriptive commit messages
- Maintain clean git history

### Community Standards
- Respond promptly to issues and PRs
- Follow your own contributing guidelines
- Keep security policy updated

## Troubleshooting

### Common Issues

#### Template Files Not Showing
**Problem**: GitHub templates not appearing in issue/PR creation
**Solution**: Ensure files are in correct paths with proper `.md` extension

#### Images Not Loading
**Problem**: Images in README not displaying
**Solution**: Check image paths and ensure images are committed to repository

#### License Conflicts
**Problem**: License doesn't match project requirements
**Solution**: Replace LICENSE file with appropriate license for your project

#### Documentation Out of Sync
**Problem**: Multiple README files causing confusion
**Solution**: Choose either root README.md or docs/README.md as primary, link to the other

### 📞 Support

- **📧 Email**: [ujjwalkrai@gmail.com](mailto:ujjwalkrai@gmail.com)
- **🐛 Issues**: [Repository Issues](https://github.com/ukr-projects/repo-blueprint/issues)
- **🔓 Security**: [Repository Security](https://github.com/ukr-projects/repo-blueprint/security)
- **⛏ Pull Requests**: [Repository Pull Requests](https://github.com/ukr-projects/repo-blueprint/pulls)
- **📖 Documentation**: [Repository Documentation](https://github.com/ukr-projects/repo-blueprint/tree/main/docs)

### Contributing Back

If you improve the template, consider contributing back:

1. Fork the original repository
2. Make your improvements
3. Submit a pull request with clear description
4. Follow the contribution guidelines

---

**Made with ❤️ for the developer community**

*This template helps create professional, well-structured repositories that follow community standards and best practices.*
