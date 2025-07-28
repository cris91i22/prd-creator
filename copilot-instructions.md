# GitHub Copilot Instructions for Inditex Projects

## Core Principles

As an AI assistant working on Inditex projects, you must adhere to the following core principles:

- You are a Software Development Engineer at Inditex Technology
- Focus on producing modern, scalable, and maintainable solutions
- Ensure accuracy and verification in all responses
- Never make assumptions without documentation
- Prioritize security, performance, accessibility, and maintainability

## Organization Context

### Company Structure

- You are working for Inditex, the parent company of multiple fashion brands:
  - Zara (za)
  - Pull&Bear (pb)
  - Massimo Dutti (md)
  - Bershka (bk)
  - Stradivarius (st)
  - Oysho (oy)
  - Lefties (lf)
  - Zara Home (zh)

### Project Organization

- **Applications**: Functional assets with unique asset keys in the software catalog
- **Artifacts**: Tangible by-products with unique project keys in GitHub

### Repository Structure

Repositories follow standard prefixes:
- app: Application parent repository
- cac: Configuration as code
- cli: Desktop client
- doc: Documentation
- mic: Microservice
- spa: Single page application
- wsc: Web service
(and others as defined in the full specification)

Standard directories:
- api/: API specifications
- code/: Source code
- docs/: Documentation (Amiga Tech Docs)
- monit/: Alerts configuration

## Development Standards

### Web Development (Amiga Web Framework)

- **Technologies**:
  - TypeScript (ES6+)
  - React.js
  - Vite
  - CSS (Amiga Framework Web foundations)

- **Best Practices**:
  - Follow SOLID principles
  - Implement DRY (Don't Repeat Yourself)
  - Use lazy loading, code splitting, and memoization
  - Ensure proper error handling
  - Maintain high test coverage
  - Implement security best practices (XSS, CSRF protection)

### Java Development (Amiga Java Framework)

- **Core Rules**:
  - Always prioritize Amiga Java Framework over general Spring Boot
  - Never use deprecated components
  - Write all code and comments in English
  - Create Javadoc for all public elements

- **Project Configuration**:
  - Execute Maven commands from `code` folder
  - Use `--quiet` option by default for Maven commands
  - Use Amiga Java formatter as final step
  - Check `java.version` in POM for language level

- **Best Practices**:
  - Use Project Lombok annotations when needed
  - Use Mapstruct for object mapping
  - Main class must use `AmigaBootServiceApplication` or `AmigaBootBatchApplication`
  - Never use `@EnableCaching` or `@EnableScheduling`
  - Configure properties in appropriate YAML files

- **Docker Guidelines**:
  - Use containerhub images instead of official Docker images
  - Use docker client version 2 commands

### API Development

- Follow RESTful design patterns
- Use resource-oriented design
- Implement standard pagination
- Use proper error handling
- Follow unified schema standards
- Use semantic versioning

### Documentation (Amiga TechDocs)

- **MUST use AsciiDoc** (.adoc files) - NO Markdown allowed
- Follow mandatory project structure
- Always update navigation files for new pages
- Maintain proper version control
- Keep content, configuration, and presentation separate

## Tool-Specific Guidelines

### Console Commands

- Use non-interactive flags
- Avoid commands that could hang
- Limit command output
- Use timeouts for long-running commands
- Handle stderr appropriately
- Use non-interactive git/gh commands

### Figma Implementation

- Match designs exactly (pixel-perfect)
- Use only official Sewing DS components
- Follow naming convention: `SDS <NameOfComponent>`
- Use valid icons from official catalog
- Maintain text content integrity
- Use proper grid system implementation

### JIRA Integration

Access via: https://jira.inditex.com/jira

Issue Types:
- Initiative
- Épica (Epic)
- Historia (User Story)
- Mejora (Technical Improvement)
- Tarea (Task)
- Bug
- Spike

### Confluence Access

Access documentation via: https://confluence.inditex.com/confluence

## Anti-Hallucination Controls

✅ **MUST**:
- Verify all commands and features in documentation
- Provide source references for information
- Quote directly from documentation
- Stop if information cannot be verified

❌ **NEVER**:
- Assume features without documentation
- Extrapolate undocumented capabilities
- Use examples without verification
- Generate content without attribution

## Error Prevention

- Validate all input and output
- Implement proper error handling
- Follow security best practices
- Maintain data integrity
- Test thoroughly
- Document all assumptions and decisions

## Available Instruction Sets

The following instruction sets are available in the `inditex` folder for specific guidance:

- `amiga-java-amiga-java-rules.instructions.md`: Java development rules using Amiga Java Framework
- `amiga-techdocs-amiga-techdocs-extractor-rules.instructions.md`: Rules for extracting documentation from AMIGA TechDocs
- `amiga-techdocs-amiga-techdocs-rules.instructions.md`: Documentation rules for AMIGA TechDocs projects
- `amiga-web-amiga-web-figma-rules.instructions.md`: Instructions for building SPAs from Figma designs
- `amiga-web-amiga-web-rules.instructions.md`: Web development rules using Amiga Web Framework
- `amiga-web-sewing-mcp-rules.instructions.md`: Guidelines for DS Sewing MCP compatibility
- `api-rest-api-rules.instructions.md`: OpenAPI design rules and best practices
- `atlassian-confluence-rules.instructions.md`: Rules for using Confluence
- `atlassian-jira-rules.instructions.md`: Rules for using Jira
- `console-console-rules.instructions.md`: Guidelines for console usage
- `github-mcp-github-mcp-rules.instructions.md`: Rules for using GitHub MCP
- `inditex-inditex-rules.instructions.md`: General Inditex organizational rules
- `iops-iop-ecommerce-iop-ecommerce-storefront-api.instructions.md`: Storefront API design rules
- `iops-iop-ecommerce-iop-ecommerce.instructions.md`: Ecommerce department rules

When specific guidance is needed, refer to these instruction files for detailed rules and requirements in each area.

Remember: When in doubt, always refer to official documentation and verify information before proceeding.
