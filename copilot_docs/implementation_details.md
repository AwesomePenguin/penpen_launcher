# Implementation Details - PenPen Launcher

## Python Backend Implementation

### Core Dependencies
```python
# requirements.txt (Key Dependencies)
fastapi>=0.104.0          # REST API framework
uvicorn>=0.24.0           # ASGI server
websockets>=12.0          # WebSocket client/server
psutil>=5.9.0             # Process and system monitoring
pywebview>=4.4.0          # WebView2 integration
aiofiles>=23.2.0          # Async file operations
boto3>=1.34.0             # Cloudflare R2 (S3-compatible)
python-dotenv>=1.0.0      # Environment variable management
pydantic>=2.5.0           # Data validation
keyboard>=0.13.5          # Low-level keyboard hooks
pillow>=10.1.0            # Screenshot functionality
```

### Async Programming Patterns

#### Service Base Class Pattern
```python
class BaseService:
    def __init__(self, name: str):
        self.name = name
        self.is_running = False
        self.websocket_client = None
        
    async def start(self):
        """Start the service and establish connections."""
        self.is_running = True
        await self.initialize()
        await self.connect_websocket()
        
    async def stop(self):
        """Gracefully stop the service."""
        self.is_running = False
        await self.cleanup()
        
    async def health_check(self) -> bool:
        """Return service health status."""
        return self.is_running
```

#### WebSocket Communication Pattern
```python
async def websocket_handler(self):
    """Standard WebSocket connection handler."""
    while self.is_running:
        try:
            async with websockets.connect(self.websocket_uri) as websocket:
                await self.register_service(websocket)
                
                async for message in websocket:
                    data = json.loads(message)
                    await self.handle_message(data, websocket)
                    
        except ConnectionClosed:
            logger.warning(f"{self.name}: WebSocket connection lost")
            await asyncio.sleep(5)  # Reconnection delay
        except Exception as e:
            logger.error(f"{self.name}: WebSocket error: {e}")
            await asyncio.sleep(10)
```

### Process Management Implementation

#### Subprocess Creation Pattern
```python
async def create_managed_process(self, command: list, service_name: str):
    """Create a subprocess with proper logging and monitoring."""
    log_file = f"logs/{service_name}.log"
    error_file = f"logs/{service_name}_error.log"
    
    with open(log_file, "a") as stdout, open(error_file, "a") as stderr:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=stdout,
            stderr=stderr,
            cwd=os.getcwd()
        )
    
    self.processes[service_name] = process
    logger.info(f"Started {service_name} (PID: {process.pid})")
    return process
```

#### Process Monitoring Loop
```python
async def monitor_processes(self):
    """Continuously monitor all managed processes."""
    while self.is_monitoring:
        for service_name, process in self.processes.items():
            if process.returncode is not None:
                # Process has exited
                await self.handle_process_exit(service_name, process.returncode)
            
        await asyncio.sleep(self.check_interval)
```

### Windows API Integration

#### Transparent Window Creation
```python
import ctypes
from ctypes import windll, byref
from ctypes.wintypes import HWND, DWORD

def make_window_transparent(hwnd: HWND, alpha: int = 180):
    """Make a window transparent using Windows API."""
    WS_EX_LAYERED = 0x80000
    LWA_ALPHA = 0x2
    
    # Get current extended window style
    ex_style = windll.user32.GetWindowLongW(hwnd, -20)
    
    # Add layered window style
    windll.user32.SetWindowLongW(hwnd, -20, ex_style | WS_EX_LAYERED)
    
    # Set transparency level
    windll.user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
```

#### Controller Input Handling
```python
import keyboard
from typing import Callable

class ControllerManager:
    def __init__(self):
        self.ps_button_callbacks = []
        self.is_monitoring = False
        
    def register_ps_button_handler(self, callback: Callable):
        """Register callback for PS button events."""
        self.ps_button_callbacks.append(callback)
        
    async def start_monitoring(self):
        """Start monitoring controller input."""
        self.is_monitoring = True
        
        def on_ps_button_press():
            for callback in self.ps_button_callbacks:
                asyncio.create_task(callback())
                
        # Register global hotkey (temporary mapping)
        keyboard.add_hotkey('insert', on_ps_button_press)
        
        while self.is_monitoring:
            await asyncio.sleep(0.1)
```

### State Management Implementation

