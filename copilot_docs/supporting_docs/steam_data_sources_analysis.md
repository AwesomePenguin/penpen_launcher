# Steam Data Sources Analysis

*Supporting documentation for Steam Scanner enhancement*

## Overview

This document analyzes the different data sources available for Steam game metadata and outlines implementation strategies for enhanced game information.

## Current Implementation Status

**Current Approach**: VDF Files Only (Basic)
- ✅ **Working**: Local Steam manifest parsing (`appmanifest_*.acf`)
- ✅ **Data Available**: App ID, game name, install directory, installation status
- ❌ **Missing**: Images, descriptions, developer info, play time, last played

## Data Source Hierarchy

### Level 1: Local VDF Files (Current Implementation)
**Location**: `steamapps/appmanifest_*.acf`
**Pros**: 
- Fast access (local files)
- No API dependencies
- Always available offline
- Reliable installation status

**Cons**: 
- Very limited metadata
- No images or rich descriptions
- No user statistics

**Available Data**:
```python
{
    "id": "steam_431960",
    "name": "Wallpaper Engine",           # ✅ Available
    "executable_path": "C:/Steam/...",    # ✅ Available  
    "is_installed": True,                 # ✅ Available
    "description": "Steam 游戏 - ...",     # ⚠️  Generic fallback
    "developer": "Unknown",               # ❌ Missing
    "image_url": "",                      # ❌ Missing
    "last_played": None,                  # ❌ Missing
    "play_time": 0                        # ❌ Missing
}
```

### Level 2: Steam Store API (Recommended Enhancement)
**Endpoint**: `https://store.steampowered.com/api/appdetails`
**Authentication**: None required (public API)
**Rate Limits**: ~200 requests/5 minutes per IP

**Pros**:
- Rich store metadata
- No API key required
- Chinese localization support
- Game images and descriptions

**Cons**:
- Rate limited
- Network dependency
- Some games may not be available

**Available Data**:
```python
{
    "name": "Wallpaper Engine",
    "short_description": "Use stunning live wallpapers...",
    "header_image": "https://steamcdn-a.akamaihd.net/steam/apps/431960/header.jpg",
    "developers": ["Kristjan Skutta"],
    "publishers": ["Kristjan Skutta"],
    "release_date": {"date": "Nov 2, 2016"},
    "categories": [{"id": 2, "description": "Single-player"}],
    "genres": [{"id": "52", "description": "Software"}]
}
```

**Example Request**:
```
GET https://store.steampowered.com/api/appdetails?appids=431960&l=schinese
```

### Level 3: Steam Web API (Full Enhancement)
**Endpoint**: `https://api.steampowered.com`
**Authentication**: Steam API key required
**Rate Limits**: 100,000 calls/day

**Pros**:
- User-specific statistics
- Play time and last played
- Comprehensive user data
- Achievement information

**Cons**:
- Requires Steam API key setup
- User authentication complexity
- Privacy considerations

**Available Data**:
```python
{
    "appid": 431960,
    "name": "Wallpaper Engine",
    "playtime_forever": 120,              # Total play time in minutes
    "rtime_last_played": 1635724800,      # Unix timestamp
    "playtime_2weeks": 30                 # Recent play time
}
```

**Required Setup**:
1. Steam API key from https://steamcommunity.com/dev/apikey
2. Steam User ID discovery
3. User authentication flow

### Level 4: Local User Data (Advanced)
**Location**: `userdata/{user_id}/config/localconfig.vdf`
**Authentication**: None (local files)

**Pros**:
- Most complete user statistics
- Offline access to user data
- Real-time play session info

**Cons**:
- Complex VDF parsing
- User-specific file locations
- Potential privacy concerns

## Implementation Strategy

### Phase 1: Keep Simple (Current)
**Status**: ✅ Implemented
**Scope**: VDF-only scanning
**Benefits**: Fast, reliable, MVP-ready

### Phase 2: Add Store API (Recommended Next Step)
**Status**: 📋 Planned
**Scope**: Enhanced metadata without user data
**Implementation**:

