# 🚀 Telegram Bot Setup Guide

## 📋 **Cross-Platform Installation Guide**

This guide ensures your Telegram bot works perfectly on both **Windows** and **Linux**.

---

## 🎯 **Quick Start**

### **Option 1: Virtual Environment (Recommended)**

#### **Linux/Mac:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### **Windows:**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Option 2: System Installation**

#### **Linux/Mac:**
```bash
pip install -r requirements.txt
```

#### **Windows:**
```cmd
python -m pip install -r requirements.txt
```

---

## 🔧 **Requirements Verification**

Run the compatibility test to verify all packages work:

```bash
python test_requirements_compatibility.py
```

**Expected Output:**
```
🎉 All packages imported successfully!
🎉 Requirements file is compatible with [Platform]!
```

---

## 📦 **Package Categories**

### **Core Dependencies (Required)**
- `python-telegram-bot==22.1` - Main bot framework
- `pyrogram==2.0.106` - Telegram client library
- `tgcrypto==1.2.5` - Fast encryption for pyrogram

### **Image Processing**
- `Pillow==10.2.0` - Image manipulation
- `matplotlib==3.6.3` - Chart generation
- `numpy==1.26.4` - Numerical operations

### **Network & HTTP**
- `requests==2.31.0` - HTTP requests
- `httpx==0.28.1` - Async HTTP client
- `curl_cffi==0.11.4` - Advanced HTTP client
- `anyio==4.9.0` - Async I/O utilities

### **Utilities**
- `python-dateutil==2.8.2` - Date parsing
- `PyYAML==6.0.1` - YAML configuration
- `schedule==1.2.2` - Task scheduling
- `tabulate==0.9.0` - Table formatting

### **Text Processing**
- `fuzzywuzzy==0.18.0` - Fuzzy string matching
- `python-Levenshtein==0.27.1` - String distance

### **Development & Testing**
- `pytest==8.4.1` - Testing framework
- `pytest-mock==3.14.1` - Mocking utilities

### **Additional Features**
- `qrcode==7.4.2` - QR code generation
- `rich==13.7.1` - Rich text formatting
- `psutil==7.0.0` - System monitoring

### **API Integration**
- `aportalsmp` - Portal API integration
- `tonnelmp` - Tonnel API integration

---

## ✅ **Platform Compatibility**

### **Linux (Ubuntu/Debian/CentOS)**
- ✅ All packages tested and working
- ✅ Pre-compiled wheels available
- ✅ System libraries automatically detected

### **Windows (10/11)**
- ✅ All packages tested and working
- ✅ Pre-compiled wheels available
- ✅ No additional system dependencies

### **macOS**
- ✅ All packages tested and working
- ✅ Compatible with both Intel and Apple Silicon

---

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **1. Permission Errors (Linux)**
```bash
# Use virtual environment instead
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **2. Compilation Errors (Windows)**
```cmd
# Install Visual C++ Build Tools
# Or use pre-compiled wheels (included in requirements)
```

#### **3. SSL Certificate Issues**
```bash
# Update certificates
pip install --upgrade certifi
```

#### **4. tgcrypto Installation Issues**
```bash
# Alternative installation
pip install --no-binary :all: tgcrypto
```

---

## 🧪 **Testing Your Installation**

1. **Run Compatibility Test:**
   ```bash
   python test_requirements_compatibility.py
   ```

2. **Test Bot Functionality:**
   ```bash
   python telegram_bot.py
   ```

3. **Verify CDN Integration:**
   ```bash
   python test_caching_fix.py
   ```

---

## 📊 **Performance Notes**

- **psutil**: Automatically optimizes for your platform
- **curl_cffi**: Uses system SSL libraries
- **python-Levenshtein**: Pre-compiled for speed
- **tgcrypto**: Fast encryption on all platforms

---

## 🎉 **Success Indicators**

✅ **All packages import without errors**  
✅ **Bot starts without dependency issues**  
✅ **CDN integration works correctly**  
✅ **Image processing functions properly**  
✅ **API integrations are functional**  

---

## 📞 **Support**

If you encounter any issues:

1. **Check the compatibility test output**
2. **Verify your Python version (3.8+)**
3. **Ensure you're using a virtual environment**
4. **Check platform-specific troubleshooting**

**Your bot is now ready for both Windows and Linux!** 🚀 