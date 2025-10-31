// Gamepad and controller input type definitions
export interface GamepadState {
  connected: boolean;
  index: number;
  id: string;
  buttons: GamepadButton[];
  axes: number[];
  timestamp: number;
  vibrationActuator?: GamepadHapticActuator;
}

export interface GamepadButton {
  pressed: boolean;
  touched: boolean;
  value: number;
}

export interface GamepadButtonMapping {
  confirm: number;      // X button (usually button 0)
  cancel: number;       // Circle button (usually button 1)
  menu: number;         // Options button (usually button 9)
  home: number;         // PS button (usually button 16)
  dpadUp: number;       // D-pad up
  dpadDown: number;     // D-pad down
  dpadLeft: number;     // D-pad left
  dpadRight: number;    // D-pad right
}

export interface NavigationHandler {
  onUp: () => void;
  onDown: () => void;
  onLeft: () => void;
  onRight: () => void;
  onConfirm: () => void;     // X button
  onCancel: () => void;      // Circle button
  onMenu: () => void;        // Options button
  onHome: () => void;        // PS button
}

export interface GamepadContextType {
  gamepadState: GamepadState | null;
  isConnected: boolean;
  buttonMappings: GamepadButtonMapping;
  registerNavigationHandler: (handler: NavigationHandler) => void;
  unregisterNavigationHandler: () => void;
}