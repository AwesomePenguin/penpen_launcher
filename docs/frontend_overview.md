# PenPen Launcher Frontend Overview

## 项目概述

PenPen Launcher 前端是一个基于 Next.js 和 TypeScript 的现代 Web 应用，专为电视游戏环境设计，提供类似游戏主机的用户体验。前端通过 WebView2 容器运行，支持手柄导航和大屏幕显示。

## 技术栈

- **框架**: Next.js 16 (Pages Router)
- **语言**: TypeScript + React 19
- **样式**: Tailwind CSS 4
- **构建工具**: Next.js Webpack
- **运行环境**: WebView2 (Windows 11)

## 核心功能模块

### 1. 游戏库视图 (Game Library)
**主要功能:**
- 显示用户游戏库的网格布局
- 游戏封面图片展示（支持默认图片回退）
- 游戏元数据显示（标题、发行商、安装状态等）
- 搜索和筛选功能
- 分类浏览（平台、类型、最近游玩等）

**组件结构:**
```
src/components/GameLibrary/
├── GameLibrary.tsx          # 主容器组件
├── GameGrid.tsx             # 游戏网格布局
├── GameCard.tsx             # 单个游戏卡片
├── GameDetails.tsx          # 游戏详情侧边栏
└── SearchFilter.tsx         # 搜索和筛选组件
```

### 2. 手柄输入系统 (Controller Input)
**主要功能:**
- DualShock 4/5 手柄检测和连接
- 方向键导航映射
- 按钮功能定义（确认、取消、菜单等）
- 手柄状态指示器
- 振动反馈支持

**实现方案:**
```typescript
// Gamepad API 集成
interface GamepadContext {
  isConnected: boolean;
  currentGamepad: Gamepad | null;
  buttonMappings: GamepadButtonMapping;
  registerNavigationHandler: (handler: NavigationHandler) => void;
}

// 导航处理器接口
interface NavigationHandler {
  onUp: () => void;
  onDown: () => void;
  onLeft: () => void;
  onRight: () => void;
  onConfirm: () => void;     // X 按钮
  onCancel: () => void;      // Circle 按钮
  onMenu: () => void;        // Options 按钮
  onHome: () => void;        // PS 按钮
}
```

### 3. 游戏启动确认 (Launch Confirmation)
**主要功能:**
- 游戏选中后的启动确认对话框
- 启动选项选择（直接启动、启动器选择等）
- 加载状态指示器
- 错误处理和重试机制

**用户流程:**
1. 用户通过手柄选择游戏
2. 按确认键弹出启动确认对话框
3. 显示游戏详情和启动选项
4. 用户确认后调用后端 API 启动游戏
5. 显示启动进度和状态

### 4. 系统状态监控 (System Status)
**主要功能:**
- 实时系统状态显示（CPU、内存、存储）
- 运行中游戏的状态监控
- 网络连接状态
- 后端服务连接状态

### 5. 设置和配置 (Settings)
**主要功能:**
- 显示设置和主题配置
- 手柄按键重映射
- 网络和云端同步设置
- 系统更新检查

## 目录结构规划

