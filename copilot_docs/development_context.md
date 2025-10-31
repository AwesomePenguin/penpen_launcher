# Development Context - PenPen Launcher

## Project Background

### Vision and Goals
PenPen Launcher aims to bring console-like gaming experience to PC gaming in a living room environment. The project focuses on:

- **TV-Optimized Interface**: Large, readable UI elements suitable for couch gaming
- **Controller-First Navigation**: Seamless DS4/DS5 controller integration
- **Unified Game Management**: Single interface for Steam, Epic, Battle.net, and custom launchers
- **Console-Like Experience**: Quick game switching, overlay functionality, and power management

### Target User Profile
- **Primary Users**: PC gamers using living room/TV setups
- **Use Case**: Couch gaming with wireless controllers
- **Technical Level**: End users who want console simplicity with PC gaming flexibility
- **Hardware**: Windows 11 ITX/small form factor PCs connected to TVs

## Development Environment Context

### Current Development Setup
- **OS**: Windows 11 (development and target platform)
- **Python**: 3.8+ for backend services
- **Node.js**: Latest LTS for frontend development
- **Git**: GitHub repository for version control
- **IDE**: VS Code recommended for development

### Target Deployment Environment
- **Hardware**: ITX form factor PC
- **OS**: Windows 11 (exclusive target)
- **Controllers**: DualShock 4 and DualSense controllers
- **Display**: 4K TV with HDR support
- **Network**: Home network (no internet required for core functionality)

## Technical Decisions and Rationale

### Architecture Decisions

#### Microservices Architecture
**Decision**: Split functionality into separate processes  
**Rationale**: 
- Fault isolation (one component failure doesn't crash everything)
- Independent scaling and resource management
- Easier debugging and development
- Service-specific optimization

#### WebSocket Communication
**Decision**: Use WebSocket for inter-service communication  
**Rationale**:
- Real-time updates for UI state changes
- Bidirectional communication
- Low latency for gaming responsiveness
- Easy to implement and debug

#### WebView2 for UI
**Decision**: Use WebView2 + NextJS instead of native Windows UI  
**Rationale**:
- Rapid UI development with web technologies
- Consistent styling and responsive design
- Easy to implement controller navigation
- Better maintainability than native UI frameworks

### Technology Stack Decisions

#### Python Backend
**Decision**: Python with AsyncIO for all backend services  
**Rationale**:
- Excellent async support for concurrent operations
- Rich ecosystem for system integration (psutil, keyboard, etc.)
- Good Windows API bindings
- Rapid development and prototyping

#### NextJS Frontend
**Decision**: NextJS with static export for frontend  
**Rationale**:
- Server-side rendering for better performance
- Built-in optimization features
- Easy deployment with static export
- Good TypeScript support for controller APIs

#### Cloudflare R2 for Logs
**Decision**: Use Cloudflare R2 for cloud log storage  
**Rationale**:
- S3-compatible API (familiar interface)
- Cost-effective for small amounts of log data
- Good performance and reliability
- No vendor lock-in (can switch to other S3-compatible services)

## Development Workflow

### Code Organization Philosophy
- **Separation of Concerns**: Each service has a single, well-defined responsibility
- **Minimal Dependencies**: Services should be as independent as possible
- **Configuration-Driven**: Behavior controlled through environment variables and config files
- **Defensive Programming**: Assume services will fail and design for recovery

### Testing Strategy
- **Unit Testing**: Focus on business logic and core algorithms
- **Integration Testing**: Test service communication and system interactions
- **Manual Testing**: Controller navigation and user experience validation
- **Performance Testing**: Resource usage and responsiveness under load

### Error Handling Philosophy
- **Graceful Degradation**: System should continue working even if non-critical services fail
- **Comprehensive Logging**: All errors and important events should be logged
- **Auto-Recovery**: Services should automatically restart after crashes when possible
- **User Feedback**: Clear indication of system status and any issues

## Design Constraints and Trade-offs

### Performance Constraints
- **Memory Usage**: Target maximum 500MB total system memory
- **CPU Usage**: Background services should use <5% CPU when idle
- **Startup Time**: System should be ready within 10 seconds of launch
- **Game Launch Time**: Maximum 3 seconds from selection to game start

### Windows 11 Specific Considerations
- **HDR Support**: Must properly handle HDR displays and color spaces
- **Window Management**: Proper handling of fullscreen games and overlay windows
- **Controller Integration**: Deep integration with Windows 11 controller APIs
- **Power Management**: Integration with Windows power management features

### Security Considerations
- **Process Isolation**: Services run with minimal required privileges
- **Input Validation**: All external inputs validated to prevent injection attacks
- **Configuration Security**: Sensitive configuration stored securely
- **Network Security**: Local-only communication by default

## Future Considerations

### Scalability Concerns
- **Game Library Size**: System should handle 100+ games without performance issues
- **Multiple Controllers**: Support for multiple simultaneous controllers
- **Network Features**: Potential for remote game streaming or management
- **Plugin System**: Architecture should support future plugin/extension system

### Maintenance Considerations
- **Automated Updates**: Self-updating system with rollback capability
- **Remote Monitoring**: Optional telemetry for system health monitoring
- **Backup/Restore**: Configuration and save data backup systems
- **Documentation**: Comprehensive user and developer documentation

## Development Milestones

### Phase 1: Core Infrastructure
- [x] Project structure and documentation
- [ ] Basic service architecture implementation
- [ ] Inter-service communication setup
- [ ] Process management and monitoring

### Phase 2: Basic UI and Game Management
- [ ] NextJS frontend with basic navigation
- [ ] Game library detection and management
- [ ] Basic game launching functionality
- [ ] Controller input integration

### Phase 3: Advanced Features
- [ ] Overlay system implementation
- [ ] Power management integration
- [ ] Cloud logging and monitoring
- [ ] Update system implementation

### Phase 4: Polish and Optimization
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] User experience refinements
- [ ] Documentation completion

## Integration Points

### Game Launcher Integration
- **Steam**: Use Steam CLI and registry detection
- **Epic Games Store**: Parse Epic's launcher database
- **Battle.net**: Monitor Battle.net installation directories
- **Custom Launchers**: File system monitoring and executable detection

### Windows System Integration
- **Controller Drivers**: Direct integration with Windows controller APIs
- **Display Management**: Integration with Windows display settings APIs
- **Power Management**: Use Windows power management APIs for shutdown/restart
- **Process Management**: Leverage Windows process management and monitoring APIs

## Known Limitations

### Current Limitations
- Windows 11 only (no backward compatibility planned)
- DS4/DS5 controllers only (no Xbox controller support initially)
- English/Chinese UI only (no other language support planned)
- Single-user system (no multi-user support)

### Future Limitation Considerations
- Network dependency for cloud features only
- Limited customization options (focus on simplicity)
- No support for legacy games requiring specific compatibility layers
- No support for VR or specialized gaming hardware