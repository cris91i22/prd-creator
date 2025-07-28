---
description: Meta-rule for extracting information from AMIGA TechDocs websites and generating precise, verified clinerules for specific tools and technologies.
author: Cline Meta-Rule System
version: 1.0.0
tags: ["meta-rule", "documentation-extraction", "clinerule-generation", "amiga-techdocs", "verification"]
globs: ["**/*"]
---

# AMIGA TechDocs Documentation Extractor Meta-Rule

## Objective

This meta-rule guides the systematic extraction of information from AMIGA TechDocs websites to generate accurate, verified clinerules for specific tools and technologies. **NO HALLUCINATIONS ALLOWED** - only documented, verifiable information.

**⚠️ FOUNDATION REQUIREMENT**: This meta-rule builds upon and extends the foundational principles established in `rules/meta/writing-effective-clinerules.md`. All generated clinerules **MUST** comply with the core principles, structure requirements, and best practices defined in that base document. This extractor adds AMIGA TechDocs-specific verification and extraction processes on top of those foundational requirements.

## 🚨 CRITICAL ANTI-HALLUCINATION INSTRUCTIONS 🚨

### Core Verification Rules

✅ **MUST verify every command, feature, or method exists in source documentation**
✅ **MUST provide source URL/section for every extracted piece of information**
✅ **MUST quote directly from documentation - NO paraphrasing without verification**
✅ **MUST stop extraction if information cannot be verified**
✅ **MUST mark unverified content as [UNVERIFIED - SKIP]**

❌ **NEVER assume features exist without explicit documentation**
❌ **NEVER extrapolate or infer capabilities not explicitly stated**
❌ **NEVER use examples from other tools without verification**
❌ **NEVER generate content without source attribution**

## Step 1: Source Collection and Validation

### 1.1 Mandatory Source Request

**ALWAYS start by asking:**
```
I need to create a clinerule for [TOOL_NAME]. Please provide:
1. GitHub repository URL with the documentation (preferred)
2. Official AMIGA TechDocs URL for this tool
3. Any specific documentation sections you want emphasized

I will prioritize direct documentation access over generic searches.
```

### 1.2 Source Verification Protocol

**For GitHub repositories:**
- Verify README.md exists and contains setup instructions
- Check for docs/ directory or wiki
- Identify configuration files and examples

**For AMIGA TechDocs sites:**
- Verify site accessibility
- Identify key navigation sections
- Locate Overview, Getting Started, Development and any other first level sections

**Fallback to Geppetto MCP only if:**
- Direct access fails
- Specific targeted searches needed
- Documentation gaps require filling

## Step 2: Systematic Information Extraction

### 2.1 Required Information Categories

**Extract ONLY if explicitly documented:**

**A. Basic Tool Information**
- Tool name and exact purpose (quote from docs)
- Installation commands (copy exactly)
- System requirements (if specified)

**B. Core Operations**
- Primary commands (exact syntax)
- Configuration file locations and names
- Directory structure requirements

**C. Critical Warnings and Notes**
- Warning boxes or callouts
- Breaking changes or version notes
- Required dependencies

**D. Integration Information**
- AMIGA framework integration steps
- Related AMIGA tools mentioned
- Inditex-specific configurations

### 2.2 Extraction Verification Checklist

Before recording any information, verify:
- [ ] Information appears in official documentation
- [ ] Commands/methods are explicitly documented
- [ ] Source section/URL is noted
- [ ] No assumptions or inferences made

**Evidence Format:**
```
EXTRACTED: [exact quote or command]
SOURCE: [URL#section or file:line]
VERIFIED: [date]
```

## Step 3: Clinerule Generation Process

**📋 FOUNDATION COMPLIANCE**: All generated clinerules MUST follow the structure, formatting, and best practices defined in `rules/meta/writing-effective-clinerules.md`. This includes proper frontmatter, clear objectives, structured content, and appropriate rule types.

### 3.1 Frontmatter Template (Based on Foundation Guide)

