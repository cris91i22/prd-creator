---
description: Mandatory rules and best practices for documentation using Amiga TechDocs, the documentation-as-code platform based on Antora and AsciiDoc. Provides guidance for structure, content, and workflow to ensure consistency and quality in Amiga TechDocs projects.
author: AMIGA TechDocs Team
version: 1.0
tags: ["amiga-techdocs", "rules", "best-practices", "mandatory", "techdocs", "docs-as-code", "documentation", "asciidoc", "antora"]
globs: ["docs/**/*.adoc", "**/amiga-docs-playbook.yml", "docs/**/nav.adoc", "docs/modules/**/*", "**/antora.yml"]
applyTo: "docs/**/*.adoc,**/amiga-docs-playbook.yml,docs/**/nav.adoc,docs/modules/**/*,**/antora.yml"
---

# Documentation Rules for ATD Projects (Amiga Tech Docs)

This document establishes the guidelines and best practices for creating and maintaining documentation for projects using Amiga Tech Docs.

## 🚨 CRITICAL INSTRUCTIONS FOR AI LANGUAGE MODELS 🚨

### Core Behavioral Rules

✅ **MUST use ONLY AsciiDoc** - NO Markdown allowed in AMIGA TechDocs projects
✅ **MUST follow the mandatory project structure** defined by AMIGA TechDocs
✅ **MUST use Geppetto MCP** for searching AMIGA TechDocs documentation and best practices
✅ **ALWAYS update navigation files** when adding new pages to modules
✅ **MUST validate AsciiDoc syntax** and follow style guidelines below

❌ **ABSOLUTELY NEVER use Markdown** - AMIGA TechDocs uses ONLY AsciiDoc (.adoc files)
❌ **NEVER convert AsciiDoc to Markdown** - always maintain AsciiDoc format
❌ **NEVER suggest Markdown alternatives** - AsciiDoc is the ONLY supported format
❌ **NEVER modify project structure** without understanding AMIGA TechDocs architecture
❌ **NEVER ignore navigation updates** when adding new documentation pages
❌ **NEVER assume file locations** - always check the docs/ directory structure

### AI Verification Checklist

