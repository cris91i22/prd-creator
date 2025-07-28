# Storefront API Design Rules

## Table of Contents

- [Introduction](#introduction)
- [General API Design Principles](#general-api-design-principles)
- [Naming Conventions](#naming-conventions)
- [API Structure and Organization](#api-structure-and-organization)
- [HTTP Methods and Status Codes](#http-methods-and-status-codes)
- [Data Validation and Constraints](#data-validation-and-constraints)
- [Documentation and Examples](#documentation-and-examples)
- [Pagination](#pagination)
- [Error Handling](#error-handling)
- [Unified Schemas](#unified-schemas)
- [Resource-Oriented Design](#resource-oriented-design)
- [Examples of Well-Designed Paths](#examples-of-well-designed-paths)

## Introduction

This document provides guidelines for designing and implementing APIs following Storefront API best practices. These rules are designed to help create high-quality, consistent, and secure API specifications that align with industry standards and company guidelines, ensuring a cohesive user experience across all Storefront services.

## API Design Quickstart Checklist

Use this checklist to quickly validate your API design before implementation:

- [ ] **Resource Oriented**: Resources are named as plural nouns with no verbs in URLs
- [ ] **URL Pattern**: URLs follow standard structure: `/api/storefront/{version}/stores/{storeId}/{domain-entity}/...`
- [ ] **Parameter Conventions**: Path parameters use camelCase; multi-word path segments use kebab-case
- [ ] **HTTP Methods**: Operations use appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE)
- [ ] **Status Codes**: All required status codes are defined for each operation
- [ ] **Pagination**: Collection endpoints implement standard pagination with limit/offset
- [ ] **Error Handling**: Standard error responses are defined using unified error schema
- [ ] **Documentation**: All operations include summary, description, and examples
- [ ] **Constraints**: All properties specify appropriate constraints (maxLength, min/max values, maxItems)
- [ ] **Schema Naming**: Schema properties use camelCase; no "Dto" suffixes in schema names
- [ ] **Unified Schemas**: Common data structures use the appropriate unified schemas
- [ ] **State Changes**: State changes use PATCH to update state properties, not special action endpoints
- [ ] **Complex Operations**: Complex operations are modeled as resources, not as actions
- [ ] **Examples**: JSON examples are provided for all operations

## General API Design Principles

🔑 **Core Principles**

- Follow RESTful design patterns and principles
- Design APIs that are secure, consistent, and easy to use
- Follow the principle of least privilege for security
- Use semantic versioning for API versions
- **Always prioritize resource-oriented design over action/verb-based endpoints**
- **Leverage unified schemas for standard data structures**

## Naming Conventions

### URL & Path Conventions

✅ **DO: Use lowercase for all path segments**
```
/api/storefront/1/stores/{storeId}/products
```

❌ **DON'T: Use uppercase or mixed case in paths**
```
/API/storefront/1/Stores/{StoreId}/Products
```

✅ **DO: Use kebab-case for multi-word path segments**
```
/api/storefront/1/stores/{storeId}/physical-stores
```

❌ **DON'T: Use underscores or camelCase for path segments**
```
/api/storefront/1/stores/{storeId}/physical_stores
/api/storefront/1/stores/{storeId}/physicalStores
```

✅ **DO: Use camelCase for query and path parameters**
```
/api/storefront/1/stores/{storeId}/products/{productId}?sortOrder=asc
```

❌ **DON'T: Use kebab-case or snake_case for parameters**
```
/api/storefront/1/stores/{storeId}/products/{product-id}?sort-order=asc
/api/storefront/1/stores/{storeId}/products/{product_id}?sort_order=asc
```

### Resource Naming

✅ **DO: Use plural nouns for collection resources**
```
/api/storefront/1/stores/{storeId}/products
```

❌ **DON'T: Use singular nouns for collections**
```
/api/storefront/1/stores/{storeId}/product
```

✅ **DO: Use consistent parameter names across related resources**
```
# Use storeId consistently
/api/storefront/1/stores/{storeId}/products
/api/storefront/1/stores/{storeId}/user/wishlists

# Use consistent path structure
/api/storefront/1/stores/{storeId}/products/{productId}
/api/storefront/1/stores/{storeId}/orders/{orderId}
```

❌ **DON'T: Mix parameter naming conventions**
```
/api/storefront/1/stores/{storeId}/products
/api/storefront/1/stores/{store_number}/orders

/api/storefront/1/stores/{storeId}/products/{productId}
/api/storefront/1/stores/{storeId}/orders/{order}
```

### Schema & Property Naming

✅ **DO: Use camelCase for all property names**
```json
{ "productName": "Slim Fit Jeans" }
```

❌ **DON'T: Use PascalCase or snake_case for properties**
```json
{ "ProductName": "Slim Fit Jeans" }
{ "product_name": "Slim Fit Jeans" }
```

✅ **DO: Use descriptive schema names without "Dto" suffix**
```
"Product" not "ProductDto"
```

❌ **DON'T: Add suffixes like DTO, Entity, or Model to schema names**
```
"ProductDto", "ProductEntity", "ProductModel"
```

### Special Naming Patterns

✅ **Date and Time Properties**
- Use suffix `Date` for date without time: `publishDate`
- Use suffix `DateTime` for date with time: `createdDateTime`
- Use ISO 8601 format (UTC timezone)

✅ **Boolean Properties**
- Use "is" prefix for boolean properties: `isAvailable`

✅ **Identifier Properties**
- Use plain `id` for primary identifiers, not entity-prefixed IDs
- Fields with pattern *[entity]Id* represent references to external entities

✅ **Monetary Values**
- Properties representing monetary values must end with suffix `...Amount`: `totalAmount`
- Use the unified Money schema for monetary values

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
  /domain1/
    schemas.yml
  /domain2/
    schemas.yml
  /shared/
    schemas.yml  # Contains only common/shared schemas
  openapi-rest.yml (main file)
```

### Component References

✅ **Use $ref for Components**:

```yaml
paths:
  /api/storefront/1/stores/{storeId}/products/{productId}:
    $ref: 'products/products.yml#/paths/~1api~1storefront~11~1stores~1{storeId}~1products~1{productId}'
```

✅ **Reference Unified Schemas**:

```yaml
parameters:
  - $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/params/4.0.0/schemas/path.yml#/storeId'
```

### Resource Tagging

✅ **Use Tags for Categorization**:

```yaml
tags:
  - name: products
    description: "Operations related to products"
  - name: users
    description: "Operations related to users"
  - name: orders
    description: "Operations related to order management"
```

✅ **Apply Tags Consistently**:

```yaml
paths:
  /api/storefront/1/stores/{storeId}/products:
    get:
      tags:
        - products
```

## Path Design



## Common Parameters

### User Identity
✅ **DO: Infer userId from the OAuth authorization token**
```
GET /api/storefront/1/stores/{storeId}/user/wishlists
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJr...
```

❌ **DON'T: Include userId as a path parameter**
```
GET /api/storefront/1/stores/{storeId}/users/{userId}/wishlists
```

### Store Identifier
✅ **DO: Include storeId as a path parameter in all API endpoints**
```
/api/storefront/1/stores/{storeId}/products
```

### Language
✅ **DO: Use the language query parameter for content localization**
```
GET /api/storefront/1/stores/{storeId}/products?language=en-US
```

- Language follows the BCP-47 standard in language-country format (e.g., `en-US`, `es-ES`)
- This is a query parameter, not a header, to facilitate URL-based caching

## Resource Hierarchy

✅ **Limit nesting to 3 sub-resources maximum**

```text
/api/storefront/1/stores/{storeId}/wishlists/{wishlistId}/items
```

❌ **Avoid deep nesting**

```text
/api/storefront/1/stores/{storeId}/users/{userId}/wishlists/{wishlistId}/items/{itemId}/attributes
```

✅ **Use consistent parameter names across related resources**

```yaml
# Use storeId consistently
/api/storefront/1/stores/{storeId}
/api/storefront/1/stores/{storeId}/users

# Use consistent resource paths
/api/storefront/1/stores/{storeId}/user/wishlists
/api/storefront/1/stores/{storeId}/user/preferences
```

✅ **Group related operations under common paths**

```yaml
/api/storefront/1/stores/{storeId}/users:
  # List users (admin operation)
  get: {}
  # Create user
  post: {}

/api/storefront/1/stores/{storeId}/user:
  # Get authenticated user
  get: {}
  # Update authenticated user
  patch: {}
  # Delete authenticated user
  delete: {}
```

## HTTP Methods and Status Codes

### HTTP Methods

✅ **Use standard HTTP methods appropriately**

- `GET`: Retrieve resources (safe, idempotent, cacheable)
- `POST`: Create resources (not idempotent)
- `PUT`: Replace resources (idempotent)
- `PATCH`: Partially update resources (not idempotent)
- `DELETE`: Remove resources (idempotent)

### HTTP Status Codes

✅ **Include appropriate HTTP status codes for each operation**:

| Operation | Required Status Codes |
|-----------|----------------------|
| GET (collection) | 200, 400, 401, 500 |
| GET (resource) | 200, 400, 401, 404, 500 |
| POST (collection) | 201, 400, 401, 403, 500 |
| POST (resource) | 201, 400, 401, 403, 409, 500 |
| PUT | 200, 400, 401, 403, 500 |
| DELETE | 204, 400, 401, 403, 404, 409, 500 |
| PATCH | 200, 400, 401, 403, 404, 500 |

✅ **Always include 409 (Conflict) status code for DELETE operations**

```yaml
delete:
  responses:
    '204':
      description: Resource deleted successfully
    '409':
      $ref: '../shared/responses.yml#/responses/Conflict'
```


## Data Type Standards and Property Conventions

### Property Naming Conventions

✅ **For date properties, use the "date" format and use "Date" as a suffix**

```yaml
publishDate:
  type: string
  format: date
  example: "1925-04-10"
```

✅ **For datetime properties, use the "date-time" format and use "DateTime" as a suffix**

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

✅ **For identifiers, always use `id` not entity-prefixed IDs**

```yaml
# Correct
id:
  type: string
  format: uuid

# Avoid
productId:
  type: string
  format: uuid
```

✅ **For monetary amounts, use "Amount" as a suffix and follow the Money schema**

```yaml
totalAmount:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/money/1.0.0/schemas/schemas.yml#/Money'
```

## Data Validation and Constraints

### String Constraints

✅ **Always include maxLength for string properties**

```yaml
productName:
  type: string
  maxLength: 255
  example: "Slim Fit Jeans"
```

### Numeric Constraints

✅ **Include minimum and maximum values for numeric properties**

```yaml
price:
  type: number
  format: double
  minimum: 0
  maximum: 10000
  example: 49.99
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

✅ **Arrays must never be null, use empty arrays instead**

✅ **Include maxItems for array properties**

```yaml
categories:
  type: array
  maxItems: 5
  items:
    type: string
  example: ["WOMAN", "DRESSES", "MIDI"]
```

✅ **Always specify maxItems for array schemas**

```yaml
# Required
data:
  type: array
  maxItems: 100
  items:
    $ref: '#/components/schemas/Product'

# Avoid
data:
  type: array
  items:
    $ref: '#/components/schemas/Product'
```

### Object Constraints

✅ **Explicitly define additionalProperties for object properties**

```yaml
brand:
  type: object
  additionalProperties: false
  properties:
    name:
      type: string
    logoUrl:
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
        $ref: '#/components/schemas/Product'
```

✅ **Name every attribute in request and response payloads**

```yaml
# Instead of this:
GET /api/storefront/1/stores/{storeId}/products/{id}
{
  "id": 358532,
  "name": "Trendy Shirt"
}

# Do this:
GET /api/storefront/1/stores/{storeId}/products/{id}
{
  "product": {
    "id": 358532,
    "name": "Trendy Shirt"
  }
}
```

✅ **Do not repeat parameters between URL and body**

```yaml
# Bad practice:
PUT /api/storefront/1/stores/{storeId}/categories/{id}
{
  "category": {
    "id": 358532,  # Redundant with the path parameter
    "name": "WOMAN"
  }
}

# Good practice:
PUT /api/storefront/1/stores/{storeId}/categories/{id}
{
  "category": {
    "name": "WOMAN"
  }
}
```

## Documentation and Examples

### API Information

✅ **Include comprehensive API descriptions**:

- Purpose of the API
- Target audience
- Key functionality
- Special requirements or considerations

✅ **Include contact information (must be a team or group)**

```yaml
info:
  contact:
    name: "API Support Team"
    email: "api-support@example.com"
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
  /api/storefront/1/stores/{storeId}/users:
    get:
      summary: "Get user information"
      description: "Returns the profile information of the authenticated user"
```

### Examples

#### Operation-Level Examples

✅ **Store complete JSON examples for all API operations**
- Create an `examples` directory alongside the OpenAPI spec file
- Name files based on operation: `[HTTP_METHOD][ResourceName].json` (e.g., `GETUsers.json`)
- Reference in OpenAPI spec using:
  ```yaml
  responses:
    '200':
      content:
        application/json:
          example:
            $ref: "./examples/GETUsers.json"
  ```

#### Schema-Level Examples

✅ **Include examples for all parameters**

```yaml
parameters:
  - name: storeId
    in: path
    required: true
    schema:
      type: string
    example: "10701"
```

✅ **Include examples for all properties in schemas**

```yaml
components:
  schemas:
    User:
      properties:
        id:
          type: string
          format: uuid
          example: "123e4567-e89b-12d3-a456-426614174000"
```

✅ **Examples are mandatory and MUST be provided in a separate `examples` folder, in JSON format**

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
                $ref: '#/components/schemas/Product'
```

### Pagination Parameters

✅ **Use offset/limit pagination by default**

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
                $ref: '#/components/schemas/Product'
            links:
              type: object
              properties:
                self:
                  type: string
                  format: uri
                  example: "https://api.example.com/api/storefront/1/stores/10701/products?limit=10&offset=0"
                prev:
                  type: string
                  format: uri
                  example: "https://api.example.com/api/storefront/1/stores/10701/products?limit=10&offset=0"
                next:
                  type: string
                  format: uri
                  example: "https://api.example.com/api/storefront/1/stores/10701/products?limit=10&offset=10"
                first:
                  type: string
                  format: uri
                  example: "https://api.example.com/api/storefront/1/stores/10701/products?limit=10&offset=0"
            limit:
              type: integer
              example: 10
            offset:
              type: integer
              example: 0
```

✅ **All collections exceeding 100 items or 1MB must be paginated**

## Error Handling

### Error Response Format

✅ **Use the unified Error schema for all error responses**

```yaml
responses:
  '400':
    description: Bad Request
    content:
      application/problem+json:
        schema:
          $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/errors/1.0.2/schemas/errors.yml#/Error'
```

✅ **All error responses (status 4xx-5xx) MUST return the standard Error object**

✅ **Use `Content-Type: application/problem+json` for error responses**

### Required Error Properties

✅ **Error responses should include at minimum**:

- `status`: HTTP status code as an integer
- `title`: A short, human-readable summary of the problem
- `detail`: A human-readable explanation specific to this occurrence of the problem
- `timestamp`: When the error occurred

### Extended Error Format

✅ **You can extend the error object with extraData**

```yaml
'404':
  description: 404 StoreFront error
  content:
    application/problem+json:
      schema:
        allOf:
          - $ref: https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/errors/1.0.2/schemas/errors.yml#/Error
          - type: object
            additionalProperties: false
            properties:
              extraData:
                type: object
                additionalProperties: true
                properties:
                  similarProducts:
                    type: array
                    description: "An array of product ids that are similar to the one that was not found"
                    items:
                      type: integer
                    example:
                      [ 444444, 333333, 222222 ]
```

## Unified Schemas

### Using Unified Schemas

✅ **Use unified schemas for common data structures**

```yaml
# Example of referencing a unified schema
price:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/money/1.0.0/schemas/schemas.yml#/Money'
```

### Available Unified Schemas

The following unified schemas are available for use in API specifications:

#### Error Schema
```yaml
# Standard error response object
Error:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/errors/1.0.2/schemas/errors.yml#/Error'
```

#### Money Schemas
```yaml
# Money object for representing monetary values
Money:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/money/1.0.0/schemas/schemas.yml#/Money'

# Price object with original, previous, current and promotional prices
Price:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/money/1.0.0/schemas/schemas.yml#/Price'

# Currency object for ISO 4217 currencies
Currency:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/money/1.0.0/schemas/schemas.yml#/Currency'
```

#### Pagination Schemas
```yaml
# Complete pagination object
Pagination:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/pagination/1.0.0/schemas/schemas.yml#/Pagination'

# Limit for controlling number of items returned
Limit:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/pagination/1.0.0/schemas/schemas.yml#/Limit'

# Offset for starting position in paginated lists
Offset:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/pagination/1.0.0/schemas/schemas.yml#/Offset'
```

#### Parameter Schemas
```yaml
# Store ID path parameter
storeId:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/params/1.0.0/schemas/path.yml#/storeId'

# Language query parameter using BCP-47 standard
language:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/params/1.0.0/schemas/query.yml#/language'
```

#### Client ID Schema
```yaml
# Client ID parameter (replaces appId and device-channel)
clientId:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/clientId/1.0.0/schemas/clientId.yml#/clientId'
```

#### User ID Schema
```yaml
# User ID parameter
userId:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/userId/1.0.0/schemas/userId.yml#/userId'
```

#### XMedia Schemas
```yaml
# Media asset representation for Storefront
StoreFrontMedia:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/xmedia/1.0.0/schemas/schemas.yml#/StoreFrontMedia'

# Core media asset object
MediaAsset:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/xmedia/1.0.0/schemas/schemas.yml#/MediaAsset'
```

#### Product Schemas
```yaml
# Commercial component object
SimplifiedCommercialComponent:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/product/1.0.0/schemas/schemas.yml#/SimplifiedCommercialComponent'

# Product reference
Reference:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/product/1.0.0/schemas/schemas.yml#/Reference'

# Product classification
Classification:
  $ref: 'https://inditex.jfrog.io/artifactory/apischemas-public/ecommhub/rest/product/1.0.0/schemas/schemas.yml#/Classification'
```

### Unified Schema Best Practices

✅ **Always use unified schemas for standard data types instead of creating custom ones**

✅ **Keep versioning in mind when referencing schemas**

✅ **Standardize on the recommended schemas for common concepts:**
- Use Error schema for all error responses
- Use Money schema for all monetary values
- Use Pagination schema for all paginated responses
- Use standard parameters (storeId, language) consistently across all APIs

### Standard Types

✅ **Date and Time Representation**
- Use suffix `Date` for date without time
- Use suffix `DateTime` for date with time
- Use ISO 8601 format (UTC timezone)
- Examples: 
  - `"createdDateTime": "2012-01-01T12:00:00.000Z"`
  - `"createdDate": "2012-01-01"`

✅ **Money Representation**
- Use the unified Money schema
- Attributes representing monetary amounts must end with suffix `...Amount`
- Use ISO 4217 currency codes

✅ **Phone Number Representation**
- Use the PhoneNumber schema with `countryCallingCode` and `subscriberNumber`

✅ **Identifiers**
- Always name identifiers as `id` (not `entityId` or `entity_id`)
- Fields with pattern *[entity]Id* are considered references to external entities
- Generally use `type: string` for identifiers, particularly when they can grow large

## Resource-Oriented Design

Resource-oriented design is the foundation of RESTful APIs. It focuses on modeling domain concepts as resources rather than actions. This section provides a clear decision tree for transforming action-based operations into resource-oriented alternatives.

### Decision Tree for Resource Design

#### 1. Basic CRUD Operations
✅ **DO: Use standard HTTP methods on resource collections and individual resources**

```yaml
# Wishlist Collection Operations
GET    /api/storefront/1/stores/{storeId}/wishlists          # List all wishlists
POST   /api/storefront/1/stores/{storeId}/wishlists          # Create a new wishlist

# Individual Wishlist Operations
GET    /api/storefront/1/stores/{storeId}/wishlists/{id}     # Get a specific wishlist
PATCH  /api/storefront/1/stores/{storeId}/wishlists/{id}     # Update wishlist details
DELETE /api/storefront/1/stores/{storeId}/wishlists/{id}     # Delete a wishlist
```

❌ **DON'T: Use verbs or actions in URLs**

```yaml
# Avoid these action-based URLs
POST   /api/storefront/1/stores/{storeId}/wishlists/create
POST   /api/storefront/1/stores/{storeId}/wishlists/{id}/update
POST   /api/storefront/1/stores/{storeId}/wishlists/{id}/delete
```

#### 2. State Changes
✅ **DO: Use PATCH to update status/state properties**

```yaml
# Change wishlist from private to public
PATCH /api/storefront/1/stores/{storeId}/wishlists/{id}
{
  "isPublic": true
}

# Share a wishlist with specific users
PATCH /api/storefront/1/stores/{storeId}/wishlists/{id}
{
  "sharedWith": ["user123", "user456"]
}
```

❌ **DON'T: Create special action endpoints for state changes**

```yaml
# Avoid these action endpoints
POST /api/storefront/1/stores/{storeId}/wishlists/{id}/actions/make-public
POST /api/storefront/1/stores/{storeId}/wishlists/{id}/actions/share
```

#### 3. Sub-resource Operations
✅ **DO: Model related entities as sub-resources**

```yaml
# Wishlist items as sub-resources
POST   /api/storefront/1/stores/{storeId}/wishlists/{id}/items        # Add item to wishlist
GET    /api/storefront/1/stores/{storeId}/wishlists/{id}/items        # Get all items in wishlist
DELETE /api/storefront/1/stores/{storeId}/wishlists/{id}/items/{itemId}  # Remove item from wishlist
```

❌ **DON'T: Use action verbs for sub-resource operations**

```yaml
# Avoid these action verbs
POST /api/storefront/1/stores/{storeId}/wishlists/{id}/actions/add-item
POST /api/storefront/1/stores/{storeId}/wishlists/{id}/actions/remove-item
```

#### 4. Complex Searches
✅ **DO: Create dedicated search resources for complex filtering**

```yaml
# Create a search for wishlists
POST /api/storefront/1/stores/{storeId}/wishlist-searches
{
  "criteria": {
    "productIds": [123, 456],
    "createdDateRange": {
      "from": "2023-01-01",
      "to": "2023-12-31"
    },
    "isPublic": true
  },
  "sort": {
    "field": "createdDateTime",
    "order": "DESC"
  }
}

# Get search results
GET /api/storefront/1/stores/{storeId}/wishlist-searches/{searchId}
```

❌ **DON'T: Use filter actions or complex query parameters**

```yaml
# Avoid complex action endpoint
POST /api/storefront/1/stores/{storeId}/wishlists/actions/filter

# Avoid overly complex query parameters
GET /api/storefront/1/stores/{storeId}/wishlists?productIds=123,456&startDate=2023-01-01&endDate=2023-12-31&...
```

#### 5. Process Initiation
✅ **DO: Create request resources for multi-step processes**

```yaml
# Initiate wishlist sharing process
POST /api/storefront/1/stores/{storeId}/wishlist-sharing-requests
{
  "wishlistId": "abc123",
  "recipients": ["user@example.com"],
  "message": "Check out these items I saved!"
}

# Check status of sharing request
GET /api/storefront/1/stores/{storeId}/wishlist-sharing-requests/{requestId}
```

❌ **DON'T: Use action endpoints for processes**

```yaml
# Avoid action endpoints
POST /api/storefront/1/stores/{storeId}/wishlists/{id}/actions/share-via-email
```

## Examples of Well-Designed Paths

### Navigation
```
GET    /api/storefront/1/stores/{storeId}/navigation/home            # Get home page content
GET    /api/storefront/1/stores/{storeId}/menu                       # Get store menu structure
GET    /api/storefront/1/stores/{storeId}/menu/items                 # Get menu item details
GET    /api/storefront/1/stores/{storeId}/events/milestones          # Get available milestones
```

### Product
```
GET    /api/storefront/1/stores/{storeId}/products/{reference}                    # Get products by reference
GET    /api/storefront/1/stores/{storeId}/products/id/{productId}                 # Get product by ID
GET    /api/storefront/1/stores/{storeId}/products/{reference}/extra-detail       # Get product extra details
GET    /api/storefront/1/stores/{storeId}/products/id/{productId}/extra-detail    # Get product extra details by ID
```

### User
```
POST   /api/storefront/1/stores/{storeId}/users                      # Create user (registration)
GET    /api/storefront/1/stores/{storeId}/user                       # Get authenticated user info
PATCH  /api/storefront/1/stores/{storeId}/user                       # Update authenticated user profile
```

### Password
```
POST   /api/storefront/1/stores/{storeId}/password-change-requests     # Create password change request
POST   /api/storefront/1/stores/{storeId}/password-recovery-requests   # Create recovery request
PUT    /api/storefront/1/stores/{storeId}/user/password                # Set password from recovery or change request
```

### Email & Phone
```
POST   /api/storefront/1/stores/{storeId}/email-verification-requests  # Create verification request
PUT    /api/storefront/1/stores/{storeId}/user/email                   # Update authenticated user email
DELETE /api/storefront/1/stores/{storeId}/user/phone                   # Remove authenticated user phone
```

### Wishlist
```
GET    /api/storefront/1/stores/{storeId}/wishlists                              # Get all wishlists
POST   /api/storefront/1/stores/{storeId}/wishlists                              # Create a new wishlist
GET    /api/storefront/1/stores/{storeId}/wishlists/{wishlistId}                 # Get a specific wishlist
DELETE /api/storefront/1/stores/{storeId}/wishlists/{wishlistId}                 # Delete a wishlist
POST   /api/storefront/1/stores/{storeId}/wishlists/{wishlistId}/items           # Add item to wishlist
DELETE /api/storefront/1/stores/{storeId}/wishlists/{wishlistId}/items/{itemId}  # Remove item
```

### Cards
```
GET    /api/storefront/1/stores/{storeId}/cards                      # Get user cards
POST   /api/storefront/1/stores/{storeId}/cards                      # Add a new card
DELETE /api/storefront/1/stores/{storeId}/cards/{cardToken}          # Delete a card
GET    /api/storefront/1/stores/{storeId}/cards/configuration        # Get configuration
```

### Cart
```
GET    /api/storefront/1/stores/{storeId}/carts/summaries            # Get summaries of user carts
GET    /api/storefront/1/stores/{storeId}/carts/{cartId}/summaries   # Get a specific cart summary
POST   /api/storefront/1/stores/{storeId}/orders/{orderId}/promotions  # Add promotions to cart
DELETE /api/storefront/1/stores/{storeId}/orders/{orderId}/promotions/{promoId}  # Remove promotion
```

### Checkout
```
POST   /api/storefront/1/stores/{storeId}/purchase-attempts/{paId}/checkout       # Initiate checkout
PATCH  /api/storefront/1/stores/{storeId}/purchase-attempts/{paId}                # Update purchase attempt
PUT    /api/storefront/1/stores/{storeId}/purchase-attempts/{paId}/shipping       # Set shipping method
```