```
src/
├── components/              # 可复用组件
│   ├── GameLibrary/         # 游戏库相关组件
│   ├── Navigation/          # 导航和菜单组件
│   ├── UI/                  # 基础 UI 组件
│   │   ├── Button.tsx
│   │   ├── Modal.tsx
│   │   ├── Card.tsx
│   │   └── LoadingSpinner.tsx
│   └── Layout/              # 布局组件
│       ├── MainLayout.tsx
│       ├── Header.tsx
│       └── Sidebar.tsx
├── pages/                   # Next.js 页面
│   ├── index.tsx            # 主界面（游戏库）
│   ├── game/
│   │   └── [id].tsx         # 游戏详情页面
│   ├── settings/
│   │   └── index.tsx        # 设置页面
│   └── api/                 # API 路由（代理到后端）
│       └── proxy/
├── hooks/                   # 自定义 React Hooks
│   ├── useGamepad.ts        # 手柄输入 Hook
│   ├── useGameLibrary.ts    # 游戏库数据 Hook
│   ├── useWebSocket.ts      # WebSocket 连接 Hook
│   └── useSystemStatus.ts   # 系统状态 Hook
├── contexts/                # React Context
│   ├── GamepadContext.tsx   # 手柄状态上下文
│   ├── GameLibraryContext.tsx # 游戏库状态上下文
│   └── ThemeContext.tsx     # 主题配置上下文
├── services/                # API 服务和外部集成
│   ├── gameLibraryApi.ts    # 游戏库 API 调用
│   ├── systemApi.ts         # 系统控制 API
│   └── websocketService.ts  # WebSocket 服务
├── types/                   # TypeScript 类型定义
│   ├── game.ts              # 游戏相关类型
│   ├── gamepad.ts           # 手柄相关类型
│   ├── system.ts            # 系统状态类型
│   └── api.ts               # API 响应类型
├── utils/                   # 工具函数
│   ├── gamepadUtils.ts      # 手柄工具函数
│   ├── imageUtils.ts        # 图片处理工具
│   └── formatters.ts        # 数据格式化工具
└── styles/                  # 样式文件
    ├── globals.css          # 全局样式
    ├── components.css       # 组件样式
    └── tv-optimized.css     # 电视显示优化样式
```

## 核心数据类型

### 游戏数据类型
```typescript
interface GameInfo {
  id: string;
  name: string;
  description?: string;
  developer?: string;
  publisher?: string;
  releaseDate?: string;
  imageUrl?: string;
  executablePath: string;
  platform: GamePlatform;
  category: GameCategory;
  isInstalled: boolean;
  lastPlayed?: Date;
  playTime?: number;
  rating?: number;
  tags: string[];
}

type GamePlatform = 'steam' | 'epic' | 'battlenet' | 'custom' | 'hoyoverse';
type GameCategory = 'action' | 'adventure' | 'rpg' | 'strategy' | 'simulation' | 'sports' | 'other';
```

### 手柄状态类型
```typescript
interface GamepadState {
  connected: boolean;
  index: number;
  id: string;
  buttons: GamepadButton[];
  axes: number[];
  timestamp: number;
  vibrationActuator?: GamepadHapticActuator;
}

interface GamepadButtonMapping {
  confirm: number;      // X 按钮 (通常是按钮 0)
  cancel: number;       // Circle 按钮 (通常是按钮 1)
  menu: number;         // Options 按钮 (通常是按钮 9)
  home: number;         // PS 按钮 (通常是按钮 16)
  dpadUp: number;       // 方向键上
  dpadDown: number;     // 方向键下
  dpadLeft: number;     // 方向键左
  dpadRight: number;    // 方向键右
}
```

## UI/UX 设计原则

### 电视显示优化
- **大字体**: 最小字体大小 18px，标题使用 24px+
- **高对比度**: 使用明暗对比强烈的配色方案
- **大点击区域**: 按钮和可交互元素最小 48x48px
- **安全区域**: 考虑电视边缘的安全显示区域
- **焦点指示**: 清晰的焦点高亮效果

### 手柄导航体验
- **网格导航**: 支持二维方向键导航
- **焦点循环**: 边界焦点环绕到对侧
- **快捷操作**: 常用功能的快捷键支持
- **视觉反馈**: 按键操作的即时视觉反馈

### 动画和过渡
- **流畅过渡**: 使用 CSS transitions 和 transform
- **微交互**: 悬停、选中、加载等状态的微动画
- **性能优化**: 避免 layout thrashing，优先使用 transform 和 opacity

## API 集成

