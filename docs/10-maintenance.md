# Maintenance

This document provides guidelines for maintaining and updating the Car Repair and Sales Tracking Application.

## Database Maintenance

### Backup Procedures

The application database should be backed up regularly using the following procedures:

1. **Daily Incremental Backups**:
   ```bash
   # Execute from project root
   python manage.py backup --type=incremental --destination=/backup/daily/$(date +%Y%m%d)
   ```

2. **Weekly Full Backups**:
   ```bash
   # Execute on Sundays
   python manage.py backup --type=full --destination=/backup/weekly/$(date +%Y%m%d)
   ```

3. **Monthly Archive Backups**:
   ```bash
   # Execute on the 1st of each month
   python manage.py backup --type=full --compress=true --destination=/backup/monthly/$(date +%Y%m)
   ```

### Database Schema Migrations

The application uses Flask-Migrate for database schema changes:

1. **Creating Migrations**:
   ```bash
   # After model changes, generate a migration
   flask db migrate -m "Description of changes"
   
   # Review the generated migration script in migrations/versions/
   
   # Apply the migration
   flask db upgrade
   ```

2. **Rolling Back Migrations**:
   ```bash
   # Revert to previous version
   flask db downgrade
   ```

3. **Migration Best Practices**:
   - Always review auto-generated migrations before applying
   - Keep migrations small and focused on specific changes
   - Include thorough comments in migration files
   - Test migrations in development environment before production

### Database Performance Optimization

Regularly perform the following database maintenance tasks:

1. **Index Optimization**:
   ```bash
   # Analyze database for missing or redundant indexes
   python manage.py analyze_indexes
   
   # Apply recommended index changes
   python manage.py optimize_indexes
   ```

2. **Database Vacuuming** (SQLite):
   ```bash
   # Remove unused space and defragment database
   python manage.py vacuum_database
   ```

3. **Query Performance Analysis**:
   ```bash
   # Identify slow queries
   python manage.py analyze_queries --threshold=1.0  # Queries taking > 1 second
   ```

## Application Updates

### Dependency Management

The application dependencies should be managed carefully:

1. **Updating Dependencies**:
   ```bash
   # Check for outdated packages
   pip list --outdated
   
   # Update specific package
   pip install --upgrade package-name
   
   # Update all dependencies within version constraints
   pip install --upgrade -r requirements.txt
   
   # Generate updated requirements file after changes
   pip freeze > requirements.txt
   ```

2. **Dependency Security Checks**:
   ```bash
   # Check for security vulnerabilities
   pip install safety
   safety check -r requirements.txt
   ```

### Code Updates

When updating application code:

1. **Version Control Workflow**:
   ```bash
   # Create feature branch
   git checkout -b feature/feature-name
   
   # Make changes
   # ...
   
   # Run tests
   pytest
   
   # Commit changes
   git commit -m "Description of changes"
   
   # Merge to development branch
   git checkout dev
   git merge feature/feature-name
   
   # Deploy to staging for testing
   # ...
   
   # Merge to main branch for production
   git checkout main
   git merge dev
   ```

2. **Code Quality Checks**:
   ```bash
   # Run linters
   flake8 app/
   
   # Run static type checker
   mypy app/
   
   # Check code formatting
   black --check app/
   ```

## Deployment Procedures

### Development Environment

Deploy to development environment:

```bash
# Update codebase
git pull origin dev

# Install/update dependencies
pip install -r requirements.txt

# Apply migrations
flask db upgrade

# Restart development server
flask run
```

### Staging Environment

Deploy to staging environment:

```bash
# Update codebase
git pull origin dev

# Install/update dependencies
pip install -r requirements.txt

# Apply migrations
flask db upgrade

# Run tests
pytest

# Restart staging server
sudo systemctl restart carapp-staging
```

### Production Environment

Deploy to production environment:

```bash
# Update codebase
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Create backup before migration
python manage.py backup --type=pre-update

# Apply migrations
flask db upgrade

# Run tests
pytest

# Restart production server
sudo systemctl restart carapp
```

