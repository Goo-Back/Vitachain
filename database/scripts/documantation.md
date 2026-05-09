# VitaChain Database Setup
 
This directory contains the complete Supabase database setup for the VitaChain platform, including schema, security policies, functions, triggers, and performance optimizations.
 
## Overview
 
VitaChain uses Supabase (PostgreSQL 15) as its primary database with comprehensive Row Level Security (RLS), automated functions, and performance optimizations. The database supports all four platform modules: KATARA (IoT farming), FARMARKET (B2B marketplace), SECONDSERVE (surplus food), and BOTABA9A (marketing).
 
## Directory Structure
 
```
database/
├── README.md                    # This documentation
├── supabase-setup.sh           # Main setup script
├── migrations/                  # Database migration files
│   ├── 01-schema.sql           # Core schema creation
│   ├── 02-rls-policies.sql     # Row Level Security policies
│   ├── 03-functions.sql        # Database functions
│   ├── 04-triggers.sql         # Database triggers
│   ├── 05-indexes.sql          # Performance optimization
│   └── 06-seed-data.sql        # Initial seed data
├── config/                      # Configuration files
│   ├── extensions.sql          # PostgreSQL extensions
│   └── database-config.sql     # Database parameters
├── scripts/                     # Utility scripts
│   ├── test-database.sh        # Comprehensive testing
│   └── verify-setup.sh         # Setup verification
└── docs/                        # Additional documentation
    ├── backup-policy.md        # Backup and recovery procedures
    └── security-guide.md       # Security best practices
```
 
## Quick Start
 
### Prerequisites
 
