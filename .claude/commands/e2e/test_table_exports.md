# E2E Test: Table Exports

Test the one-click table exports and query results export functionality.

## User Story

As a data analyst
I want to export tables and query results as CSV files with a single click
So that I can use the data in external tools like Excel or share it with colleagues

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** core UI elements are present:
   - Query input textbox
   - Query button
   - Upload Data button
   - Available Tables section

5. Click "Upload Data" button to open the modal
6. Click the "Users" sample data button to load sample data
7. Wait for the table to appear in Available Tables section
8. Take a screenshot showing the users table with download button
9. **Verify** the download button appears to the left of the "x" (remove) icon for the users table

10. Click the download button for the users table
11. **Verify** the download is triggered (network request to /api/export/table/users)
12. Take a screenshot after clicking download button

13. Enter the query: "Show me all users"
14. Click the Query button
15. Wait for results to appear
16. Take a screenshot of the results section
17. **Verify** the download button appears to the left of the "Hide" button in the results header

18. Click the download button in the results section
19. **Verify** the download is triggered (network request to /api/export/results)
20. Take a screenshot after clicking results download button

## Success Criteria
- Download button appears to the left of "x" icon for each table in Available Tables
- Download button appears to the left of "Hide" button in Query Results
- Clicking table download button triggers a CSV download
- Clicking results download button triggers a CSV download
- 5 screenshots are taken