Before proceeding with AMIGA TechDocs tasks, verify:
1. ✅ Am I working with a docs/ directory containing AMIGA TechDocs structure?
2. ✅ Are there .adoc files in modules/*/pages/ directories?
3. ✅ Is there an amiga-docs-playbook.yml file present?
4. ✅ Will I use ONLY AsciiDoc syntax - NO Markdown allowed?
5. ✅ Do I need to update navigation files when adding new pages?
6. ✅ Should I consult Geppetto MCP for AMIGA TechDocs-specific guidance?
7. ✅ Am I absolutely certain to NEVER suggest or use Markdown in this project?

## Documentation as Code Principles

-   **AsciiDoc as format:** All documentation will be written using AsciiDoc syntax.
-   **Version control:** Documentation will be managed as code, using a version control system (Git).
-   **Separation of concerns:** Maintain a clear separation between content, configuration, and presentation.
-   **Automation:** Leverage automated processes for generating and publishing documentation.
-   **Standardization:** Follow the documentation structure and style guide defined below.

## Documentation Structure and Organization

AMIGA TechDocs follows a hierarchical structure: **Site → Component → Module → Pages**

### Mandatory Directory Structure

```
docs/
├── amiga-docs-playbook.yml          # Site configuration (Antora playbook)
├── package.json                     # Dependencies and scripts
├── antora.yml                       # Component descriptor
├── modules/                         # Documentation modules
│   ├── ROOT/                        # Root module (homepage)
│   │   ├── pages/
│   │   │   └── home.adoc           # Main entry point
│   │   ├── partials/
│   │   │   └── nav.adoc            # Navigation definition
│   │   └── images/                 # Module-specific images
│   ├── overview/                   # MANDATORY: Product overview
│   │   ├── pages/                  # AsciiDoc pages (.adoc files)
│   │   │   ├── about.adoc
│   │   │   └── index.adoc
│   │   ├── partials/               # Reusable content snippets
│   │   │   └── nav.adoc           # Navigation definition
│   │   └── images/                 # Module-specific images
│   ├── getting-started/            # MANDATORY: Quickstart section
│   │   ├── pages/
│   │   ├── partials/
│   │   │   └── nav.adoc
│   │   └── images/
│   ├── additional-information/     # MANDATORY: Live information
│   │   ├── pages/
│   │   ├── partials/
│   │   │   └── nav.adoc
│   │   └── images/
│   └── [custom-modules]/          # OPTIONAL: Additional modules
└── .github/workflows/              # GitHub Actions for publishing
```

Each documentation project should be modular. Each module **MUST** have a `nav.adoc` for navigation.

### Required modules

-   **Overview:** General description of the product. Include:
    - What the product is
    - Benefits and vision
    - Architecture overview
    - How to read the docs
    - Glossary

-   **Getting started:** First step for users. Include:
    - Basic concepts
    - Prerequisites
    - Quickstart
    - Next steps

-   **Additional information:** Dynamic meta-information. Include:
    - EOL policy
    - Release notes
    - Changelog
    - Migration guides
    - FAQs
    - Contact details

### Optional modules

Add as needed based on product scope (e.g., API reference, configuration, components).

Where applicable, structure them with:

-   Quickstart
-   Supported modes
-   Configuration (overview)
-   Usage (guides and examples)
-   API reference (dependencies, imports, configuration properties, classes, components, types, functions, endpoints)

### Project root module

-   **Homepage (`home.adoc`):** The `ROOT` module must contain a `home.adoc` page that serves as the main entry point to the documentation.

## Development Workflow

### Initial Setup

🔧 **Installation Commands**:
```bash
cd docs
npm install
```

🔧 **Development Server**:
```bash
npm run start
# Opens at http://localhost:8080
```

### Content Creation Workflow

1. **Create AsciiDoc file** in appropriate `modules/[module-name]/pages/` directory
2. **Update navigation** in corresponding `modules/[module-name]/partials/nav.adoc`
3. **Test locally** with `npm run start`
4. **Validate and publish** following deployment workflows

### Navigation Management

✅ **ALWAYS update nav.adoc** when adding new pages:

```asciidoc
* xref:overview:about.adoc[About]
* xref:overview:architecture.adoc[Architecture]
* xref:overview:new-page.adoc[New Page] // ← Add new entries like this
```

### Common Commands

```bash
# Install dependencies
npm install

# Start development server
npm run start

# Build for production (if available)
npm run build

# Check for linting issues (if configured)
npm run lint
```

## Style and Content Guides

Follow the style guide below and default to the Google developer documentation style guide if unspecified.

### General principles

-   **Separate content types:** Maintain a clear separation between actionable content (such as guides and examples) and reference documentation (including configuration properties, APIs, and specifications) that can be linked across different guides.
-   **Use the inverted pyramid:** Present the most important information first, followed by supporting details and background. Start sections and paragraphs with clear key messages or conclusions, then provide additional context or explanations.
-   **Design standalone pages:** Every page should make sense on its own. Start with a short intro, and include helpful links.
- **One idea per section:** Ensure each section addresses one clear concept to enhance readability and comprehension.
-   **No pre-announcements:** Do not document future or unavailable features.
-   **Ensure consistency:** Maintain consistency in terminology, format, and style throughout the documentation.

### Grammar and Language

-   **Language:** All documentation will be written in American English.
-   **Sentence structure:**
    -   Prefer short, direct sentences.
    -   Avoid filler words ("just," "please," "simply").
    -   If a sentence has many commas, split it.
-   **Tense:** Use present simple over future.
-   **Active voice:** Prefer active voice over passive voice.
-   **Personal pronouns:**
    -   Avoid using "you" and "we" in instructions. Write impersonally.
    -   If necessary, prefer "you" over "we."
-   **Conditional clauses:** Place conditional clauses before instructions.
-   **Contractions:** Avoid using contractions (use "it is" instead of "it's").
-   **Precise verbs:** Avoid phrasal verbs and delexical verbs (have, take, make, give, go, do). Use more precise single-word verbs (e.g., "configure" instead of "set up").

### Formatting and Punctuation
-   **Titles and headings:** Use sentence case (only the first word capitalized, unless they are proper nouns).
-   **Proper nouns and trademarks:** Maintain original capitalization (e.g., OpenShift, GitHub, AMIGA).
-   **UI elements:** Mark user interface elements (buttons, menus, etc.) in **bold**.
-   **Emphasis:**
    -   To emphasize, use introductory phrases, headings, or bulleted lists.
    -   Avoid using italics, highlighting, ALL CAPS, underlining, or bold just for emphasis.
    -   If a paragraph is preceded by text followed by a colon, put that introductory text in **bold**, including the colon.
-   **Serial comma (Oxford comma):** In a series of three or more items, use a comma before the final "and" or "or."
-   **Lists:**
    -   Use numbered lists for sequences of steps.
    -   Use bulleted lists for most other lists.
-   **Identifiable data:** Do not use real or identifiable data (names, usernames, tokens, emails) in examples. Use fictitious data.
-   **Code snippets:** Remember to include necessary imports. When possible, define them in a separate file and include them so they can be easily tested.
-   **Admonitions:** Do not place one admonition immediately after another, as it disrupts the reading flow. Each admonition should convey a single idea and, for warnings or cautions, be positioned before the related instructions.

### AsciiDoc Syntax Examples

✅ **Document structure**:
```asciidoc
= Page Title
:page-description: Brief description of the page content
:page-keywords: keyword1, keyword2, keyword3

== Section Heading

Content paragraph with proper formatting.

=== Subsection

More detailed content.
```

✅ **Code blocks with syntax highlighting**:
```asciidoc
[source,javascript]
----
const example = {
  property: "value",
  method: function() {
    console.log("Hello World");
  }
};
----
```

✅ **Cross-references using xref**:
```asciidoc
xref:module-name:page-name.adoc[Link Text]
xref:overview:about.adoc[About This Project]
```

✅ **External links**:
```asciidoc
https://example.com[External Link]
link:https://example.com[External Link with Link Macro]
```

✅ **Image inclusion**:
```asciidoc
image::image-name.png[Alt text, width=900]
image::diagrams/architecture.svg[Architecture Diagram, 800]
```

✅ **Tables**:
```asciidoc
[cols="1,2,1"]
|===
|Column 1 |Column 2 |Column 3

|Row 1, Col 1
|Row 1, Col 2
|Row 1, Col 3
|===
```

## AMIGA TechDocs Extensions

AMIGA TechDocs provides custom AsciiDoc extensions to enhance documentation with interactive and visual components.

### Available Extensions

- **Accordion**: Collapsible content sections
- **Tabs**: Tabbed content organization  
- **Grid**: Layout components for better content organization
- **Hero**: Landing page headers with call-to-action buttons
- **Timeline**: Process and chronological visualization
- **Emoji**: Enhanced visual communication
- **Figma**: Design integration and embedding
- **Tooltip**: Interactive help and definitions

### Extension Usage Examples

✅ **Accordion for collapsible content**:
```asciidoc
[.accordion]
[.accordion-item]
[.accordion-header]
====== Configuration Options
[.accordion-content]
Detailed configuration information that can be expanded or collapsed.

[.accordion-item]
[.accordion-header]
====== Advanced Settings
[.accordion-content]
Advanced configuration details.
```

✅ **Tabs for organized content**:
```asciidoc
[.tabs]
[.tab]
===== JavaScript
[source,javascript]
----
const config = {
  environment: "production"
};
----

[.tab]
===== Python
[source,python]
----
config = {
    "environment": "production"
}
----
```

✅ **Grid for layout organization**:
```asciidoc
[.grid]
[.grid-item]
== Feature 1
Description of the first feature.

[.grid-item]
== Feature 2
Description of the second feature.
```

### Images and Diagrams

-   **Image format:** Prefer PNG for its transparency support and lossless compression.
-   **Attribution:** Cite the source of all images to avoid copyright issues.
-   **Alternative text (alt text):** Provide descriptive alternative text for all images.
-   **Alignment:** Center images and their captions (default behavior).
-   **Consistent width:** Use a consistent width for images (recommended: 900px). They will be scaled automatically if necessary.
-   **Privacy:** Do not use images containing information about identifiable individuals.
-   **Text images:** Do not use images to display only text, code examples, or terminal output. Write the text directly.
-   **Diagrams:**
    -   Various tools can be used, but it is recommended to follow Amiga Tech Docs suggestions (e.g., Kroki-compatible tools).
    -   Include the diagram's source file in the repository for future updates.
-   **Screenshots:**
    -   Minimum legible width: 600px (400px for vertical orientation). Maximum recommended: 1200px.
    -   Crop to show only relevant information while maintaining context.
    -   To highlight elements: use rectangular shapes without background (border >=1px) or circular bubbles with text (font >=12px). Recommended color: green (#17CFB0) or light peach (#FAF0E6) if contrast is insufficient.

## Integration and Tools

### Using Geppetto MCP

🔍 **ALWAYS use Geppetto MCP** for:
- Searching AMIGA TechDocs documentation and best practices
- Finding extension usage examples
- Understanding configuration options
- Troubleshooting setup issues

**Example search queries**:
```bash
"AMIGA TechDocs AsciiDoc syntax examples"
"AMIGA TechDocs extension accordion usage"
"AMIGA TechDocs publishing Azure configuration"
"AMIGA TechDocs navigation management best practices"
```

### Publishing and Deployment

🚀 **Publishing platforms**:
- **Microsoft Azure** (recommended)
- GitHub Pages (candidate for deprecation)

🚀 **Deployment workflows**:
- PR validation
- Develop branch builds
- Release processes with documentation tags: `docs/<VERSION>`
- Version control integration

### Troubleshooting Common Issues

🔧 **Local development issues**:
- Ensure `npm install` completed successfully
- Check node.js version compatibility
- Verify AsciiDoc syntax with local build
- Update navigation files when adding pages

🔧 **Content issues**:
- Validate cross-references work correctly
- Check image paths and accessibility
- Ensure proper module organization
- Test extension syntax

## Additional References

### Documentation Resources
📚 **Official AMIGA TechDocs**: https://amiga-techdocs.docs.inditex.dev/tech-docs/latest/home.html
📚 **GitHub repository**: https://github.com/inditex/lib-amigatechdocs
📚 **AsciiDoc documentation**: https://docs.asciidoctor.org/asciidoc/latest/
📚 **Antora documentation**: https://docs.antora.org/antora/latest/
📚 **Google Developer Documentation Style Guide**: https://developers.google.com/style

### Support Channels
🆘 **For assistance**:
- **Questions and ideas**: GitHub Discussions
- **Bugs and incidents**: Community repository issues
- **Framework support**: AMIGA Framework Team

### Key NPM Packages
- `@amigatechdocs/core`: Shell package with devtools and AsciiDoc extensions
- `@amigatechdocs/tools`: CLI tools and development utilities
- `@amigatechdocs/uibundle`: UI bundle with Sewing Design System theme
- `@amigatechdocs/publish-azure-blob-storage`: Azure publishing tools
- `@amigatechdocs/publish-github-pages`: GitHub Pages publishing tools

This comprehensive set of rules will help maintain high-quality, consistent, and user-friendly documentation for all AMIGA TechDocs projects while ensuring AI assistance follows best practices and project standards.
