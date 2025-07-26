# Contributing to repo-blueprint

Thank you for your interest in contributing to repo-blueprint! We welcome contributions from everyone and appreciate your help in making this boilerplate template better for the development community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [ujjwalkrai@gmail.com](mailto:ujjwalkrai@gmail.com).

## Getting Started

### Prerequisites

Before you begin, ensure you have the following:
- A GitHub account
- Git installed on your local machine
- Basic knowledge of Markdown for documentation
- Understanding of GitHub templates and repository structure

### First Time Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/repo-blueprint.git
   cd repo-blueprint
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/ukr-projects/repo-blueprint.git
   ```
4. Review the project structure:
   ```
repo-blueprint/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── assets/
│   ├── repo-blueprint-banner.jpg
│   ├── repo-blueprint-logo.png
│   └── screenshots/
│       └── community-standard.jpg
├── docs/
│   ├── CODE_OF_CONDUCT.md
│   ├── CONTRIBUTING.md
│   ├── README.md
│   └── SECURITY.md
└── LICENSE
   ```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Template Improvements**: Enhance existing templates and documentation
- **New Templates**: Add new GitHub templates or documentation templates
- **Documentation**: Improve or add to our documentation and guides
- **Bug Reports**: Help us identify and fix issues in templates
- **Feature Requests**: Suggest new templates or improvements
- **Visual Assets**: Contribute to logos, banners, or other visual elements
- **Best Practices**: Help establish and document repository best practices

### Before You Start

1. Check existing [issues](https://github.com/ukr-projects/repo-blueprint/issues) and [pull requests](https://github.com/ukr-projects/repo-blueprint/pulls) to avoid duplicates
2. For major changes or new templates, please open an issue first to discuss your proposed changes
3. Make sure your contribution aligns with the project's goal of providing a professional, reusable repository template

## Development Setup

### Local Development

1. Create a new branch for your feature or improvement:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   # or
   git checkout -b docs/documentation-update
   ```

2. Make your changes following our [coding standards](#coding-standards)

3. Test your changes:
   - Verify Markdown formatting renders correctly
   - Check that all internal links work
   - Ensure templates follow GitHub standards
   - Test any new documentation for clarity

4. Preview your changes:
   - Use a Markdown previewer for documentation changes
   - Validate template formatting on GitHub
   - Check visual assets display correctly

## Coding Standards

### General Guidelines

- Write clear, readable, and well-structured documentation
- Follow existing formatting patterns and styles
- Use consistent terminology throughout documentation
- Ensure all templates are professional and reusable
- Add comments or explanations for complex sections

### Documentation Standards

#### Markdown Guidelines
- Use consistent heading hierarchy (# ## ### ####)
- Include table of contents for longer documents
- Use code blocks with appropriate language highlighting
- Include proper links and references
- Follow standard Markdown formatting practices

#### Template Standards
- Follow GitHub's template guidelines
- Include clear instructions and examples
- Use placeholder text that's easy to understand and replace
- Ensure templates are comprehensive yet concise
- Test templates with actual use cases

### File Organization

- Keep related files in appropriate directories
- Use clear, descriptive file names
- Maintain consistent directory structure
- Include README files in subdirectories when helpful

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.

### Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: A new template or feature
- `fix`: A bug fix in templates or documentation
- `docs`: Documentation only changes
- `style`: Changes that improve formatting or presentation
- `refactor`: Restructuring existing content without changing functionality
- `chore`: Maintenance tasks and updates

### Examples

```
feat(templates): add issue template for enhancement requests

fix(readme): correct broken links in documentation section

docs: update contributing guidelines with template standards

style(assets): optimize banner image for better loading

refactor(structure): reorganize docs folder for better navigation
```

## Pull Request Process

### Before Submitting

1. Ensure your branch is up to date with the main branch:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Review your changes thoroughly
3. Update documentation if necessary
4. Ensure all links and references work correctly

### Submitting Your Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request from your fork to the main repository

3. Fill out the pull request template completely

4. Link any related issues using keywords (e.g., "Closes #123")

### Pull Request Template

When creating a pull request, please include:

- **Description**: Clear description of what changes you made
- **Motivation**: Why are these changes needed?
- **Type of Change**: Bug fix, new feature, documentation, etc.
- **Testing**: How did you test your changes?
- **Screenshots**: If applicable, add screenshots of visual changes
- **Breaking Changes**: List any breaking changes
- **Checklist**: Complete the provided checklist

### Review Process

1. All pull requests require at least one review from a maintainer
2. Address any feedback or requested changes promptly
3. Once approved, a maintainer will merge your pull request
4. Your contribution will be included in the next release

## Issue Guidelines

### Before Creating an Issue

1. Search existing issues to avoid duplicates
2. Check if the issue might be related to your specific use case
3. Gather relevant information (screenshots, examples, etc.)

### Bug Reports

When reporting a bug, please include:

- **Bug Description**: Clear and concise description
- **Steps to Reproduce**: How to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Template/File Affected**: Which template or file has the issue
- **Additional Context**: Screenshots, examples, etc.

### Feature Requests

When requesting a feature, please include:

- **Feature Description**: Clear description of the proposed feature
- **Use Case**: Why is this feature needed?
- **Proposed Solution**: Your ideas for implementation
- **Examples**: Examples from other projects if applicable
- **Additional Context**: Any other relevant information

### Template Requests

When requesting a new template:

- **Template Type**: What kind of template (issue, PR, documentation, etc.)
- **Purpose**: What problem does this template solve?
- **Content Structure**: Outline of what the template should include
- **Examples**: Examples from other successful projects
- **Target Audience**: Who would use this template?

## Community

### Getting Help

If you need help or have questions, don't hesitate to:
- Open an issue with the "question" label
- Email us at [ujjwalkrai@gmail.com](mailto:ujjwalkrai@gmail.com)
- Check existing documentation and templates for examples

### Recognition

We appreciate all contributions and maintain a contributors list to recognize everyone who has helped improve this project. All contributors will be acknowledged in our documentation.

### License

By contributing to this project, you agree that your contributions will be licensed under the MIT License, the same license as the project. See [LICENSE](../LICENSE) for details.

---

## Quick Reference

### Common Commands

```bash
# Setup
git clone https://github.com/your-username/repo-blueprint.git
cd repo-blueprint
git remote add upstream https://github.com/ukr-projects/repo-blueprint.git

# Development
git checkout -b feature/new-template
# Make your changes
git add .
git commit -m "feat: add new template for X"
git push origin feature/new-template
```

### 📞 Support

- **📧 Email**: [ujjwalkrai@gmail.com](mailto:ujjwalkrai@gmail.com)
- **🐛 Issues**: [Repository Issues](https://github.com/ukr-projects/repo-blueprint/issues)
- **🔓 Security**: [Repository Security](https://github.com/ukr-projects/repo-blueprint/security)
- **⛏ Pull Requests**: [Repository Pull Requests](https://github.com/ukr-projects/repo-blueprint/pulls)
- **📖 Documentation**: [Repository Documentation](https://github.com/ukr-projects/repo-blueprint/docs)

### Need Help?

If you're new to contributing or need assistance:
- Review our existing templates for examples
- Check the project structure and follow existing patterns
- Don't hesitate to ask questions in issues or via email
- Start with small improvements to get familiar with the project

Thank you for contributing to repo-blueprint! Together, we're making it easier for developers to create professional, well-structured repositories. 🎉