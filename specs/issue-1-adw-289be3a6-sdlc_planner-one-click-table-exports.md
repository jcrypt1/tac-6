# Feature: One Click Table Exports

## Metadata
issue_number: `1`
adw_id: `289be3a6`
issue_json: `{"number":1,"title":"One Click Table Exports","body":"\nAdd one click table exports and one click result export feature to get results as csv files.\nCreate two new endpoints to support these features. One exporting tables, one for exporting query results.\nPlace a download button directly to the left of the \"x\" icon for available tables.\nPlace a download button directly to the left of the \"hide\" button for query results.\nUse the appropriate download icon."}`

## Feature Description
This feature adds CSV export functionality to the Natural Language SQL Interface application. Users will be able to export entire database tables as CSV files with a single click, as well as export query results to CSV. This provides a convenient way to get data out of the application for further analysis in external tools like Excel, Google Sheets, or other data processing applications.

## User Story
As a data analyst
I want to export tables and query results as CSV files with a single click
So that I can use the data in external tools like Excel or share it with colleagues

## Problem Statement
Currently, users can upload data, query it using natural language, and view results in the application. However, there is no way to export this data. Users who want to use their query results in other applications or share data have no convenient way to do so.

## Solution Statement
Add two new API endpoints for CSV export functionality:
1. `GET /api/export/table/{table_name}` - Export an entire table as CSV
2. `POST /api/export/results` - Export query results as CSV

Add download buttons to the UI:
1. A download button to the left of the "x" (remove) icon for each table in the Available Tables section
2. A download button to the left of the "Hide" button in the Query Results section

The download buttons will use an appropriate download icon (arrow pointing down into a tray) and trigger browser downloads of CSV files.

## Relevant Files
Use these files to implement the feature:

- `app/server/server.py` - Main FastAPI server where new endpoints will be added
- `app/server/core/data_models.py` - Pydantic models for request/response types; new export response model needed
- `app/server/core/sql_processor.py` - SQL execution utilities; used to fetch table data
- `app/server/core/sql_security.py` - Security utilities for safe query execution
- `app/client/src/main.ts` - Main client TypeScript file where UI event handlers and download logic will be added
- `app/client/src/api/client.ts` - API client; new export API methods will be added
- `app/client/src/types.d.ts` - TypeScript type definitions; new types for export responses
- `app/client/src/style.css` - Styles for the download button
- `app/client/index.html` - HTML structure (no changes needed, buttons added via JS)
- `app/server/tests/test_sql_injection.py` - Example test file; reference for adding new tests
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test file

### New Files
- `app/server/tests/test_export.py` - Unit tests for export endpoints
- `.claude/commands/e2e/test_table_exports.md` - E2E test for table exports feature

## Implementation Plan
### Phase 1: Foundation
- Add new Pydantic models for export responses in `data_models.py`
- Create utility functions for CSV generation in a new module or extend existing ones
- Add TypeScript type definitions for export functionality

### Phase 2: Core Implementation
- Implement `/api/export/table/{table_name}` endpoint that:
  - Validates the table name using existing security utilities
  - Fetches all data from the table
  - Generates CSV content with proper escaping
  - Returns as downloadable file with appropriate headers
- Implement `/api/export/results` endpoint that:
  - Accepts query results data from the client
  - Generates CSV content
  - Returns as downloadable file
- Add API client methods for triggering downloads
- Add download buttons to UI with proper styling

### Phase 3: Integration
- Wire up download buttons to trigger CSV downloads
- Test end-to-end functionality
- Ensure proper error handling for edge cases (empty tables, special characters in data)

## Step by Step Tasks

### Task 1: Create E2E Test File
- Create `.claude/commands/e2e/test_table_exports.md` with test steps to validate:
  - Load sample data (users table)
  - Verify download button appears next to "x" icon for tables
  - Click table download button and verify download triggers
  - Run a query
  - Verify download button appears next to "Hide" button in results
  - Click results download button and verify download triggers

### Task 2: Add Export Response Models
- Edit `app/server/core/data_models.py` to add:
  - `ExportResultsRequest` model with `columns: List[str]` and `results: List[Dict[str, Any]]` fields

