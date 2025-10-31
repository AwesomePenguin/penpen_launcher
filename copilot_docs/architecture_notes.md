# Architecture Notes - PenPen Launcher

## System Overview

PenPen Launcher is a microservices-based TV gaming launcher designed for Windows 11 ITX systems. The architecture emphasizes process isolation, fault tolerance, and seamless user experience.

## Core Architecture Principles

### 1. Microservices Design
- **Independent Services**: Each component runs as a separate process
- **Fault Isolation**: Single service failure doesn't crash the entire system
- **Resource Management**: Services can be independently restarted and monitored
- **Communication**: WebSocket-based real-time communication between services

### 2. Process Lifecycle Management
```
System Boot → Core API → Watchdog → Main UI → Ready State
    ↓
Game Launch → UI Transition → Overlay Service → Gaming State
    ↓
Game Exit → Cleanup → UI Restore → Ready State
```

### 3. Service Dependencies
```
launcher.py (Entry Point)
    ├── process_manager.py (Orchestrator)
    │   ├── core_api.py (Central Hub)
    │   ├── watchdog_service.py (Monitor)
    │   └── main_ui.py (Primary UI)
    └── overlay_ui.py (Game Overlay - Dynamic)
```

## Detailed Component Architecture

### Core API Service (core_api.py)
**Role**: Central communication hub and system coordinator
**Technology**: FastAPI + WebSocket
**Responsibilities**:
- Game library management
- System state coordination
- WebSocket message routing
- Health check endpoints
- Static file serving (frontend)

**Key Endpoints**:
- `GET /api/games` - Game library
- `POST /api/games/{id}/launch` - Game launching
- `WebSocket /ws/system` - Real-time communication
- `GET /api/system/status` - System state

### Main UI Service (main_ui.py)
**Role**: Primary user interface for browsing and system management
**Technology**: WebView2 + NextJS frontend
**Responsibilities**:
- Game browsing interface
- System settings
- Power management
- Controller navigation

**State Management**:
- Active during browsing state
- Hidden/closed during gaming state
- Auto-restart after game exit

### Overlay UI Service (overlay_ui.py)
**Role**: In-game overlay for quick actions
**Technology**: Transparent WebView2 + Windows API
**Responsibilities**:
- PS button monitoring
- Quick game termination
- Screenshot capture
- Power menu access

**Lifecycle**:
- Created when game launches
- Destroyed when game exits
- Process-specific (monitors parent game PID)

### Watchdog Service (watchdog_service.py)
**Role**: System health monitoring and auto-recovery
**Technology**: AsyncIO-based monitoring loops
**Responsibilities**:
- Process health checks
- Automatic service restart
- Crash detection and logging
- System status reporting

**Monitoring Strategy**:
- HTTP health checks for Core API
- Process existence checks for UI services
- Resource usage monitoring
- Configurable restart limits

### Process Manager (process_manager.py)
**Role**: System lifecycle orchestration
**Technology**: AsyncIO subprocess management
**Responsibilities**:
- Service startup sequencing
- State transition management
- Graceful shutdown coordination
- Emergency recovery procedures

## State Management

### System States
```python
class SystemState(Enum):
    BOOTING = "booting"      # Initial startup
    BROWSING = "browsing"    # Main UI active
    GAMING = "gaming"        # Game running + overlay
    SHUTTING_DOWN = "shutting_down"  # Cleanup phase
```

### State Transitions
- **BOOTING → BROWSING**: All core services started successfully
- **BROWSING → GAMING**: Game launch initiated
- **GAMING → BROWSING**: Game terminated (manual or automatic)
- **ANY → SHUTTING_DOWN**: System shutdown requested

## Communication Architecture

### WebSocket Message Flow
```
Main UI ←→ Core API ←→ Overlay UI
    ↓           ↓           ↓
Watchdog ←→ Log Uploader
```

### Message Types
- `game_launched`: Game startup notification
- `game_terminated`: Game exit notification
- `system_shutdown`: Shutdown command
- `heartbeat`: Service health ping
- `overlay_command`: Overlay control messages

## Data Flow

### Game Launch Sequence
1. User selects game in Main UI
2. Main UI → Core API: Launch request
3. Core API: Start game process
4. Core API → All services: Game launched event
5. Main UI: Hide/minimize
6. Process Manager: Start overlay service
7. System State: BROWSING → GAMING

### Error Recovery Flow
1. Watchdog: Detect service failure
2. Watchdog: Log crash event
3. Watchdog: Attempt service restart
4. If restart fails: Emergency procedures
5. Core API: Broadcast system events

## Windows 11 Integration

### Controller Support
- **DS4/DS5 Detection**: WinAPI + HID integration
- **PS Button Mapping**: Low-level input hooks
- **Haptic Feedback**: DualSense advanced features

### Window Management
- **Transparent Overlays**: Layered windows with alpha blending
- **Fullscreen Coordination**: Game window focus management
- **HDR Support**: Windows 11 HDR pipeline integration

### System Integration
- **Process Priority**: Game process priority management
- **Resource Monitoring**: CPU/Memory usage tracking
- **Power Management**: Shutdown/restart coordination

## Performance Considerations

### Resource Optimization
- **Memory Usage**: Target < 500MB total system memory
- **CPU Usage**: Background services < 5% CPU
- **Startup Time**: System ready in < 10 seconds
- **Game Launch**: < 3 seconds from selection to game start

### Scalability
- **Game Library**: Support 100+ games without performance degradation
- **Concurrent Processes**: Handle multiple background services efficiently
- **Log Management**: Automatic log rotation and cleanup

## Security Architecture

### Process Isolation
- **Separate User Context**: Services run in isolated processes
- **Privilege Separation**: Minimal required permissions per service
- **Input Validation**: All external inputs validated and sanitized

### Data Protection
- **Configuration Security**: Sensitive config in protected files
- **Log Sanitization**: Remove sensitive data from logs
- **Network Security**: Local-only communication by default