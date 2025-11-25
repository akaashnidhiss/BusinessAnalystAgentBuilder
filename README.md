# Business Analyst Agent Builder

Cursor for Consultants - A lightweight agentic IDE for business analysts that lets you connect to real data, define tools around it, and spin up AI agents to explore, query, and automate workflows without heavy engineering support.

Building tooling on this to let you build scalable, data native agents, and surface them as MCP Servers for use in any MCP Client platform (Claude, GPTs, etc.)

## Common use cases
- Supplier discovery and segmentation – Quickly search across massive supplier databases, enrich profiles, and group suppliers by capability, geography, risk, or performance based on unstructured descriptions and metadata.
- Taxonomy-based material classification – Map messy material descriptions to a standard taxonomy (UNSPSC, custom schemas), flag inconsistencies, and suggest normalized categories for downstream analytics.
BOM and spec mining – Parse bills of materials and technical specifications to pull out key attributes (materials, tolerances, dimensions, compliance tags) and answer targeted questions without manually reading every line.
- Contract and document tagging – Extract key terms, clauses, and attributes from contracts, SOWs, or policy documents and tag them into structured fields for faster analysis and reporting.
- Ad-hoc data Q&A for projects – Stand up a temporary agent on top of project data (files, tables, exports) so teams can ask natural language questions, get repeatable answers, and avoid rebuilding bespoke one-off analyses.

## What it looks like

**Home – create a new agent**

![BAAB home](frontend/docs/BAAB_Make_Agent_Home.png)

**Step 1 – name and describe your agent**

![BAAB step 1](frontend/docs/BAAB_Make_Agent_Step1.png)

**Step 2 – connect data and tools**

![BAAB step 2](frontend/docs/BAAB_Make_Agent_Step2.png)

**Step 3 – configure prompts and behaviors**

![BAAB step 3](frontend/docs/BAAB_Make_Agent_Step3.png)

**Step 4 – review and launch**

![BAAB step 4](frontend/docs/BAAB_Make_Agent_Step4.png)

## Future plans

- Build out the backend and create a demo friendly hosted product.
- Publish a gallery of reusable agent blueprints for common BA workflows
- Improve collaboration features like sharing agents as MCP Server details.
- Harden backend APIs and add lightweight auth so it’s easier to deploy in team environments

