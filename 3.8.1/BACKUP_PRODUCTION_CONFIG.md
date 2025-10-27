# 🔒 Production Backup Configuration

## Current Settings
- **Backup Interval**: 60 minutes (1 hour)
- **Backup Location**: `sqlite_data/backups/`
- **Retention Policy**: 7 days
- **Max Backup Count**: 50 files

## Schedule
- **First Backup**: Immediately when bot starts
- **Subsequent Backups**: Every hour at the same minute the bot started
- **Example**: If bot started at 06:47, backups occur at 07:47, 08:47, 09:47, etc.

## Backup Contents
Each backup ZIP file contains:
1. `user_requests.db` - Main user data
2. `analytics.db` - Analytics data
3. `premium_system.db` - Premium subscriptions
4. `historical_prices.db` - Price history
5. `bypass_stats.db` - Bypass statistics
6. `backup_info.txt` - Backup metadata

## Delivery
- **Method**: Telegram messages to admins
- **Recipients**: All users in `ADMIN_USER_IDS`
- **Format**: ZIP attachment with summary info
- **Retry Logic**: 3 attempts with exponential backoff

## Monitoring
- Check `sqlite_data/backups/` directory for new files
- Monitor bot logs for backup success/failure messages
- Verify admin accounts receive backup files

## File Size
- **Uncompressed**: ~3.3MB (5 databases)
- **Compressed**: ~1.2MB (65% compression)
- **Transfer Time**: 2-3 seconds typical

## Emergency Recovery
To restore from backup:
1. Stop the bot
2. Extract backup ZIP to `sqlite_data/` directory
3. Restart the bot

**Last Updated**: July 13, 2025
**Bot Version**: Production v3.4 