**Reference: `rules/meta/writing-effective-clinerules.md` Section 3 - Frontmatter for Metadata**

```yaml
---
description: [Tool purpose from official docs - clear and concise per foundation guide]
author: Generated from [SOURCE_URL]
version: 1.0.0
tags: ["[tool-name]", "amiga", "[additional-verified-tags]"]
globs: ["[verified-file-patterns]"] # File patterns where rule is relevant
source_documentation: "[PRIMARY_SOURCE_URL]"
extraction_date: "[DATE]"
---
```

### 3.2 Rule Structure Compliance

**Reference: `rules/meta/writing-effective-clinerules.md` Section 4 - Types of ClineRules**

**MUST determine and follow appropriate rule type:**
- **Informational/Documentation Rules**: For comprehensive tool information
- **Process/Workflow Rules**: For step-by-step procedures
- **Behavioral/Instructional Rules**: For AI guidance and constraints
- **Meta-Rules**: For rule management processes

### 3.3 Required Sections (Only if Information Available)

**Reference: `rules/meta/writing-effective-clinerules.md` Section 2 - Core Principles**

**If documented, include with proper structure:**
- **Clear Objective** (mandatory per foundation guide)
- Tool overview (quoted from docs)
- Installation steps (exact commands)
- Core usage patterns (verified examples)
- Configuration requirements (exact filenames/structure)
- Integration steps (if specified)
- Troubleshooting (if provided)

**If NOT documented, mark as:**
```
## [Section Name]
[NOT DOCUMENTED - Information not available in source documentation]
```

### 3.4 AI Behavioral Rules Section

**Reference: `rules/meta/writing-effective-clinerules.md` Section 5 - Language and Formatting for AI Guidance**

**Generate based on verified information only, following foundation formatting:**
```
## 🚨 CRITICAL INSTRUCTIONS FOR AI LANGUAGE MODELS 🚨

✅ **MUST [specific verified requirement]** # Use MUST for absolute requirements
✅ **SHOULD [verified recommendation]** # Use SHOULD for strong recommendations

❌ **NEVER [specific documented constraint]** # Use NEVER for absolute prohibitions
❌ **SHOULD NOT [verified discouragement]** # Use SHOULD NOT for strong discouragement
```

### 3.5 Foundation Guide Compliance Checklist

**Before finalizing any generated clinerule, verify compliance with `rules/meta/writing-effective-clinerules.md`:**

- [ ] **Clear Objective**: Rule has well-defined purpose stated clearly
- [ ] **Structured Content**: Uses proper Markdown headings, lists, code blocks
- [ ] **Clarity and Precision**: Clear, unambiguous language throughout
- [ ] **Modularity**: Focuses on specific tool/workflow area
- [ ] **Proper Frontmatter**: Includes all required metadata fields
- [ ] **Appropriate Rule Type**: Follows correct structure for rule category
- [ ] **Effective Formatting**: Uses bold, italics, emojis appropriately
- [ ] **Concrete Examples**: Includes specific, verified code/commands
- [ ] **Verification Steps**: Includes checklists or validation procedures

## Step 4: Quality Assurance and Verification

### 4.1 Foundation Guide Compliance Verification

**Reference: `rules/meta/writing-effective-clinerules.md` Section 8 - Testing Your Rule**

**MUST verify compliance with foundation principles:**
- [ ] **Human Readability**: Clear to another person per foundation guide
- [ ] **AI Interpretation**: Provides specific guidance without ambiguities
- [ ] **Practical Application**: Can be manually tested/validated
- [ ] **Self-Review**: Adheres to all foundation guide principles

### 4.2 Pre-Generation Checklist

**Technical Verification:**
- [ ] All commands tested against documentation
- [ ] All file paths verified from source
- [ ] All configuration options documented in source
- [ ] No inferred or assumed capabilities included
- [ ] Source attribution complete