### 后端 API 接口
```typescript
// 游戏库管理
interface GameLibraryAPI {
  getGames(): Promise<GameInfo[]>;
  getGameById(id: string): Promise<GameInfo>;
  launchGame(id: string, options?: LaunchOptions): Promise<LaunchResult>;
  getGameImage(id: string): Promise<string>; // 返回图片 URL 或 base64
  searchGames(query: string): Promise<GameInfo[]>;
  updateGameMetadata(id: string, metadata: Partial<GameInfo>): Promise<void>;
}

// 系统状态
interface SystemAPI {
  getSystemStatus(): Promise<SystemStatus>;
  restartLauncher(): Promise<void>;
  shutdown(): Promise<void>;
  checkForUpdates(): Promise<UpdateInfo>;
}

// WebSocket 消息类型
interface WebSocketMessage {
  type: 'gameStatusChange' | 'systemStatusUpdate' | 'gameLibraryUpdate';
  data: any;
  timestamp: string;
}
```

### 错误处理策略
- **网络错误**: 自动重试 + 降级显示
- **API 错误**: 用户友好的错误提示
- **图片加载失败**: 默认图片占位符
- **手柄断连**: 自动检测重连 + 键盘降级

## 性能优化策略

### 图片优化
- **懒加载**: 使用 React.lazy 和 Intersection Observer
- **图片格式**: 支持 WebP 格式，PNG/JPG 回退
- **缓存策略**: 游戏封面图片本地缓存
- **占位符**: 加载时的骨架屏或模糊图片

### 渲染优化
- **虚拟滚动**: 大量游戏时的虚拟化列表
- **React.memo**: 防止不必要的重渲染
- **useCallback/useMemo**: 优化计算密集型操作
- **代码分割**: 路由级别的代码分割

### 内存管理
- **组件卸载**: 清理事件监听器和定时器
- **图片资源**: 及时释放不需要的图片资源
- **WebSocket**: 连接生命周期管理

## 开发阶段规划

### 阶段 1: 基础框架搭建
- [ ] 设置 TypeScript 严格模式配置
- [ ] 配置 Tailwind CSS 电视显示主题
- [ ] 创建基础组件库 (Button, Card, Modal)
- [ ] 实现主布局和导航结构

### 阶段 2: 游戏库核心功能
- [ ] 游戏列表展示组件
- [ ] 游戏卡片组件（支持封面图片）
- [ ] 搜索和筛选功能
- [ ] 游戏详情展示

### 阶段 3: 手柄输入集成
- [ ] Gamepad API 集成和状态管理
- [ ] 焦点管理系统
- [ ] 方向键导航逻辑
- [ ] 按键映射和配置

### 阶段 4: 游戏启动流程
- [ ] 启动确认对话框
- [ ] 加载状态管理
- [ ] 错误处理和重试机制
- [ ] 后端 API 集成

### 阶段 5: 高级功能
- [ ] 实时状态监控
- [ ] 设置和配置界面
- [ ] 系统更新检查
- [ ] 性能优化和测试

## 技术考虑

### 浏览器兼容性
- **目标浏览器**: WebView2 (基于 Chromium)
- **ES 特性**: 可以使用最新的 ES2022+ 特性
- **CSS 特性**: 支持 Grid、Flexbox、CSS 变量等现代特性

### 安全性
- **CORS 配置**: 正确配置跨域请求
- **CSP 策略**: 内容安全策略设置
- **输入验证**: 前端输入验证和清理

### 可访问性
- **键盘导航**: 完整的键盘导航支持
- **屏幕阅读器**: ARIA 标签和语义化 HTML
- **色彩对比**: WCAG 2.1 AA 标准色彩对比度

## 部署和构建

### 构建流程
```bash
# 开发环境
npm run dev

# 生产构建
npm run build

# 构建输出目录
frontend/out/
```

### 与后端集成
- **静态文件服务**: 后端 FastAPI 服务静态文件
- **API 代理**: Next.js API 路由代理到后端 API
- **WebSocket 连接**: 直连后端 WebSocket 服务

### 热更新支持
- **开发模式**: Next.js 热重载
- **生产部署**: 构建后静态文件部署
- **版本管理**: 与后端版本同步更新

---

这个前端架构设计为 PenPen Launcher 提供了完整的类主机游戏启动器体验，重点关注手柄导航、电视显示优化和流畅的用户交互。所有组件都按照项目的编程规范进行设计，确保代码质量和可维护性。