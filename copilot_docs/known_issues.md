# Known Issues - Quick Notes

*This file serves as a quick note area for AI assistants to jot down issues that need attention during task execution. For full issue tracking, use GitHub Issues at: https://github.com/AwesomePenguin/penpen_launcher/issues*

## Purpose
- **Quick Notes**: Temporary holding for issues discovered during other tasks
- **Task Continuity**: Prevent task interruption while noting important problems
- **Reminder System**: Ensure issues aren't forgotten after completing current work

## Workflow
1. **During Task A**: If Task B issue is discovered → Note it here briefly
2. **Continue Task A**: Don't get distracted by Task B
3. **Complete Task A**: Review this file and remind user of pending issues
4. **Address Task B**: Create proper GitHub Issue for detailed tracking

---

## Current Quick Notes

### [CRITICAL] Process Management - Steam URL launcher returns incorrect process IDs
- **Discovered during**: Phase 3 game launch integration testing with Wallpaper Engine
- **Quick note**: Steam URL protocol (`steam://rungameid/431960`) creates temporary `cmd.exe` processes, returning their PIDs instead of actual game process PIDs. This causes tracking issues for background applications like Wallpaper Engine that have persistent services.
- **Behavior observed**: 
  - First launch triggers Steam client startup and auto-update process
  - Subsequent launches return different PIDs each time (cmd.exe processes)
  - Wallpaper Engine background service remains running with same PID (19452)
  - Launch endpoint can't properly track actual game processes
- **Next step**: Implement process discovery after Steam launch to find actual game processes

### [HIGH] Steam Integration - Process tracking for background/service games
- **Discovered during**: Wallpaper Engine launch testing
- **Quick note**: Some Steam games (Wallpaper Engine, overlay apps) run as background services. Current launcher assumes 1:1 mapping between launch command and game process, but Steam games may have complex process hierarchies.
- **Next step**: Enhance process tracking to discover actual game processes after Steam launch
- **Discovered during**: Phase 2 system status integration testing
- **Quick note**: System status (CPU, memory, storage) currently uses 10-second polling. WebSocket would provide real-time updates and reduce API overhead for frequently changing data.
- **Next step**: Implement WebSocket broadcasting for system status updates

### [ENHANCEMENT] System Status - Enhanced visualizations
- **Discovered during**: Phase 2 system status integration testing  
- **Quick note**: Current system status shows text-based percentages. Could add progress bars, charts, or visual indicators for better TV/controller interface experience.
- **Next step**: Design and implement visual system status components (progress bars, mini charts)

### [MEDIUM] Steam Scanner - Limited metadata from VDF-only scanning
- **Discovered during**: Backend-frontend integration testing
- **Quick note**: Current Steam scanner only uses local VDF files, missing rich metadata (images, descriptions, play time, last played). Only returns basic info: name, app_id, install_dir, executable_path.
- **Next step**: Implement Steam Store API integration for enhanced metadata (no API key required)
- **Supporting docs**: See detailed analysis in `copilot_docs/supporting_docs/steam_data_sources_analysis.md`

### [LOW] Frontend - Next.js image hostname configuration needs restart
- **Discovered during**: Frontend integration testing  
- **Quick note**: Updated next.config.ts to allow arbitrary image hosts, but requires frontend server restart to take effect
- **Next step**: Document in deployment notes that config changes require restart

---

## Issue Format
When adding quick notes, use this simple format:

```
### [PRIORITY] Component - Brief Description
- **Discovered during**: [Current task context]
- **Quick note**: [Brief description of the issue]
- **Next step**: [Create GitHub issue / investigate / etc.]
```

**Example:**
```
### [HIGH] Core API - WebSocket connection drops unexpectedly
- **Discovered during**: Frontend integration testing
- **Quick note**: WebSocket connections dropping after 30 seconds of inactivity
- **Next step**: Create GitHub issue with detailed investigation
```

---

## Maintenance
- **Clear after action**: Remove notes once proper GitHub issues are created
- **Keep it brief**: This is for quick notes, not detailed analysis
- **Regular cleanup**: Review and clear resolved items weekly