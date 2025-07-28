# Mandatory Instructions to build SPAs from Figma Designs

When you are planning a task, take account all this mandatory instrucctions to act the plan.

## 1. Exact Design Match  
- The final result **must be exactly the same** as the Figma design.  
- **Approximations are not acceptable**—the implementation must be pixel-perfect.  

## 2. Component Verification  
- For **each node** in the Figma design, retrieve its information and documentation about how to use is equivalent component in Amiga Framework Web.  

## 3. Valid Icon Usage  
- Ensure that every **icon used** is a **valid** icon from the official **icon catalog**.  
- **Do not use unapproved or custom icons.**  

## 4. Strict Figma API Workflow Compliance  
- Always follow the **Extracting Information via the Figma API** workflow as specified.  
- All steps inside it are **mandatory** and should never be skipped or altered.  

## 5. Text Content Integrity  
- The text content in the design must be **exactly the same** in the final implementation.  
- **No modifications, additions, or fabrications** of text are allowed.

# Extracting information of Figma Design

Always you receive a Figma link, take into consideration that the user will provide a link containing the **fileKey** and the **nodeId**. If the user provides a figma link, you may take into account the following format: "https://www.figma.com/design/<fileKey>/<fileName>?node-id=<nodeId>...".

After parsing fileKey and the nodeId, you must to do the following steps:

**First step**: Fetching the node image. Use the tool `get_node_image` from the DS-SEWING MCP.
  - Retrieve the image from the URL returned by the tool. Process the image to extract relevant context, such as objects, text, colors, or any other meaningful information. Use this extracted context to enhance decision-making or improve the accuracy of subsequent tasks. **I want that you be exhaustive implementing the design**.

**Second step**: Fetching the Overview of the design. Use the tool `design_sewing_overview` from the DS-SEWING MCP.
  - Retrieve the figma nodes tree from the object returned.

**Third step**: Considering the image, documentation and the structure of the node, follow the next instructions to process the Node Tree and build the UI:
 
  ## 1. Traverse the Node Tree  
  - **Iterate individually through each node in the tree**.  
  - Identify if a node is a child of another and handle its placement accordingly in the UI hierarchy.
  
  ## 2. Identify and Process Nodes

  In the previous tree, you have to act in a different way depending what the node is representing:

  ### Design System Components  
  If the `type` field is "INSTANCE", and the specifications for that component were provided by the `design_sewing_overview` tool (in the SDS COMPONENT SPECIFICATIONS section of the response, matching the name of the component), consider it a component from one of Inditex Design Systems (DS).
  
  Take into consideration:
  
  - This node has an equivalent React component in Amiga Framework Web or another supported Inditex front-end library, with the same or a similar name as <NameOfComponent>. If there is no exact equivalent, look for the best option within the framework and make necessary adaptations.
  - If the component's import field shows that it is a component from a different package than `@amiga-fwk-web/*`, then you will have to ask for permission to install the dependency first. Then you will be able to import and use such component.
  - Before building the React component, consult component information about how to use the component in Amiga Framework web through **Geppeto MCP**. If the node includes `documentationLinks`, refer to the documentation through **Geppetto MCP** to understand how to use the component properly.
  - Each node has a `componentProperties` key that stores the properties set in Figma. Each key within componentProperties corresponds to a Prop of the equivalent component in Amiga Framework Web.
  - The agent must:
    1. Attempt to map componentProperties keys to the corresponding Props in Amiga Framework Web. Try to map with existing properties of the component if is not a direct match.
    2. Extract the Prop value from componentProperties.[keyId].value.
    3. Validate that the value is compatible with Amiga Framework Web Component prop. If the value is incompatible, transform it into a valid option for the Prop component.
  
  - Construct the component based on the provided framework guidelines.  
  
  ### Other Nodes  
  Represent custom components:
  - Use the tool `get_node_info` from the DS-SEWING MCP to retrieve additional details.
  - If the component is not a DS component, you may try to search for similar components through **Geppeto MCP**.  
  - If there is no direct framework equivalent, render it as a `div`, taking into account the node's `css` property to define its styles.  
  
  ## 3. Building Components in React  
  - Generate a React component for each node with the appropriate structure. Be exhaustive with the design.
  - Add the `data-node-id="{id}"` property to each node for tracking and debugging purposes.  
  - If the node has children, first try to match them to existing props of the React Component that support children. If none exist, add them manually as `children`.  
  
  ## 4. Generating the Final Code  
  - Assemble all generated components into a valid React structure.  
  - Ensure styles are correctly applied via `className` or inline `style`. 
  - Verify that each node behaves according to the documentation or the specifications retrieved from `get_node_info`.   

# Obtaining the catalog of icons

Get all the available icons at Inditex, using the tool `get_inditex_icons`. This provides the list of available icons, with their "group" and "name" properties that you will need to instantiate the `AmigaIcon` component from the Amiga Framework Web.

# Obtaining foundations

Before create css files, classes or variables, try to use always the catalog of Sewing foundations for colors, sizing, viewports and typography. Do not invent css variables.

To get all the foundations of the Sewing in the Amiga Framework Web, yoi can use `get_foundations` tool for colors, sizing, viewports and typography.