#### State Machine Pattern
```python
from enum import Enum
from typing import Dict, Callable

class SystemState(Enum):
    BOOTING = "booting"
    BROWSING = "browsing"
    GAMING = "gaming"
    SHUTTING_DOWN = "shutting_down"

class StateMachine:
    def __init__(self):
        self.current_state = SystemState.BOOTING
        self.state_handlers: Dict[SystemState, Callable] = {}
        self.transition_callbacks: Dict[tuple, list] = {}
        
    def register_state_handler(self, state: SystemState, handler: Callable):
        """Register handler for specific state."""
        self.state_handlers[state] = handler
        
    async def transition_to(self, new_state: SystemState):
        """Transition to new state with callbacks."""
        old_state = self.current_state
        
        # Execute transition callbacks
        transition_key = (old_state, new_state)
        if transition_key in self.transition_callbacks:
            for callback in self.transition_callbacks[transition_key]:
                await callback(old_state, new_state)
                
        self.current_state = new_state
        
        # Execute new state handler
        if new_state in self.state_handlers:
            await self.state_handlers[new_state]()
```

### Error Handling Patterns

#### Graceful Degradation
```python
async def safe_service_call(self, service_func, fallback_func=None):
    """Call service function with graceful degradation."""
    try:
        return await service_func()
    except ServiceUnavailableError:
        logger.warning("Service unavailable, using fallback")
        if fallback_func:
            return await fallback_func()
        return None
    except Exception as e:
        logger.error(f"Service call failed: {e}")
        await self.handle_service_error(e)
        return None
```

#### Retry with Exponential Backoff
```python
async def retry_with_backoff(self, func, max_retries=3, base_delay=1):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s")
            await asyncio.sleep(delay)
```

### Logging Implementation

#### Structured Logging Setup
```python
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'service': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
            
        return json.dumps(log_data, ensure_ascii=False)

def setup_logging(service_name: str, log_level=logging.INFO):
    """Setup structured logging for a service."""
    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        f'logs/{service_name}.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(StructuredFormatter())
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

### Configuration Management

#### Environment Configuration
```python
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Core API Settings
    core_api_port: int = 8000
    core_api_host: str = "localhost"
    
    # Logging Settings
    log_level: str = "INFO"
    upload_logs: bool = False
    
    # Cloudflare R2 Settings
    r2_access_key_id: Optional[str] = None
    r2_secret_access_key: Optional[str] = None
    r2_endpoint_url: Optional[str] = None
    r2_bucket_name: Optional[str] = None
    
    # System Settings
    max_restart_count: int = 3
    health_check_interval: int = 5
    websocket_timeout: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
```

## Frontend Implementation

### NextJS Architecture

#### Component Structure
```
frontend/
├── components/
│   ├── ui/              # Reusable UI components
│   ├── game/            # Game-specific components
│   ├── navigation/      # Controller navigation
│   └── system/          # System management
├── pages/
│   ├── index.tsx        # Main game library
│   ├── settings.tsx     # System settings
│   └── api/             # API route handlers
├── hooks/
│   ├── useGamepad.ts    # Controller input hook
│   ├── useWebSocket.ts  # WebSocket connection hook
│   └── useSystemState.ts # System state management
└── styles/
    ├── globals.css      # Global styles
    └── tv-optimized.css # TV-specific styling
```

#### Controller Navigation Hook
```typescript
// hooks/useGamepad.ts
import { useEffect, useState } from 'react';

interface GamepadState {
  connected: boolean;
  buttons: boolean[];
  axes: number[];
}

export function useGamepad() {
  const [gamepad, setGamepad] = useState<GamepadState | null>(null);
  
  useEffect(() => {
    let animationId: number;
    
    function updateGamepad() {
      const gamepads = navigator.getGamepads();
      const pad = gamepads[0];
      
      if (pad) {
        setGamepad({
          connected: true,
          buttons: Array.from(pad.buttons).map(b => b.pressed),
          axes: Array.from(pad.axes)
        });
      } else {
        setGamepad(null);
      }
      
      animationId = requestAnimationFrame(updateGamepad);
    }
    
    updateGamepad();
    
    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, []);
  
  return gamepad;
}
```

### Build Configuration

#### next.config.js
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  distDir: 'out',
  images: {
    unoptimized: true
  },
  experimental: {
    esmExternals: false
  }
}

module.exports = nextConfig
```

## Database/Storage Implementation

### Local Data Storage
- **Game Library**: JSON files in `data/` directory
- **User Settings**: JSON configuration files
- **Game Metadata**: Cached game information
- **Screenshots**: PNG files in `screenshots/` directory

### Cloud Storage Integration
```python
# log_uploader.py implementation details
class CloudflareR2Client:
    def __init__(self, settings: Settings):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            endpoint_url=settings.r2_endpoint_url
        )
        self.bucket_name = settings.r2_bucket_name
        
    async def upload_log_file(self, file_path: str):
        """Upload log file to Cloudflare R2."""
        object_key = f"logs/{datetime.now().strftime('%Y/%m/%d')}/{os.path.basename(file_path)}"
        
        async with aiofiles.open(file_path, 'rb') as file:
            content = await file.read()
            
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=content,
            ContentType='text/plain'
        )
```