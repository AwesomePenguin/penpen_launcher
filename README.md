# PenPen Launcher

🎮 **A TV-optimized PC gaming launcher designed for living room gaming experiences**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%2011-blue)](https://www.microsoft.com/windows/)
[![Controller](https://img.shields.io/badge/Controller-DS4%2FDS5-red)](https://www.playstation.com/)

## Overview

PenPen Launcher transforms your Windows 11 ITX PC into a console-like gaming experience, perfect for couch gaming with a controller. It provides a unified interface for launching games from multiple platforms while offering console-style features like in-game overlays and seamless controller navigation.

### Key Features

🖥️ **TV-Optimized Interface**
- Large, readable UI elements designed for 4K displays
- Console-style navigation optimized for controllers
- Beautiful, game-focused interface that feels at home in your living room

🎮 **Controller-First Design**
- Deep integration with DualShock 4 and DualSense controllers
- PS button functionality for quick access and power management
- Haptic feedback and LED support for DualSense controllers

🚀 **Multi-Platform Game Management**
- Steam integration for your Steam library
- Epic Games Store support
- Battle.net compatibility
- Custom launcher support (Hoyoverse, etc.)
- Unified game library across all platforms

⚡ **Gaming-Focused Features**
- In-game overlay accessible via PS button
- Quick game switching without returning to desktop
- Screenshot capture and management
- Automatic crash recovery and system monitoring

🛠️ **Robust Architecture**
- Microservices-based design for reliability
- Automatic service recovery and health monitoring
- Cloud logging and monitoring (optional)
- Seamless system updates

## Technology Stack

**Backend Services**
- Python 3.8+ with AsyncIO
- FastAPI for REST APIs and WebSocket communication
- Process management and system monitoring

**Frontend**
- NextJS with WebView2 integration
- Responsive design optimized for TV displays
- Real-time updates via WebSocket connections

**System Integration**
- Windows 11 native APIs
- Controller input management
- Transparent overlay windows
- Cloud storage integration (Cloudflare R2)

## Project Structure

```
penpen_launcher/
├── backend/           # Python services (API, UI, monitoring)
├── frontend/          # NextJS web interface
├── docs/             # User documentation and guides
├── copilot_docs/     # Development context and notes
└── .github/          # GitHub templates and workflows
```

## System Requirements

- **Operating System**: Windows 11 (x64)
- **Controllers**: DualShock 4 or DualSense (PS5)
- **Display**: 1080p+ (4K HDR recommended)
- **Hardware**: ITX/SFF PC or equivalent
- **Software**: Python 3.8+, Node.js LTS

## Development Status

🚧 **This project is currently in active development**

We're building a comprehensive TV gaming launcher that brings console convenience to PC gaming. The architecture is designed, core components are being implemented, and we're working toward an initial release.

### Current Focus
- Core service architecture implementation
- Game library detection and management
- Controller integration and overlay system
- UI development and responsive design

## Architecture Highlights

PenPen Launcher uses a **microservices architecture** where each component runs independently:

- **Core API Service**: Central hub for game management and system coordination
- **Main UI Service**: Primary interface for browsing and managing games
- **Overlay Service**: In-game overlay for quick actions and controls
- **Watchdog Service**: System monitoring and automatic recovery
- **Process Manager**: Service lifecycle and state management

This design ensures that if one component fails, the rest of the system continues operating, providing a robust gaming experience.

## Contributing

We welcome contributions! This project is designed to be:
- **Bilingual**: Supporting both English and Chinese developers
- **Well-Documented**: Comprehensive guides and API documentation
- **Modern**: Using current best practices and technologies

For technical details, see our [development documentation](docs/) and [architecture notes](copilot_docs/).

## Community

- **Issues & Features**: [GitHub Issues](https://github.com/AwesomePenguin/penpen_launcher/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AwesomePenguin/penpen_launcher/discussions)
- **Documentation**: [Project Overview](docs/project_overview.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with ❤️ for the couch gaming community. PenPen Launcher aims to bridge the gap between PC gaming flexibility and console gaming convenience.

---

**Note**: This project is optimized for living room gaming setups and designed specifically for Windows 11 with PlayStation controllers. For technical implementation details, architecture notes, and development guides, please refer to the documentation in the `docs/` and `copilot_docs/` directories.