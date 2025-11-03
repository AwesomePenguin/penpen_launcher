# Backend-Frontend Integration Strategy
*Created: 2025-11-03*

## 🎯 Integration Goal
Connect the working backend (real Steam game data) with the complete frontend (TV-optimized UI) to create a fully functional PenPen Launcher.

## 📊 Current Status
- **Backend**: ✅ MVP complete, 1 real Steam game detected, all 7 core modules working
- **Frontend**: ✅ Complete UI framework with mock data (6 sample games)
- **Target**: Replace frontend mock data with real backend API calls

## 🗺️ 4-Phase Integration Plan

### Phase 1: Basic API Connection (30 min)
**Goal**: Replace mock data with real game data

**Steps**:
1. **Start Backend**: `python launcher.py --debug --port 8000`
2. **Test API**: `curl http://localhost:8000/api/games`
3. **Create API Service**: `frontend/src/services/api.ts`
4. **Update Frontend**: Replace mock data in `pages/index.tsx`

**Success**: Frontend shows 1 real Steam game instead of 6 mock games

### Phase 2: System Status Integration (20 min)
**Goal**: Real system monitoring in header

**Steps**:
1. **System API**: Add `fetchSystemStatus()` to API service
2. **Update Header**: Show real CPU/memory/storage data
3. **Connection Status**: Real "系统在线" indicator

**Success**: Header displays actual system resource usage

### Phase 3: Game Launch Integration (30 min)
**Goal**: Actually launch games from frontend

**Steps**:
1. **Launch API**: Add `launchGame(gameId)` function
2. **Update GameCard**: Connect "启动游戏" button to real backend
3. **Launch States**: Show launching/success/error states

**Success**: Clicking game card actually launches Steam game

### Phase 4: Real-time WebSocket (20 min)
**Goal**: Live system updates

**Steps**:
1. **WebSocket Client**: `ws://localhost:8000/ws`
2. **Real-time Updates**: System stats update without refresh
3. **Game Events**: Launch/exit notifications via WebSocket

**Success**: Live system monitoring and game event notifications

## 🔧 Technical Implementation Notes

### API Endpoints
```
GET  /api/games           # Game library
GET  /api/system/status   # System resources
POST /api/games/{id}/launch # Launch game
WS   /ws                  # Real-time events
```

### Development Servers
```powershell
# Terminal 1: Backend
cd backend
python launcher.py --debug --port 8000

# Terminal 2: Frontend
cd frontend/penpen-launcher-frontend
npm run dev
```

### Data Model Compatibility
- Backend Pydantic models ↔ Frontend TypeScript interfaces
- Already designed for 1:1 mapping
- CORS pre-configured for `localhost:3000`

## 🚦 Priority Order
1. **HIGH**: Game list API (Phase 1)
2. **HIGH**: Game launch (Phase 3) 
3. **MEDIUM**: System status (Phase 2)
4. **MEDIUM**: WebSocket real-time (Phase 4)

## 🎯 Success Criteria
- [ ] Frontend displays real Steam game data
- [ ] System header shows actual CPU/memory usage
- [ ] Game launch button starts real Steam game
- [ ] Real-time system monitoring works
- [ ] WebSocket game events display

## 🐛 Known Issues to Address
- Backend logging directory creation (needs file handler fix)
- CORS verification needed
- Error handling for API failures
- Loading states during API calls

## 📝 Next Actions
1. Fix backend logging file creation issue
2. Start backend API server
3. Test API endpoints manually
4. Begin Phase 1 frontend integration

---
*This is a living document - update as integration progresses*