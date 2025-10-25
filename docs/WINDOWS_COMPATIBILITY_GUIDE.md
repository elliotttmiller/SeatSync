# Windows Compatibility Guide - SeatSync Scraping Service

## Overview

The SeatSync scraping service has been fully optimized for Windows compatibility. This guide explains the Windows-specific features, configurations, and optimizations implemented to ensure seamless operation on Windows platforms.

## Windows-Specific Features

### 1. Event Loop Policy Configuration

**Issue**: Windows uses `ProactorEventLoop` by default, which has limitations with subprocess operations.

**Solution**: Automatic detection and configuration of `WindowsSelectorEventLoopPolicy`.

```python
# Automatically applied on Windows systems
if IS_WINDOWS:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

**Benefits**:
- Eliminates `NotImplementedError` exceptions
- Proper subprocess handling for browser automation
- Compatible with Playwright/Camoufox operations

### 2. Windows-Native Browser Priority

**Feature**: On Windows, the scraper prioritizes Windows-native browsers (Chrome, Edge).

```python
WINDOWS_PREFERRED_BROWSERS = [
    'chrome136',    # Latest Chrome
    'chrome133a',   # Chrome stable
    'chrome131',    # Chrome LTS
    'edge101',      # Microsoft Edge (Windows-native)
    'chrome124',    # Chrome compatibility
    'chrome123',    # Chrome fallback
]
```

**Behavior**:
- 70% chance to use Windows-preferred browsers
- 30% chance to use any browser for variety
- Optimizes for Windows-native browser fingerprints

### 3. Extended Timeouts for Windows

**Reason**: Windows file I/O and disk operations can be slower than Unix systems.

```python
AWS_WAF_CONFIG = {
    "initial_wait": 10 if IS_WINDOWS else 8,  # +2 seconds on Windows
    "max_wait": 35 if IS_WINDOWS else 30,     # +5 seconds on Windows
    "retry_attempts": 5,
    "backoff_factor": 1.5,
}
```

**Impact**:
- More reliable AWS WAF challenge handling
- Better success rate on slower systems
- Accommodates Windows Defender scanning overhead

### 4. ThreadPoolExecutor with Named Threads

**Configuration**:
```python
_executor = ThreadPoolExecutor(
    max_workers=4, 
    thread_name_prefix='scrapling_worker'
)
```

**Benefits**:
- Clear thread identification in Windows Task Manager
- Better debugging on Windows systems
- Proper thread isolation from event loop

### 5. Platform Detection Display

**Streamlit UI**: Shows Windows-optimized status

```python
# Sidebar shows: 🪟 Windows-optimized
# Scraping page shows: Windows-Optimized: Enhanced event loop handling
```

**Visual Indicators**:
- 🪟 Windows icon in UI
- "Windows-optimized configuration active" in logs
- Platform-specific messaging throughout

## Windows Compatibility Checks

### Automatic Detection

The service automatically detects Windows on startup:

```python
import platform

IS_WINDOWS = platform.system() == 'Windows'
```

No configuration needed - works automatically!

### Verification

Check Windows features are active:

```python
from app.services.scrapling_scraper import ScraplingScraperService

service = ScraplingScraperService()
print(f"Windows mode: {service.is_windows}")  # True on Windows
```

## Windows Installation Guide

### Prerequisites

1. **Python 3.8+** (Python 3.11+ recommended)
2. **Windows 10 or Windows 11**
3. **Administrator rights** (for package installation)

### Installation Steps

```powershell
# 1. Clone repository
git clone https://github.com/elliotttmiller/SeatSync.git
cd SeatSync

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Install Streamlit dependencies
pip install streamlit plotly

# 5. Verify installation
python -c "from backend.app.services.scrapling_scraper import IS_WINDOWS; print(f'Windows detected: {IS_WINDOWS}')"
```

### Running on Windows

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Run Streamlit app
streamlit run streamlit_app.py

# The app will automatically:
# - Detect Windows
# - Configure WindowsSelectorEventLoopPolicy
# - Use Windows-preferred browsers
# - Apply extended timeouts
```

## Windows-Specific Configurations

### Browser Preferences

The service automatically prioritizes browsers based on platform:

| Platform | Preferred Browsers | Reason |
|----------|-------------------|--------|
| Windows | Chrome, Edge | Native to Windows, better fingerprints |
| Linux | Chrome, Firefox | Common Linux browsers |
| macOS | Chrome, Safari | Native to macOS |

### Timeout Adjustments

| Operation | Linux/Mac | Windows | Reason |
|-----------|-----------|---------|--------|
| Initial Wait | 8s | 10s | Windows Defender overhead |
| Max Wait | 30s | 35s | Slower disk I/O |
| Fetch Timeout | 150s | 150s | Same (network-based) |

### Thread Configuration

```python
# Thread pool sized for typical Windows systems
max_workers = 4  # One per marketplace

# Named threads for easy identification
thread_name_prefix = 'scrapling_worker'
```

View threads in Task Manager → Details → right-click columns → Select "Thread Count"

## Troubleshooting Windows Issues

### Issue 1: NotImplementedError

**Symptom**: `NotImplementedError` when scraping

**Solution**: Already fixed! The service uses `WindowsSelectorEventLoopPolicy`.

**Verification**:
```python
import asyncio
policy = asyncio.get_event_loop_policy()
print(type(policy).__name__)  # Should show WindowsSelectorEventLoopPolicy
```

