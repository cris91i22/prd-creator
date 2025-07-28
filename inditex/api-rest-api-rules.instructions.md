# OpenAPI Design Rules

## Table of Contents

- [Introduction](#introduction)
- [General API Design Principles](#general-api-design-principles)
- [API Structure and Organization](#api-structure-and-organization)
- [Path Design](#path-design)
- [HTTP Methods and Status Codes](#http-methods-and-status-codes)
- [Schema and Property Naming](#schema-and-property-naming)
- [Data Validation and Constraints](#data-validation-and-constraints)
- [Documentation and Examples](#documentation-and-examples)
- [Pagination](#pagination)
- [Error Handling](#error-handling)
- [Security and Authentication](#security-and-authentication)

## Introduction

This document provides guidelines for generating OpenAPI specifications that follow company best practices. These rules are designed to help LLM generate high-quality, consistent, and secure API specifications that align with industry standards and company guidelines.

## General API Design Principles

🔑 **Core Principles**

- Follow RESTful design patterns and principles
- Use consistent naming conventions across all API elements
- Design APIs that are secure, consistent, and easy to use
- Follow the principle of least privilege for security
- Use semantic versioning for API versions

## API Structure and Organization

### File Organization

✅ **Best Practice**: Split large API specifications into multiple files for better maintainability

```text
openapi-rest.yml (main file) + separate files for each resource
```

❌ **Avoid**: One large monolithic OpenAPI file

### File Structure

✅ **Recommended Structure**:

```text
/apis/
  /books/
    books.yml
  /users/
    users.yml
  /libraries/
    libraries.yml
  openapi-rest.yml (main file)
```

### Imports

✅ **Import direclty used refs only**:

❌ **Avoid importing nested imports if not used in the file directly, components are inherited if the path is imported**:

### File Naming

✅ **Consistent Naming**:

```text
books.yml, users.yml, libraries.yml
```

❌ **Avoid**:

```text
BooksAPI.yml, users_api.yml, Library-API.yml
```

### Component Organization

❌ **Avoid naming conflicts between domain concepts and OpenAPI components in folders**

✅ **Organize schemas by domain**:

```text
/apis/
  /domain1/
    schemas.yml  # Contains schemas specific to domain1
  /domain2/
    schemas.yml  # Contains schemas specific to domain2
  /shared/
    schemas.yml  # Contains only common/shared schemas
```

❌ **Avoid keeping all schemas in a single file**:

```text
/apis/
  /shared/
    schemas.yml  # Contains ALL schemas from all domains
```

### Component References

✅ **Use $ref for Components**:

```yaml
paths:
  /books/{bookId}:
    $ref: 'books/books.yml#/paths/~1books~1{bookId}'
```

### Path Organization

✅ **Group Related Paths with Comments**:

```yaml
paths:
  # Books
  /books:
    $ref: 'books/books.yml#/paths/~1books'

  # Users
  /users:
    $ref: 'users/users.yml#/paths/~1users'
```

### Resource Tagging

✅ **Use Tags for Categorization**:

```yaml
tags:
  - name: books
    description: "Operations related to books"
  - name: users
    description: "Operations related to users"
```

✅ **Apply Tags Consistently**:

```yaml
paths:
  /books:
    get:
      tags:
        - books
```

## Path Design

### Case Conventions

✅ **Use lowercase for all path segments**

```text
/api/books
```

❌ **Avoid**

```text
/API/Books
```

✅ **Use kebab-case for multi-word path segments**

```text
/api/book-reviews
```

❌ **Avoid underscores**

```text
/api/book_reviews
```

✅ **Use camelCase for path parameters**

```text
/api/books/{bookId}
```

❌ **Avoid**

```text
/api/books/{book_id}
```

✅ **Use camelCase for query parameters**

```text
/api/books?sortOrder=asc
```

❌ **Avoid**

```text
/api/books?sort_order=asc
```

### Resource Naming

✅ **Use plural nouns for collection resources**

```text
/api/libraries
```

❌ **Avoid singular for collections**

```text
/api/library
```

### Resource Hierarchy

✅ **Limit nesting to 3 sub-resources maximum**

```text
/api/libraries/{libraryId}/books/{bookId}
```

❌ **Avoid deep nesting**

```text
/api/libraries/{libraryId}/books/{bookId}/pages/{pageId}/annotations/{annotationId}
```

✅ **Use consistent parameter names across related resources**

```yaml
# Use libraryId consistently
/libraries/{libraryId}
/libraries/{libraryId}/books

# Use userId consistently
/users/{userId}/borrowings
/users/{userId}/preferences
```

✅ **Group related operations under common paths**

```yaml
/books:
  # List books
  get: {}
  # Create book
  post: {}

/books/{bookId}:
  # Get book
  get: {}
  # Update book
  put: {}
  # Delete book
  delete: {}
```

## HTTP Methods and Status Codes

### HTTP Methods

✅ **Use standard HTTP methods appropriately**

- `GET`: Retrieve resources
- `POST`: Create resources or trigger operations
- `PUT`: Replace resources
- `PATCH`: Partially update resources
- `DELETE`: Remove resources

### HTTP Status Codes

✅ **Include appropriate HTTP status codes for each operation**:

| Operation | Required Status Codes |
|-----------|----------------------|
| GET (collection) | 200, 400, 401, 500 |
| GET (resource) | 200, 400, 401, 404, 500 |
| POST (collection) | 201, 400, 401, 403, 500 |
| POST (resource) | 201, 400, 401, 403, 409, 500 |
| POST (controller) | 200, 400, 401, 403, 404, 500 |
| PUT | 200, 400, 401, 403, 500 |
| DELETE | 400, 401, 403, 404, 409, 500 |
| PATCH | 204, 400, 401, 403, 404, 500 |

✅ **Always include 409 (Conflict) status code for DELETE operations**

```yaml
delete:
  responses:
    '204':
      description: Resource deleted successfully
    '409':
      $ref: '../shared/responses.yml#/responses/Conflict'
```

✅ **Use appropriate status codes for the HTTP method**:

- `200 OK`: Can be used with any method
- `201 Created`: Should only be used with POST and PUT
- `204 No Content`: Can be used with any method
- `400 Bad Request`: Can be used with any method
- `401 Unauthorized`: Can be used with any method
- `403 Forbidden`: Can be used with any method
- `404 Not Found`: Can be used with any method
- `409 Conflict`: Should only be used with POST, PUT, DELETE, PATCH

## Schema and Property Naming

### Schema Case Conventions

✅ **Use camelCase for all property names**

```json
{ "bookTitle": "The Great Gatsby" }
```

❌ **Avoid PascalCase or snake_case**

```json
{ "BookTitle": "The Great Gatsby" }
{ "book_title": "The Great Gatsby" }
```

### Schema Naming

✅ **Use clear, descriptive schema names**

```text
"Book"
```

❌ **Don't suffix schema names with "dto", "DTO", or "Dto"**

```text
"BookDto"
```

### Property Naming Conventions

✅ **For date properties, use the "date" format and consider using "Date" as a suffix**

```yaml
publishDate:
  type: string
  format: date
  example: "1925-04-10"
```

✅ **For datetime properties, use the "date-time" format and consider using "DateTime" as a suffix, do not add maxLength constraints**

```yaml
borrowedDateTime:
  type: string
  format: date-time
  example: "2023-01-01T12:00:00Z"
```

✅ **For boolean properties, consider using "is" as a prefix**

```yaml
isAvailable:
  type: boolean
  example: true
```

## Data Validation and Constraints

### String Constraints

✅ **Always include maxLength for string properties that not have a specific format like uuid, date or date-time**

```yaml
bookTitle:
  type: string
  maxLength: 100
  example: "The Great Gatsby"
```

```yaml
borrowedDateTime:
  type: string
  format: date-time
  example: "2025-06-27T07:20:50.52Z"
```

### Numeric Constraints

✅ **Include minimum and maximum values for numeric properties**

```yaml
pageCount:
  type: integer
  minimum: 1
  maximum: 10000
  example: 235
```

✅ **Always define both minimum and maximum for numeric properties**

```yaml
# Required
limit:
  type: integer
  minimum: 1
  maximum: 100
  example: 20

# Avoid
limit:
  type: integer
  example: 20
```

### Array Constraints

✅ **Include maxItems for array properties**

```yaml
genres:
  type: array
  maxItems: 5
  items:
    type: string
  example: ["Fiction", "Classic"]
```

✅ **Always specify maxItems for array schemas**

```yaml
# Required
data:
  type: array
  maxItems: 100
  items:
    $ref: '#/components/schemas/Book'

# Avoid
data:
  type: array
  items:
    $ref: '#/components/schemas/Book'
```

### Object Constraints

✅ **Explicitly define additionalProperties for object properties**

```yaml
publisher:
  type: object
  additionalProperties: false
  properties:
    name:
      type: string
    location:
      type: string
```

✅ **Always define additionalProperties for schema objects**

```yaml
# Required
schema:
  type: object
  additionalProperties: false
  properties:
    name:
      type: string

# Avoid
schema:
  type: object
  properties:
    name:
      type: string
```

### Request Bodies

✅ **Always define schemas for request bodies**

```yaml
requestBody:
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/Book'
```

## Documentation and Examples

### API Information

✅ **Include comprehensive API descriptions**:

- Purpose of the API
- Target audience
- Key functionality
- Special requirements or considerations

✅ **Include contact information**

```yaml
info:
  contact:
    name: "API Support"
    email: "api@example.com"
    url: "https://example.com/support"
```

✅ **Include external documentation links**

```yaml
externalDocs:
  description: "Find out more about our API"
  url: "https://example.com/docs"
```

### Operation Documentation

✅ **Include a summary for all operations**

```yaml
paths:
  /books:
    get:
      summary: "Get all books in the library"
      description: "Returns a paginated list of all books in the library system"
```

### Examples

✅ **Include examples for all parameters**

```yaml
parameters:
  - name: bookId
    in: path
    required: true
    schema:
      type: string
    example: "123e4567-e89b-12d3-a456-426614174000"
```

✅ **Include examples for all properties in schemas**

```yaml
components:
  schemas:
    Book:
      properties:
        id:
          type: string
          format: uuid
          example: "123e4567-e89b-12d3-a456-426614174000"
```

✅ **Always include examples for schema references**

```yaml
schema:
  $ref: './schemas.yml#/schemas/Component'
  example: {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Button"
  }
```

✅ **Always include examples for array items**

```yaml
items:
  $ref: './schemas.yml#/schemas/Component'
  example: {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Button"
  }
```

✅ **Always include examples for pagination properties**

```yaml
limit:
  type: integer
  example: 20
offset:
  type: integer
  example: 0
total:
  type: integer
  example: 100
```

### Server Documentation

✅ **Use server variables for flexible deployment**

```yaml
servers:
  - url: https://{host}:{port}/{basePath}
    description: "API server"
    variables:
      host:
        default: 'api.example.com'
      port:
        default: '443'
      basePath:
        default: 'v1'
```

✅ **Include descriptions for server configurations**

```yaml
servers:
  - url: https://api.example.com/v1
    description: "Production API server"
  - url: https://staging-api.example.com/v1
    description: "Staging API server for testing"
```

## Pagination

### Response Structure

✅ **For collection endpoints, return an object with a data array property**

```yaml
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                $ref: '#/components/schemas/Book'
```

### Pagination Properties

✅ **Include limit, offset, and links properties for pagination**

```yaml
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                $ref: '#/components/schemas/Book'
            links:
              type: object
              properties:
                self:
                  type: string
                  format: uri
                  example: "https://api.example.com/books?limit=10&offset=0"
                prev:
                  type: string
                  format: uri
                  example: "https://api.example.com/books?limit=10&offset=0"
                next:
                  type: string
                  format: uri
                  example: "https://api.example.com/books?limit=10&offset=10"
                first:
                  type: string
                  format: uri
                  example: "https://api.example.com/books?limit=10&offset=0"
            limit:
              type: integer
              example: 10
            offset:
              type: integer
              example: 0
```

## Error Handling

### Error Response Format

✅ **Define errors following the Problem Details RFC9457 specification**

```yaml
responses:
  400:
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 400
            title:
              type: string
              example: "Bad Request"
            detail:
              type: string
              example: "The request contains invalid parameters"
```

### Required Error Properties

✅ **Error responses should include at minimum**:

- `status`: HTTP status code as an integer
- `title`: A short, human-readable summary of the problem
- `detail`: A human-readable explanation specific to this occurrence of the problem

### Shared Error Definitions

✅ **Use shared error definitions for consistent error responses**

```yaml
responses:
  '400':
    description: Bad Request
    content:
      application/json:
        schema:
          $ref: "https://inditex.jfrog.io/artifactory/apischemas-public/apidsg/rest/default-error-utils/0.1.1/schemas/errors.yml#/BadRequest400"
```

✅ **Available shared error definitions**:

- `BadRequest400`: Use for invalid request format or data
- `Unauthorized401`: Use for authentication issues
- `Forbidden403`: Use for authorization issues
- `NotFound404`: Use when a resource is not found
- `Conflict409`: Use for conflicts (e.g., when a resource cannot be deleted)
- `InternalServerError500`: Use for general system errors
- `ServiceUnavailable503`: Use for specific server errors
- `GatewayTimeout504`: Use for timeout errors
- `UnexpectedStatusCode`: Use for general system errors

✅ **Example of using shared error definitions**:

```yaml
paths:
  /books/{bookId}:
    get:
      responses:
        '200':
          description: Successfully retrieved book
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Book'
        '400':
          $ref: '../shared/responses.yml#/responses/BadRequest'
        '401':
          $ref: '../shared/responses.yml#/responses/Unauthorized'
        '404':
          $ref: '../shared/responses.yml#/responses/NotFound'
        '500':
          $ref: '../shared/responses.yml#/responses/InternalServerError'
```

✅ **Define shared responses in a responses.yml file**:

```yaml
# shared/responses.yml
responses:
  BadRequest:
    description: Bad Request
    content:
      application/json:
        schema:
          $ref: "https://inditex.jfrog.io/artifactory/apischemas-public/apidsg/rest/default-error-utils/0.1.1/schemas/errors.yml#/BadRequest400"
  Unauthorized:
    description: Unauthorized
    content:
      application/json:
        schema:
          $ref: "https://inditex.jfrog.io/artifactory/apischemas-public/apidsg/rest/default-error-utils/0.1.1/schemas/errors.yml#/Unauthorized401"
  Forbidden:
    description: Forbidden
    content:
      application/json:
        schema:
          $ref: "https://inditex.jfrog.io/artifactory/apischemas-public/apidsg/rest/default-error-utils/0.1.1/schemas/errors.yml#/Forbidden403"
  NotFound:
    description: Not Found
    content:
      application/json:
        schema:
          $ref: "https://inditex.jfrog.io/artifactory/apischemas-public/apidsg/rest/default-error-utils/0.1.1/schemas/errors.yml#/NotFound404"
  Conflict:
    description: Conflict
    content:
      application/json:
        schema:
          $ref: "https://inditex.jfrog.io/artifactory/apischemas-public/apidsg/rest/default-error-utils/0.1.1/schemas/errors.yml#/Conflict409"
  InternalServerError:
    description: Internal Server Error
    content:
      application/json:
        schema:
          $ref: "https://inditex.jfrog.io/artifactory/apischemas-public/apidsg/rest/default-error-utils/0.1.1/schemas/errors.yml#/InternalServerError500"
```

## Security and Authentication

### HTTPS

✅ **Use HTTPS for all server URLs**

```yaml
servers:
  - url: https://api.example.com
```

### Security Schemes

✅ **Use only allowed authentication methods**:

- Bearer
- ApiKey
- Basic
- OAuth2
- OpenId
- CookieAuth

❌ **Avoid**:

- OAuth 1.0
- Implicit grant flow in OAuth2
- Resource owner password flow in OAuth2

✅ **Define multiple authentication methods when appropriate**

```yaml
components:
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

✅ **Always place security schemes under components.securitySchemes**

```yaml
# Correct
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer

# Incorrect
securitySchemes:
  BearerAuth:
    type: http
    scheme: bearer
```

✅ **Ensure security values in the security section match defined security schemes**

```yaml
# Security schemes definition
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-KEY

# Security usage - must match defined schemes
security:
  - BearerAuth: []
  - ApiKeyAuth: []
```

✅ **Use descriptive names for security schemes**

```yaml
components:
  securitySchemes:
    LibraryApiKey:
      type: apiKey
      in: header
      name: X-LIBRARY-API-KEY
```

✅ **Include descriptions for security schemes**

```yaml
components:
  securitySchemes:
    LibraryOAuth2:
      type: oauth2
      description: "OAuth 2.0 authentication for library API access"
      flows:
        authorizationCode:
          authorizationUrl: https://library-api.example.com/oauth/authorize
          tokenUrl: https://library-api.example.com/oauth/token
          scopes:
            read:books: Read access to book information
            write:books: Write access to book information
            read:users: Read access to user information
```

### Security Requirements

✅ **Define security requirements at the global level**

```yaml
security:
  - BearerAuth: []
```