### Task 3: Implement Table Export Endpoint
- Edit `app/server/server.py` to add:
  - `GET /api/export/table/{table_name}` endpoint
  - Use `validate_identifier` for table name validation
  - Use `check_table_exists` to verify table exists
  - Query all data from the table using `execute_query_safely`
  - Generate CSV content with proper header row and data rows
  - Use Python's `csv` module with `io.StringIO` for CSV generation
  - Return `StreamingResponse` with `Content-Disposition: attachment; filename="{table_name}.csv"` header
  - Return `text/csv` content type

### Task 4: Implement Results Export Endpoint
- Edit `app/server/server.py` to add:
  - `POST /api/export/results` endpoint
  - Accept `ExportResultsRequest` body with columns and results
  - Generate CSV content from the provided data
  - Return `StreamingResponse` with `Content-Disposition: attachment; filename="query_results.csv"` header
  - Return `text/csv` content type

### Task 5: Add Unit Tests for Export Endpoints
- Create `app/server/tests/test_export.py` with tests for:
  - Table export with valid table name
  - Table export with non-existent table (404 error)
  - Table export with invalid table name (400 error)
  - Results export with valid data
  - Results export with empty results
  - CSV escaping for special characters (commas, quotes, newlines)

### Task 6: Add TypeScript Types
- Edit `app/client/src/types.d.ts` to add:
  - `ExportResultsRequest` interface matching the server model

### Task 7: Add API Client Methods
- Edit `app/client/src/api/client.ts` to add:
  - `exportTable(tableName: string): void` method that creates a hidden link element and triggers download from `/api/export/table/{tableName}`
  - `exportResults(columns: string[], results: Record<string, any>[]): Promise<void>` method that POSTs to `/api/export/results` and triggers download

### Task 8: Add CSS Styles for Download Button
- Edit `app/client/src/style.css` to add:
  - `.download-table-button` class styled similarly to `.remove-table-button`
  - `.download-results-button` class styled similarly to `.toggle-button`
  - Hover states for both button types
  - Appropriate spacing to position buttons correctly

### Task 9: Add Download Button to Tables Section
- Edit `app/client/src/main.ts` in the `displayTables` function to:
  - Create a download button element before the remove button
  - Use a download SVG icon (arrow pointing down) or Unicode character
  - Add click handler that calls `api.exportTable(table.name)`
  - Style the button using the `.download-table-button` class

### Task 10: Add Download Button to Results Section
- Edit `app/client/src/main.ts` in the `displayResults` function to:
  - Store the current results data (columns and results) in a module-level variable
  - Create a download button element to the left of the "Hide" button in the results header
  - Add click handler that calls `api.exportResults(columns, results)`
  - Style the button using the `.download-results-button` class

### Task 11: Run Validation Commands
- Execute all validation commands to ensure the feature works correctly with zero regressions

## Testing Strategy
### Unit Tests
- Test table export endpoint with valid and invalid table names
- Test results export endpoint with various data shapes
- Test CSV generation with special characters (commas, quotes, newlines, Unicode)
- Test error handling for missing tables

### Edge Cases
- Empty tables (should export with header row only)
- Empty query results (should export with header row only)
- Data with commas, quotes, and newlines (proper CSV escaping)
- Unicode characters in data
- Very large tables (memory considerations)
- Invalid or SQL injection attempts in table names

## Acceptance Criteria
- Download button appears to the left of "x" icon for each table in Available Tables
- Download button appears to the left of "Hide" button in Query Results
- Clicking table download button downloads a CSV file named `{table_name}.csv`
- Clicking results download button downloads a CSV file named `query_results.csv`
- CSV files contain proper headers (column names)
- CSV files properly escape special characters
- Invalid table names return appropriate error responses
- All existing tests continue to pass
- No TypeScript errors in frontend build

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_table_exports.md` test file to validate this functionality works

## Notes
- The download functionality uses a simple approach of creating a temporary anchor element with the download URL, which works for both the GET endpoint (table export) and the POST endpoint (results export via blob URL)
- For the POST endpoint, the client will need to receive the response as a blob and create an object URL for download
- CSV generation uses Python's built-in `csv` module which handles proper escaping of special characters
- The `StreamingResponse` from FastAPI is used to efficiently stream the CSV content without loading everything into memory (important for large tables)
- The download icon can use Unicode character (e.g., `\u2B07` or `\u21E9`) or an inline SVG for better cross-browser compatibility