### Issue 2: Slow Scraping

**Symptom**: Scraping takes longer than expected

**Reason**: Windows Defender may scan downloaded content

**Solutions**:
1. Add exclusion for Python working directory in Windows Defender
2. Extended timeouts already configured (10s initial, 35s max)
3. Disable real-time protection temporarily (not recommended for production)

**Add Exclusion**:
```powershell
# Run as Administrator
Add-MpPreference -ExclusionPath "C:\path\to\SeatSync"
```

### Issue 3: Browser Launch Fails

**Symptom**: Browser fails to launch during scraping

**Possible Causes**:
- Antivirus blocking browser executable
- Insufficient permissions
- Missing browser binaries

**Solutions**:
```powershell
# 1. Install scrapling browser components
python -m scrapling install

# 2. Run as Administrator (if needed)
# Right-click Python script → Run as Administrator

# 3. Check Windows Firewall settings
# Allow Python through Windows Firewall
```

### Issue 4: Memory Usage High

**Symptom**: High memory usage during scraping

**Reason**: 4 concurrent browser instances (one per marketplace)

**Expected Usage**: ~200-400MB per browser = 800-1600MB total

**Solutions**:
- Normal behavior, no action needed
- Close other applications during heavy scraping
- Upgrade RAM if consistently running out (8GB+ recommended)

## Performance Optimization for Windows

### 1. Disable Windows Defender for Project Directory

**Warning**: Only for development, not production!

```powershell
# Add exclusion (Run as Administrator)
Add-MpPreference -ExclusionPath "C:\path\to\SeatSync"

# Verify exclusion
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

### 2. Use SSD for Better Performance

- Scraping involves disk I/O for browser cache
- SSD significantly improves performance
- HDD acceptable but slower

### 3. Close Background Applications

- Browser automation is resource-intensive
- Close unnecessary applications
- Keep Task Manager open to monitor

### 4. Windows Power Settings

```powershell
# Set to High Performance mode
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Verify
powercfg /getactivescheme
```

## Windows-Specific Logs

When running on Windows, you'll see:

```
✅ Windows detected - Using WindowsSelectorEventLoopPolicy for optimal compatibility
✅ Scrapling scraper initialized with full stealth mode (v0.3.7) - Windows-optimized configuration active
```

## Comparison: Windows vs Linux/Mac

### Event Loop

| Feature | Windows | Linux/Mac |
|---------|---------|-----------|
| Default Policy | ProactorEventLoop | SelectorEventLoop |
| Our Configuration | WindowsSelectorEventLoopPolicy | Default (no change) |
| Subprocess Support | ✅ With our fix | ✅ Native |

### Browser Priority

| Platform | Primary | Secondary |
|----------|---------|-----------|
| Windows | Chrome, Edge | Firefox, Safari |
| Linux | Chrome, Firefox | Safari, Edge |
| macOS | Chrome, Safari | Firefox, Edge |

### Timeouts

| Platform | Initial | Max | Reason |
|----------|---------|-----|--------|
| Windows | 10s | 35s | Defender overhead |
| Linux | 8s | 30s | Faster I/O |
| macOS | 8s | 30s | Faster I/O |

## Testing on Windows

Run the test suite to verify Windows compatibility:

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Run tests
python -m pytest backend/tests/test_scrapling_scraper.py -v

# Expected output:
# ✅ All 5 tests passing
# ✅ Windows-specific features active
```

## Windows-Specific Features Summary

✅ **Automatic Windows Detection**
- No configuration required
- Detects Windows on import
- Applies optimizations automatically

✅ **WindowsSelectorEventLoopPolicy**
- Eliminates NotImplementedError
- Proper subprocess handling
- Compatible with browser automation

✅ **Windows-Native Browser Priority**
- 70% Chrome/Edge on Windows
- Realistic Windows fingerprints
- Better anti-detection

✅ **Extended Timeouts**
- +2 seconds initial wait
- +5 seconds max wait
- Accommodates Windows Defender

✅ **Named Threads**
- Easy identification in Task Manager
- Better debugging
- Clean thread management

✅ **UI Indicators**
- 🪟 Windows icon in Streamlit
- Platform status display
- "Windows-optimized" messaging

✅ **Comprehensive Logging**
- Windows-specific log messages
- Platform detection in logs
- Enhanced debugging information

## Best Practices for Windows

1. **Use Latest Python**: Python 3.11+ recommended for Windows
2. **Run as Administrator**: Only if needed for browser installation
3. **SSD Recommended**: Better performance with disk-intensive operations
4. **Close Background Apps**: Browser automation uses significant resources
5. **Monitor Task Manager**: Check memory/CPU during scraping
6. **Add AV Exclusions**: For development directories (optional)
7. **High Performance Mode**: Better consistency in timing-sensitive operations

## Conclusion

The SeatSync scraping service is **fully optimized for Windows** with:

- ✅ Automatic Windows detection
- ✅ Proper event loop configuration
- ✅ Windows-native browser priority
- ✅ Extended timeouts for Windows
- ✅ Named threads for debugging
- ✅ Clear UI indicators
- ✅ Comprehensive documentation

No additional configuration needed - just install and run! The service automatically detects Windows and applies all optimizations.

---

**Supported Windows Versions**: Windows 10, Windows 11
**Minimum Python**: 3.8+ (3.11+ recommended)
**Status**: ✅ Production-Ready on Windows
