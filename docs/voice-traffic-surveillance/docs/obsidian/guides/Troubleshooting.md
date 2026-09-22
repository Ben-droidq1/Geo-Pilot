# Troubleshooting Guide

## Common Issues

### Installation Issues

#### Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
pip install -r requirements.txt --force-reinstall
```

#### Port Already in Use

**Error:**
```
Error: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn tools.traffic_server:app --port 8001
```

#### Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix permissions
chmod +x publish.py
chmod +x deployment/browser/server.py
```

---

### API Key Issues

#### AssemblyAI API Key Not Set

**Error:**
```
Error: ASSEMBLYAI_API_KEY not set in environment
```

**Solution:**
```bash
# Check .env file exists
cat .env

# Ensure API key is set
ASSEMBLYAI_API_KEY=your_key_here

# Reload environment
source .env
```

#### Invalid API Key

**Error:**
```
Error: Unauthorized (401)
```

**Solution:**
1. Verify API key in AssemblyAI dashboard
2. Check for typos
3. Ensure key is active

---

### Connection Issues

#### Connection Refused

**Error:**
```
Error: Connection refused at localhost:8000
```

**Solution:**
```bash
# Check if server is running
curl http://localhost:8000/health

# If not running, start server
python tools/traffic_server.py

# Check logs
tail -f logs/traffic_surveillance.log
```

#### WebSocket Connection Failed

**Error:**
```
WebSocket connection failed
```

**Solution:**
```bash
# Check WebSocket endpoint
curl http://localhost:8000/ws/traffic-updates

# Verify server is running
ps aux | grep uvicorn

# Check firewall
sudo ufw status
```

---

### Voice Agent Issues

#### Agent Not Responding

**Symptoms:**
- No voice response
- Transcript not updating

**Solution:**
```bash
# Check agent is published
cat .agent_id

# Republish agent
python publish.py

# Check browser server
curl http://localhost:3000/health
```

#### Poor Transcription Quality

**Symptoms:**
- Misheard commands
- Incorrect vehicle names

**Solution:**
1. Add keyterms to `agents/traffic-surveillance.jsonc`
2. Speak clearly and at normal pace
3. Reduce background noise

---

### Camera Issues

#### Camera Offline

**Error:**
```
Camera cam_001 is offline
```

**Solution:**
```bash
# Check camera status
curl -X POST http://localhost:8000/tools/get_camera_status \
  -H "Content-Type: application/json" \
  -d '{"status_filter": "offline"}'

# Verify camera connection
ping camera_ip_address

# Check camera power
```

#### No Detection Data

**Symptoms:**
- Vehicle count is 0
- No tracking data

**Solution:**
1. Verify YOLO model is loaded
2. Check camera feed is active
3. Adjust confidence threshold:

```yaml
detection:
  confidence_threshold: 0.3  # Lower threshold
```

---

### Performance Issues

#### Slow Response Times

**Symptoms:**
- API responses > 1s
- Voice delay

**Solution:**
```bash
# Check system resources
top
htop

# Increase workers
uvicorn tools.traffic_server:app --workers 4

# Enable GPU
# Edit config/inference_config.yaml
performance:
  gpu_enabled: true
```

#### High Memory Usage

**Symptoms:**
- System slowdown
- Out of memory errors

**Solution:**
```bash
# Check memory usage
free -h

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Reduce batch size
# Edit config/inference_config.yaml
performance:
  batch_size: 8  # Reduce from 16
```

---

### Database Issues

#### Connection Failed

**Error:**
```
Error: Connection to database failed
```

**Solution:**
```bash
# Check database status
sudo systemctl status postgresql

# Restart database
sudo systemctl restart postgresql

# Check connection
psql -U postgres -d geopilot
```

---

## Debugging

### Enable Debug Logging

```python
# In tools/traffic_server.py
logging.basicConfig(level=logging.DEBUG)
```

### Check Logs

```bash
# Application logs
tail -f logs/traffic_surveillance.log

# System logs
sudo journalctl -u geopilot-traffic -f
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Test traffic stats
curl -X POST http://localhost:8000/tools/get_traffic_stats \
  -H "Content-Type: application/json" \
  -d '{"camera_id": "cam_001"}'

# Test WebSocket
wscat -c ws://localhost:8000/ws/traffic-updates
```

---

## Getting Help

### Documentation

- [[Getting Started]] - Setup guide
- [[Configuration Guide]] - Configuration options
- [[API Reference]] - API documentation

### Support

- **GitHub Issues**: Report bugs
- **Discord**: Community support
- **Email**: support@geopilot.com

### Useful Commands

```bash
# Check Python version
python --version

# Check pip packages
pip list

# Check system info
uname -a

# Check disk space
df -h
```

---

## Related Pages

- [[Getting Started]]
- [[Configuration Guide]]
- [[Deployment Guide]]

## Tags

#troubleshooting #debugging #issues #solutions

---

*Part of [[GeoPilot Traffic Surveillance]]*