### Rollback Procedures

If a deployment causes issues:

```bash
# Revert to previous code version
git checkout main@{1}

# Restore database from pre-update backup
python manage.py restore --source=/backup/pre-update/latest

# Restart server
sudo systemctl restart carapp
```

## Monitoring and Logging

### Log Management

The application uses structured logging:

1. **Log Locations**:
   - Application Logs: `/var/log/carapp/app.log`
   - Error Logs: `/var/log/carapp/error.log`
   - Access Logs: `/var/log/carapp/access.log`
   - Database Logs: `/var/log/carapp/db.log`

2. **Log Rotation**:
   ```bash
   # Configure logrotate (typically in /etc/logrotate.d/carapp)
   /var/log/carapp/*.log {
       daily
       missingok
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 carapp carapp
       sharedscripts
       postrotate
           systemctl reload carapp
       endscript
   }
   ```

3. **Log Analysis**:
   ```bash
   # Basic log statistics
   python manage.py analyze_logs --period=24h
   
   # Error frequency analysis
   python manage.py error_report --period=7d
   ```

### Performance Monitoring

Monitor application performance:

1. **System Resource Monitoring**:
   ```bash
   # CPU, memory, and disk usage
   python manage.py monitor_resources
   ```

2. **Response Time Monitoring**:
   ```bash
   # Monitor endpoint response times
   python manage.py monitor_performance
   ```

3. **Database Connection Monitoring**:
   ```bash
   # Check database connection pool
   python manage.py monitor_db_connections
   ```

## Data Management

### Data Import/Export

The application supports data import and export:

1. **Data Export**:
   ```bash
   # Export all data to JSON
   python manage.py export --format=json --output=backup.json
   
   # Export specific tables
   python manage.py export --tables=cars,sales --format=csv --output=export/
   ```

2. **Data Import**:
   ```bash
   # Import data from JSON
   python manage.py import --format=json --input=backup.json
   
   # Import specific tables
   python manage.py import --tables=cars --format=csv --input=import/cars.csv
   ```

### Data Cleanup

Perform regular data maintenance:

1. **Orphaned Records Cleanup**:
   ```bash
   # Identify and clean orphaned records
   python manage.py cleanup_orphans
   ```

2. **Temporary Data Pruning**:
   ```bash
   # Remove temporary data older than 30 days
   python manage.py prune_temp_data --age=30d
   ```

3. **Audit Log Archiving**:
   ```bash
   # Archive audit logs older than 90 days
   python manage.py archive_logs --type=audit --age=90d --destination=/archive/audit/
   ```

## Security Maintenance

### Security Updates

Keep the application security current:

1. **Security Patch Application**:
   ```bash
   # Apply security patches
   pip install --upgrade security-patched-packages
   ```

2. **Security Configuration Review**:
   ```bash
   # Check security configuration
   python manage.py security_check
   ```

3. **Security Scanning**:
   ```bash
   # Scan for common vulnerabilities
   python manage.py security_scan
   ```

### User Access Management

Manage user access:

1. **User Audit**:
   ```bash
   # List all users with roles
   python manage.py list_users
   
   # Audit user activity
   python manage.py user_activity --period=30d
   ```

2. **Inactive User Management**:
   ```bash
   # Identify inactive users (90+ days)
   python manage.py inactive_users --days=90
   
   # Disable inactive users
   python manage.py disable_users --inactive-days=90
   ```

## System Configuration

### Configuration Management

The application uses environment-specific configuration:

1. **Configuration Files**:
   - `.env.development`: Development environment variables
   - `.env.staging`: Staging environment variables
   - `.env.production`: Production environment variables

2. **Configuration Update**:
   ```bash
   # Update configuration and restart
   nano .env.production
   # Edit configuration values
   sudo systemctl restart carapp
   ```

3. **Configuration Validation**:
   ```bash
   # Validate configuration
   python manage.py validate_config
   ```

## Troubleshooting

### Common Issues

#### Database Connection Issues

