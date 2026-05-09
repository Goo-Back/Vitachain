# VitaChain Database Backup Policy

## Automated Backups
- **Frequency:** Daily automatic backups by Supabase
- **Retention:** 30 days
- **Region:** EU-West (Frankfurt)
- **Encryption:** At rest and in transit

## Point-in-Time Recovery
- **Granularity:** 1 minute
- **Retention:** 7 days
- **Availability:** 24/7

## Manual Backups
Manual backups can be created via:
1. Supabase Dashboard
2. Supabase CLI: `supabase db dump`

## Restoration
1. Point-in-time recovery via Supabase Dashboard
2. Full restoration from backup
3. Selective table restoration

## Testing
- Backup restoration tests should be performed quarterly
- Test restoration procedures documented
- Recovery time objective: 4 hours
- Recovery point objective: 15 minutes
