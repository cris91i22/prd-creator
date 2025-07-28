# Figma Guidelines for DS Sewing MCP

This guide outlines the essential requirements and best practices for creating Figma files that are compatible with DS Sewing MCP. Following these guidelines ensures proper integration with the Sewing Design System and Amiga Framework Web Components.

## Component Implementation Requirements

### Using Component Instances

* All Sewing Design System components *must be implemented as instances*
* Never use detached components or direct element creation
* Always use the official Sewing DS component library

### Naming Conventions

* Components implementing Sewing DS must follow the naming pattern: `SDS <NameOfComponent>`
* The `<NameOfComponent>` *must match* or closely align with Amiga Framework Web component names
* Examples:
  * `SDS Button` for button components
  * `SDS TextField` for text input fields
  * `SDS SelectField` for dropdown selects

### Property Alignment

* Component properties *must exactly match* Amiga Framework Web Components
  * Property names must be identical
  * Property values must correspond to available options in Amiga Framework
* This ensures accurate translation from design to implementation
* Example:

```txt
SDS Button properties:
- variant: "primary" | "secondary" | "tertiary"
- size: "small" | "medium" | "large"
```

## Layout Structure Guidelines

[!IMPORTANT]
All layouts *must be built using Frames* in Figma. Frames are the foundation for proper layout structure and ensure correct implementation of the Sewing Design System grid components.

### Grid System Implementation

#### Basic Grid Components

* Use `SDS Grid` Frames for container layouts
* Implement `SDS Grid Col` Frames for column definitions
* Apply `SDS Grid Row` Frames for row organization
* Ensure proper Frame nesting for layout hierarchy

#### Grid Usage Example

```text
SDS Grid
├── SDS Grid Row
│   ├── SDS Grid Col (content)
│   ├── SDS Grid Col (content)
└── SDS Row
    ├── SDS Grid Col (content)
    └── SDS Grid Col (content)
```

### Form Layouts

#### Form-specific Components

* Use `SDS Grid Form` Frame for form containers
* Apply `SDS Grid Form Row` Frame for form row organization
* Implement `SDS Grid Form Col` Frame for form fields
* Maintain consistent Frame hierarchy for form structures

#### Form Structure Example

```text
SDS Grid Form
├── SDS Grid Form Row
│   ├── SDS Grid From Col (form field)
│   └── SDS Grid Form Col (form field)
└── SDS Grid From Row
    └── SDS Grid Form Col (submit button)
```

## Best Practices and Restrictions

### Do's

* ✓ Use component instances from the Sewing Design System
* ✓ Follow naming conventions strictly
* ✓ Maintain proper grid structure
* ✓ Align properties with Amiga Framework specifications

### Don'ts

* ⨯ Don't work with detached components
* ⨯ Don't add custom CSS to Sewing DS Instances
* ⨯ Don't modify existing Sewing DS Components
* ⨯ Don't create custom variations of Design System components

## Component Integration Examples

### Basic Component Example

```text
SDS Button
├── Properties
│   ├── variant: "primary"
│   ├── size: "medium"
│   └── disabled: false
└── Text: "Submit"
```

### Form Layout Example

```text
SDS Grid Form
├── SDS Grid Form Row
│   ├── SDS Grid Form Col
│   │   └── SDS TextField
│   │       ├── label: "First Name"
│   │       └── required: true
│   └── SDS Grid Form Col 
│       └── SDS TextField
│           ├── label: "Last Name"
│           └── required: true
└── SDS Grid Form Row
    └── SDS Grid Form Col
        └── SDS Button
            └── text: "Save"
```

## Tips for Success

* Review component documentation in Amiga Framework Web before implementation
* Maintain consistent naming across your design files
* Keep layouts organized using the proper grid structure