**Symptoms**:
- Application returns 500 errors
- Logs show database connection errors

**Resolution**:
```bash
# Check database status
sudo systemctl status postgresql

# Restart database if needed
sudo systemctl restart postgresql

# Check application database connection
python manage.py check_db_connection
```

#### Application Performance Issues

**Symptoms**:
- Slow response times
- High CPU or memory usage

**Resolution**:
```bash
# Check system resources
top -u carapp

# Check for slow queries
python manage.py analyze_queries --running

# Restart application
sudo systemctl restart carapp
```

#### Login/Authentication Issues

**Symptoms**:
- Users unable to log in
- Session expiration problems

**Resolution**:
```bash
# Check authentication logs
tail -n 100 /var/log/carapp/auth.log

# Verify session configuration
python manage.py check_auth_config

# Reset user password if needed
python manage.py reset_password --username=admin
```

### Diagnostic Tools

The application includes diagnostic tools:

1. **Health Check**:
   ```bash
   # Check application health
   python manage.py health_check
   ```

2. **System Diagnostics**:
   ```bash
   # Run diagnostic suite
   python manage.py diagnostics
   ```

3. **Test Environment**:
   ```bash
   # Create isolated test environment
   python manage.py create_test_env
   
   # Run tests in isolation
   python manage.py test_in_isolation
   ```

## Backup and Disaster Recovery

### Disaster Recovery Plan

The application has a disaster recovery plan:

1. **Complete System Failure**:
   - Provision new server with same specifications
   - Install OS and dependencies
   - Deploy application code
   - Restore database from latest backup
   - Restore configuration from backup
   - Update DNS records if IP changed
   - Test functionality

2. **Database Corruption**:
   - Stop application
   - Restore database from latest backup
   - Apply transaction logs (if available)
   - Validate database integrity
   - Restart application
   - Test functionality

3. **Application Corruption**:
   - Deploy previous known-good version
   - Validate database compatibility
   - Test functionality

### Recovery Testing

Regularly test disaster recovery:

```bash
# Test restoration to temporary server
python manage.py test_recovery --target=temp-server

# Validate restored data
python manage.py validate_restoration

# Document recovery time
python manage.py record_recovery_metrics
```

## Performance Optimization

### Application Optimization

Optimize application performance:

1. **Code Profiling**:
   ```bash
   # Profile application performance
   python -m cProfile -o profile.pstats manage.py profile
   
   # Analyze profile
   python -m pstats profile.pstats
   ```

2. **Cache Configuration**:
   ```bash
   # Analyze cache hit/miss ratio
   python manage.py analyze_cache
   
   # Optimize cache configuration
   python manage.py optimize_cache
   ```

3. **Static Asset Optimization**:
   ```bash
   # Minimize and bundle static assets
   python manage.py optimize_assets
   ```

### Database Optimization

Optimize database performance:

1. **Query Optimization**:
   ```bash
   # Identify and optimize slow queries
   python manage.py optimize_queries
   ```

2. **Index Tuning**:
   ```bash
   # Analyze index usage
   python manage.py analyze_indexes
   
   # Create missing indexes
   python manage.py create_indexes
   ```

## Documentation Maintenance

Keep documentation up to date:

1. **Documentation Updates**:
   ```bash
   # Generate updated API documentation
   python manage.py generate_api_docs
   
   # Check documentation for broken links
   python manage.py check_docs
   ```

2. **Change Log Maintenance**:
   ```bash
   # Update change log from commits
   python manage.py update_changelog
   ```

## Scheduled Maintenance Tasks

Set up regular maintenance:

1. **Daily Tasks**:
   - Database backup
   - Log rotation
   - Performance monitoring

2. **Weekly Tasks**:
   - Full database backup
   - Security updates
   - Error log analysis

3. **Monthly Tasks**:
   - Inactive user audit
   - Database optimization
   - Documentation review
   - Recovery testing

4. **Quarterly Tasks**:
   - Dependency updates
   - Full security audit
   - Performance optimization 