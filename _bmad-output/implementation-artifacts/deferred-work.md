# Deferred Work Items

## Deferred from: code review of 1-7-performance-optimization (2026-05-02)

- **O(n) linear search in endpoint statistics** - Performance optimization using linear search through metrics list in `backend/app/core/performance.py:131-134`. This is a pre-existing architectural choice that could be optimized in a future performance iteration but doesn't block current functionality.

## Deferred from: code review of story 3-6-weather-data-integration (2026-05-03)

- **30-day retention policy not automated** - Weather data cleanup function exists but no automated scheduling for data retention enforcement. This is a pre-existing infrastructure gap that requires cron job setup or similar automation.
- **Weather component not integrated in actual dashboard** - WeatherWidget component created but integration in the actual KATARA dashboard page not verified. This is a frontend integration task that should be addressed in a separate dashboard enhancement story.

## Deferred from: code review of story 3-9-alert-read-unread-management (2026-05-03)

- **Rate Limiting Missing** - No rate limiting on status update endpoints in backend API routes. This is a broader security concern not specific to this story that should be addressed in a separate security epic.
- **Transaction Safety** - Bulk updates lack database transactions in alert service. This is a pre-existing pattern in the codebase that should be addressed in a broader database consistency epic.