1. **Supabase Account**: Create a free account at [supabase.com](https://supabase.com)
2. **Supabase CLI**: Install the CLI globally
   ```bash
   npm install -g supabase
   ```
3. **Environment Variables**: Set up your environment
   ```bash
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_ANON_KEY="your-anon-key"
   export SUPABASE_SERVICE_KEY="your-service-role-key"
   export VITACHAIN_DB_PASSWORD="your-secure-password"
   ```
 
### Setup Process
 
1. **Create Supabase Project**
   - Go to [supabase.com/dashboard](https://supabase.com/dashboard)
   - Create new project in EU (Frankfurt) region
   - Choose PostgreSQL 15
   - Generate and save API keys
 
2. **Run Setup Script**
   ```bash
   cd database
   chmod +x supabase-setup.sh
   ./supabase-setup.sh
   ```
 
3. **Verify Installation**
   ```bash
   chmod +x scripts/verify-setup.sh
   ./scripts/verify-setup.sh
   ```
 
4. **Run Tests**
   ```bash
   chmod +x scripts/test-database.sh
   ./scripts/test-database.sh
   ```
 
## Database Schema
 
### Core Tables
 
#### Users & Authentication
- **users**: Core user accounts with email verification
- **user_profiles**: Extended user information (name, role, approval status)
- **roles**: User roles and permissions (farmer, restaurant, citizen, admin)
 
#### IoT & Telemetry (KATARA)
- **devices**: ESP32 devices with location and configuration
- **sensors**: Individual sensors attached to devices
- **telemetry**: Time-series sensor data with quality scores
 
#### Agricultural Marketplace (FARMARKET)
- **products**: Agricultural product listings
- **orders**: Purchase orders with status tracking
- **order_items**: Individual items within orders
 
#### Restaurant Marketplace (SECONDSERVE)
- **meals**: Surplus meal listings with pickup times
- **pickup_slots**: Time slots for meal collection
- **reservations**: Customer reservations with pickup codes
 
#### Notifications & System
- **alerts**: System alerts and notifications
- **email_notifications**: Email notification queue
- **in_app_notifications**: In-app notification system
- **audit_logs**: Complete audit trail
- **system_metrics**: Performance and usage metrics
- **support_tickets**: Customer support system
 
## Security Features
 
### Row Level Security (RLS)
 
All tables have comprehensive RLS policies that ensure:
 
1. **User Isolation**: Users can only access their own data
2. **Role-Based Access**: Different permissions for farmers, restaurants, citizens, and admins
3. **Data Privacy**: Sensitive information is properly protected
4. **API Security**: Different access levels for anonymous, authenticated, and service roles
 
### Security Policies
 
- **Users**: Can only view/update own profiles
- **Farmers**: Can manage own products, view orders for their products
- **Restaurants**: Can manage own meals, view reservations
- **Citizens**: Can view public data, manage own reservations
- **Admins**: Full access to all data for platform management
 
### Authentication Integration
 
- JWT-based authentication with Supabase Auth
- Automatic user profile creation on registration
- Email verification required for account activation
- Admin approval for certain roles (optional)
 
## Performance Optimizations
 
### Indexing Strategy
 
1. **Foreign Key Indexes**: All foreign keys are indexed
2. **Time-Series Optimization**: Telemetry data indexed by device and timestamp
3. **Geospatial Indexes**: Location-based queries use PostGIS
4. **Search Optimization**: Full-text search on product/meal names
5. **Composite Indexes**: Optimized for common query patterns
 
### Query Performance
 
- Target: <200ms response time for 95th percentile
- Connection pooling with PgBouncer
- Automatic query statistics collection
- Slow query monitoring and alerting
 
### Database Configuration
 
- Shared buffers: 256MB (adjustable based on server size)
- Work memory: 4MB per connection
- Autovacuum tuned for time-series data
- WAL optimization for high write throughput
 
## Database Functions
 
### Core Functions
 
- **create_user_profile()**: Create user profile with role assignment
- **register_device()**: Register IoT devices with API key generation
- **ingest_telemetry()**: Ingest sensor data with validation
- **create_product()**: Create agricultural product listings
- **create_order()**: Process B2B orders with inventory management
- **create_meal()**: Create surplus meal listings
- **create_reservation()**: Process meal reservations with pickup codes
- **create_alert()**: Create system alerts and notifications
 
### Utility Functions
 
- **log_audit_event()**: Comprehensive audit logging
- **record_metric()**: System metrics collection
- **check_database_health()**: Database health monitoring
- **get_database_stats()**: Performance statistics
 
## Database Triggers
 
### Automation Triggers
 
- **Timestamp Updates**: Automatic updated_at field management
- **Audit Logging**: Complete audit trail for all data changes
- **Telemetry Alerts**: Automatic alerts for critical sensor readings
- **Order Notifications**: Email notifications for order status changes
- **Reservation Expiration**: Automatic cleanup of expired reservations
- **Data Validation**: Business rule enforcement at database level
 
### Security Triggers
 
- **Device Offline Detection**: Alert when devices go offline
- **Meal Expiration**: Automatic deactivation of expired meals
- **Email Retry Logic**: Automatic retry for failed email notifications
 
## Monitoring & Maintenance
 
### Performance Monitoring
 
- **Database Overview View**: Connection and usage statistics
- **Table Sizes View**: Storage usage monitoring
- **Index Usage View**: Index performance analysis
- **Slow Queries View**: Query optimization guidance
 
### Health Checks
 
- Connection monitoring
- Query performance tracking
- Storage capacity monitoring
- Autovacuum status checking
 
### Maintenance Procedures
 
- Regular statistics updates
- Index maintenance
- Log rotation
- Backup verification
 
## Backup & Recovery
 
### Automated Backups
 
- **Daily Backups**: Automatic daily backups by Supabase
- **Point-in-Time Recovery**: 1-minute granularity for 7 days
- **Cross-Region Replication**: Backup redundancy
- **Encryption**: All backups encrypted at rest
 
### Recovery Procedures
 
1. **Point-in-Time Recovery**: For specific time restoration
2. **Full Restoration**: Complete database restoration
3. **Selective Recovery**: Table-level restoration
4. **Testing**: Regular recovery testing procedures
 
### Backup Configuration
 
```sql
-- Check backup status
SELECT * FROM pg_stat_archiver;
 
-- Verify WAL archiving
SHOW archive_mode;
SHOW archive_command;
```
 
## Testing
 
### Unit Tests
 
- Function testing with various inputs
- RLS policy validation
- Trigger functionality testing
 
### Integration Tests
 
- End-to-end workflow testing
- API endpoint testing
- Performance benchmarking
 
### Test Scripts
 
```bash
# Run comprehensive tests
./scripts/test-database.sh
 
# Verify setup completeness
./scripts/verify-setup.sh
```
 
## Environment Configuration
 
### Development
 
```bash
# .env.development
SUPABASE_URL=https://dev-project.supabase.co
SUPABASE_ANON_KEY=dev-anon-key
SUPABASE_SERVICE_KEY=dev-service-key
DATABASE_URL=postgresql://postgres:password@localhost:5432/dev_db
```
 
### Production
 
```bash
# .env.production
SUPABASE_URL=https://prod-project.supabase.co
SUPABASE_ANON_KEY=prod-anon-key
SUPABASE_SERVICE_KEY=prod-service-key
DATABASE_URL=postgresql://postgres:secure-password@db.prod-project.supabase.co:5432/postgres
```
 
## API Integration
 
### REST API Endpoints
 
```javascript
// Example: Fetch active products
const { data, error } = await supabase
  .from('products')
  .select('*')
  .eq('is_active', true)
  .order('created_at', { ascending: false });
 
// Example: Create reservation
const { data, error } = await supabase
  .rpc('create_reservation', {
    meal_uuid: mealId,
    citizen_uuid: userId,
    quantity: 2
  });
```
 
### Real-time Subscriptions
 
```javascript
// Example: Subscribe to telemetry updates
const subscription = supabase
  .channel('telemetry')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'telemetry' },
    (payload) => console.log('New telemetry:', payload.new)
  )
  .subscribe();
```
 
## Troubleshooting
 
### Common Issues
 
1. **Connection Timeout**: Check SSL configuration and network connectivity
2. **RLS Policy Errors**: Verify user authentication and role assignments
3. **Performance Issues**: Check index usage and query statistics
4. **Storage Limits**: Monitor database size and cleanup old data
 
### Debug Commands
 
```sql
-- Check active connections
SELECT * FROM pg_stat_activity;
 
-- Analyze slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
 
-- Check index usage
SELECT * FROM pg_stat_user_indexes ORDER BY idx_scan DESC;
 
-- Verify RLS policies
SELECT * FROM pg_policies WHERE tablename = 'your_table';
```
 
## Security Best Practices
 
### API Keys
 
- Never expose service role key in client-side code
- Use anon key for client applications
- Rotate keys regularly
- Monitor key usage
 
### Data Protection
 
- Enable SSL/TLS for all connections
- Use parameterized queries to prevent SQL injection
- Implement proper input validation
- Regular security audits
 
### Access Control
 
- Follow principle of least privilege
- Regular user access reviews
- Implement proper session management
- Monitor for suspicious activity
 
## Migration Guide
 
### Schema Changes
 
1. Create new migration file in `migrations/` directory
2. Use descriptive naming: `NN-description.sql`
3. Test migrations on development environment
4. Run migrations in production during maintenance window
 
### Rollback Procedures
 
1. Document rollback steps for each migration
2. Test rollback procedures
3. Have backup verification ready
4. Communicate changes to team
 
## Support
 
### Documentation
 
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/docs/)
 
### Monitoring Tools
 
- Supabase Dashboard
- Custom monitoring views
- Performance metrics collection
- Alert system integration
 
### Getting Help
 
1. Check this documentation first
2. Review Supabase documentation
3. Check application logs
4. Contact database administrator
 
## License
 
This database setup is part of the VitaChain project and follows the project's licensing terms.
 