```python
async def enhance_with_store_api(game_info: GameInfo) -> GameInfo:
    """Enhance basic game info with Steam Store API data"""
    app_id = game_info.id.replace("steam_", "")
    
    async with aiohttp.ClientSession() as session:
        url = "https://store.steampowered.com/api/appdetails"
        params = {"appids": app_id, "l": "schinese"}
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if app_id in data and data[app_id]["success"]:
                    store_data = data[app_id]["data"]
                    
                    # Merge store data with basic info
                    return GameInfo(
                        **game_info.dict(),
                        description=store_data.get("short_description", game_info.description),
                        developer=store_data.get("developers", [None])[0],
                        image_url=store_data.get("header_image", ""),
                        release_date=store_data.get("release_date", {}).get("date"),
                        tags=game_info.tags + [g["description"] for g in store_data.get("genres", [])]
                    )
    
    return game_info  # Return original if API fails
```

### Phase 3: Add Web API (Future Enhancement)
**Status**: 📋 Future
**Scope**: User statistics and play data
**Requirements**: Steam API key, user authentication

## Category Mapping

Steam uses a different category system than our simplified enum. Mapping strategy:

```python
def map_steam_category(genres: list) -> GameCategory:
    """Map Steam genres to our category system"""
    for genre in genres:
        name = genre.get("description", "").lower()
        if "action" in name:
            return GameCategory.ACTION
        elif "rpg" in name or "role-playing" in name:
            return GameCategory.RPG
        elif "strategy" in name:
            return GameCategory.STRATEGY
        elif "adventure" in name:
            return GameCategory.ADVENTURE
        elif "simulation" in name:
            return GameCategory.SIMULATION
        elif "sports" in name:
            return GameCategory.SPORTS
    
    return GameCategory.OTHER
```

## Error Handling Strategy

```python
async def safe_steam_api_call(app_id: str) -> dict:
    """Make resilient Steam API calls with proper error handling"""
    try:
        # API call implementation
        pass
    except aiohttp.ClientError:
        logger.warning(f"Network error for Steam API (App {app_id})")
        return {}
    except asyncio.TimeoutError:
        logger.warning(f"Timeout for Steam API (App {app_id})")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error for Steam API (App {app_id}): {e}")
        return {}
```

## Rate Limiting Strategy

```python
import asyncio
from datetime import datetime, timedelta

class SteamApiRateLimiter:
    def __init__(self, max_requests=180, time_window=300):  # 180 req/5min
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Wait if necessary to respect rate limits"""
        now = datetime.now()
        
        # Remove old requests outside time window
        self.requests = [req for req in self.requests 
                        if (now - req).total_seconds() < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0]).total_seconds()
            await asyncio.sleep(wait_time)
        
        self.requests.append(now)
```

## Testing Strategy

### Unit Tests
- VDF parsing with mock files
- API response parsing with mock data
- Category mapping logic
- Error handling scenarios

### Integration Tests
- Real Steam API calls (with rate limiting)
- End-to-end game discovery
- Fallback behavior when APIs fail

### Test Data
```python
WALLPAPER_ENGINE_STORE_RESPONSE = {
    "431960": {
        "success": True,
        "data": {
            "name": "Wallpaper Engine",
            "steam_appid": 431960,
            "short_description": "Use stunning live wallpapers on your desktop.",
            "header_image": "https://steamcdn-a.akamaihd.net/steam/apps/431960/header.jpg",
            "developers": ["Kristjan Skutta"],
            "publishers": ["Kristjan Skutta"],
            "release_date": {"date": "Nov 2, 2016"},
            "genres": [{"id": "52", "description": "Software"}]
        }
    }
}
```

## Migration Path

1. **Current**: VDF-only implementation working
2. **Phase 2**: Add Store API as optional enhancement layer
3. **Phase 3**: Add Web API with user authentication
4. **Phase 4**: Local user data parsing for offline user stats

## Configuration Options

```python
# Environment variables for Steam API enhancement
STEAM_API_KEY=your_steam_api_key_here          # Optional: for user data
STEAM_STORE_API_ENABLED=true                   # Enable store API calls
STEAM_API_RATE_LIMIT=180                       # Requests per 5 minutes
STEAM_API_TIMEOUT=10                           # Timeout in seconds
STEAM_CACHE_TTL=3600                          # Cache TTL in seconds
```

This analysis provides a roadmap for enhancing Steam game discovery while maintaining the current working implementation as a reliable fallback.