**Foundation Guide Compliance:**
- [ ] Follows appropriate rule type structure (Section 4 of foundation guide)
- [ ] Uses proper language and formatting (Section 5 of foundation guide)
- [ ] Includes clear objective and structured content (Section 2 of foundation guide)
- [ ] Frontmatter follows metadata requirements (Section 3 of foundation guide)

### 4.3 Content Verification Protocol

**For each element in the clinerule:**
1. Cross-reference with source documentation
2. Verify exact syntax/naming
3. Confirm current validity (check for deprecation notices)
4. Mark verification status
5. **Validate against foundation guide formatting requirements**

### 4.4 Final Validation Steps

**Before presenting clinerule:**
- Confirm all examples are from documentation
- Verify no hallucinated commands/features
- Check that all source URLs are accessible
- Validate file glob patterns against actual project structure
- **Ensure full compliance with `rules/meta/writing-effective-clinerules.md` requirements**
- **Verify rule follows appropriate type structure from foundation guide**
- **Confirm formatting matches foundation guide conventions**

## Step 5: Documentation Gap Handling

### 5.1 When Information Is Missing

**If critical information is not documented:**
```
## [Missing Section]
⚠️ **DOCUMENTATION GAP**: [Specific information] not found in official documentation.
SOURCE CHECKED: [URL]
STATUS: Requires manual verification or additional sources.
```

### 5.2 Incomplete Documentation Response

**If source documentation is insufficient:**
1. Document what IS available
2. Clearly mark gaps
3. Suggest where additional information might be found
4. **DO NOT** fill gaps with assumptions

## Step 6: Source Attribution Requirements

### 6.1 Mandatory Source Documentation

**Every clinerule MUST include:**
```
## Sources and Verification

**Primary Documentation**: [URL]
**Extraction Date**: [DATE]
**Verification Status**: All commands and examples verified against source
**Last Source Update**: [If available from documentation]

### Verified Elements
- [Element 1]: Source [URL#section]
- [Element 2]: Source [URL#section]
```

### 6.2 Update Protocol

**Include in clinerule:**
```
## Maintenance Notes

This clinerule was generated from [SOURCE] on [DATE].
For updates:
1. Re-verify against current documentation
2. Update extraction date
3. Note any breaking changes
4. Maintain source attribution
```

## Emergency Stops and Escalation

### When to STOP Extraction

**STOP immediately if:**
- Source documentation is inaccessible
- Commands cannot be verified
- Information contradicts between sources
- Too many documentation gaps exist

**Escalation Protocol:**
1. Document specific issues encountered
2. List verified vs. unverified information
3. Recommend manual verification steps
4. Suggest alternative documentation sources

## Verification Commands for Generated Clinerules

**Include verification section in every generated clinerule:**
```
## Self-Verification Checklist

Before using this clinerule, verify:
- [ ] Source documentation is still accessible
- [ ] Commands are current (check for updates)
- [ ] File paths exist in your project
- [ ] Dependencies are properly installed
- [ ] Integration steps match your setup

**Last Verified**: [DATE]
**Source**: [URL]
```

## Foundation Reference and Compliance

**📚 BASE DOCUMENT**: `rules/meta/writing-effective-clinerules.md`

This meta-rule is a specialized extension of the foundational clinerule writing guide. **ALL generated clinerules MUST comply with the base document requirements.**

### Key Foundation Guide Sections Referenced:
- **Section 2**: Core Principles for All ClineRules
- **Section 3**: Frontmatter for Metadata  
- **Section 4**: Types of ClineRules and Their Structure
- **Section 5**: Language and Formatting for AI Guidance
- **Section 8**: Testing Your Rule

### Hierarchical Relationship:
1. **`rules/meta/writing-effective-clinerules.md`** = Foundation (MUST follow)
2. **`amiga-techdocs-extractor-rules.md`** = Specialized extension (adds AMIGA-specific verification)
3. **Generated clinerules** = Final output (complies with both foundation + AMIGA requirements)

This meta-rule ensures that generated clinerules are accurate, verifiable, and maintainable while preventing hallucination and ensuring source transparency, all while maintaining full compliance with established clinerule writing standards.
