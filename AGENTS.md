## Development Instructions
To ensure clean code structure and organization:
- All new widget types should be generated in their own file and class within the @app/widgets/ directory.
- All new screens should be generated in their own file and cliss within the @app/screens/ directory.
- Larger functionality requests should be broken down in reusable functions for single pieces of functionality.
- When updating or adding functionality, ensure relevant usage information is added to the project README.
- This application uses a redis cache for data pulled from the MLB-StatsAPI library. If new functionality requires new data_service requests ensure these requests leverage the application caching strategy with reasonable TTLs.

## Testing Instructions
- All changes MUST have their style verified. Use pylint as described in @.github/workflows/pylint.yml after making any code changes. Ensure tests are included in linting checks.
- All changes MUST be verified by running pytest as described in the README. All tests must pass and code coverage in @app/ must remain at 100%.
- Add unit tests for any new functionality to ensure 100% coverage. 
