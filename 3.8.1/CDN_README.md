# Telegram Bot Assets CDN Server

A Flask-based CDN server to serve Telegram bot assets including sticker price cards, gift cards, sticker collections, and downloaded images.

## Features

- **RESTful API**: Clean API endpoints for accessing files
- **File Information**: Get detailed file metadata
- **Search Functionality**: Search for files by name
- **Health Monitoring**: Built-in health check endpoint
- **Caching**: HTTP caching headers for better performance
- **Systemd Service**: Can run as a system service
- **Logging**: Comprehensive logging for monitoring

## API Endpoints

### Main Endpoints

- `GET /` - API information and available folders
- `GET /health` - Health check and folder status
- `GET /api/<folder_key>` - List all files in a folder
- `GET /api/<folder_key>/<filename>` - Serve a specific file
- `GET /api/<folder_key>/<filename>/info` - Get file information
- `GET /api/<folder_key>/search?q=<query>` - Search files in a folder

### Available Folders

- `sticker_price_cards` - Sticker price cards
- `new_gift_cards` - New gift cards
- `sticker_collections` - Sticker collections
- `downloaded_images` - Downloaded images

## Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install CDN requirements
pip install -r cdn_requirements.txt
```

### 2. Start the CDN Server

```bash
# Make script executable (if not already)
chmod +x start_cdn.sh

# Start the server
./start_cdn.sh start
```

### 3. Test the CDN

```bash
# Test endpoints
./start_cdn.sh test

# Check status
./start_cdn.sh status
```

## Installation as System Service

### 1. Install Systemd Service

```bash
# Install the service
./start_cdn.sh install

# Start the service
sudo systemctl start cdn-server

# Enable auto-start on boot
sudo systemctl enable cdn-server
```

### 2. Service Management

```bash
# Start service
sudo systemctl start cdn-server

# Stop service
sudo systemctl stop cdn-server

# Restart service
sudo systemctl restart cdn-server

# Check status
sudo systemctl status cdn-server

# View logs
sudo journalctl -u cdn-server -f
```

## Usage Examples

### List All Files in a Folder

```bash
curl https://asadffastest.store/api/new_gift_cards
```

### Get File Information

```bash
curl https://asadffastest.store/api/new_gift_cards/Heart_Locket_card.png/info
```

### Search for Files

```bash
curl "https://asadffastest.store/api/new_gift_cards/search?q=heart"
```

### Download a File

```bash
curl -O https://asadffastest.store/api/new_gift_cards/Heart_Locket_card.png
```

### Health Check

```bash
curl https://asadffastest.store/health
```

## Configuration

### Port Configuration

Edit `cdn_server.py` to change the port:

```python
PORT = 8080  # Change to your desired port
```

### Base Directory

Update the `BASE_DIR` in `cdn_server.py`:

```python
BASE_DIR = "/path/to/your/assets"
```

### Folder Mapping

Modify the `FOLDERS` dictionary in `cdn_server.py`:

```python
FOLDERS = {
    "sticker_price_cards": "Sticker_Price_Cards",
    "new_gift_cards": "new_gift_cards", 
    "sticker_collections": "sticker_collections",
    "downloaded_images": "downloaded_images"
}
```

## Production Deployment

### 1. Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 cdn_server:app
```

### 2. Using Nginx as Reverse Proxy

Create nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. SSL/HTTPS Setup

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Logs

### View Logs

```bash
# Application logs
tail -f cdn.log

# Systemd service logs
sudo journalctl -u cdn-server -f

# Real-time monitoring
watch -n 1 'curl -s https://asadffastest.store/health | jq'
```

### Performance Monitoring

```bash
# Check memory usage
ps aux | grep cdn_server

# Check disk usage
du -sh /home/yousefmsm1/Desktop/3.6.3.1/*/

# Monitor network connections
netstat -tlnp | grep 8080
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8080
   sudo lsof -i :8080
   
   # Kill the process
   sudo kill -9 <PID>
   ```

2. **Permission Denied**
   ```bash
   # Check file permissions
   ls -la cdn_server.py
   
   # Fix permissions
   chmod +x cdn_server.py
   ```

3. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r cdn_requirements.txt
   ```

4. **Service Not Starting**
   ```bash
   # Check service status
   sudo systemctl status cdn-server
   
   # View detailed logs
   sudo journalctl -u cdn-server -n 50
   ```

### Debug Mode

To run in debug mode for development:

```bash
# Edit cdn_server.py and change:
app.run(host=HOST, port=PORT, debug=True, threaded=True)
```

## Security Considerations

1. **Firewall Configuration**
   ```bash
   # Allow only specific IPs
   sudo ufw allow from 192.168.1.0/24 to any port 8080
   ```

2. **Rate Limiting**
   Consider implementing rate limiting for production use.

3. **Authentication**
   For sensitive assets, consider adding authentication middleware.

## API Response Examples

### Folder Listing Response

```json
{
  "folder": "new_gift_cards",
  "folder_name": "new_gift_cards",
  "total_files": 83,
  "files": [
    {
      "name": "Heart_Locket_card.png",
      "size": 245760,
      "modified": "2024-01-15T10:30:00",
      "url": "/api/new_gift_cards/Heart_Locket_card.png"
    }
  ]
}
```

### File Information Response

```json
{
  "filename": "Heart_Locket_card.png",
  "folder": "new_gift_cards",
  "size": 245760,
  "modified": "2024-01-15T10:30:00",
  "mime_type": "image/png",
  "encoding": null,
  "url": "/api/new_gift_cards/Heart_Locket_card.png",
  "direct_url": "https://asadffastest.store/api/new_gift_cards/Heart_Locket_card.png"
}
```

### Health Check Response

```json
{
  "status": "healthy",
  "server_time": "2024-01-15T10:30:00",
  "folders": {
    "sticker_price_cards": {
      "exists": true,
      "path": "/home/yousefmsm1/Desktop/3.6.3.1/Sticker_Price_Cards"
    }
  }
}
```

## Support

For issues and questions:
- Check the logs: `tail -f cdn.log`
- Test endpoints: `./start_cdn.sh test`
- Check service status: `sudo systemctl status cdn-server` 