/**
 * Logger utility - Sistema de logging para o frontend
 * Complementa o sistema de autenticação
 */

enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  data?: any;
  stack?: string;
}

class Logger {
  private logLevel: LogLevel = LogLevel.INFO;
  private logs: LogEntry[] = [];
  private maxLogs: number = 1000;

  constructor() {
    // Configurar nível de log baseado no ambiente
    const env = process.env.NODE_ENV || 'development';
    this.logLevel = env === 'production' ? LogLevel.WARN : LogLevel.DEBUG;
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= this.logLevel;
  }

  private createLogEntry(level: LogLevel, message: string, data?: any): LogEntry {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: LogLevel[level],
      message,
    };

    if (data) {
      entry.data = data;
    }

    if (level === LogLevel.ERROR && data instanceof Error) {
      entry.stack = data.stack;
    }

    return entry;
  }

  private addLog(entry: LogEntry): void {
    this.logs.push(entry);
    
    // Manter apenas os últimos logs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }
  }

  debug(message: string, data?: any): void {
    if (!this.shouldLog(LogLevel.DEBUG)) return;
    
    const entry = this.createLogEntry(LogLevel.DEBUG, message, data);
    this.addLog(entry);
    console.debug(`[DEBUG] ${message}`, data);
  }

  info(message: string, data?: any): void {
    if (!this.shouldLog(LogLevel.INFO)) return;
    
    const entry = this.createLogEntry(LogLevel.INFO, message, data);
    this.addLog(entry);
    console.info(`[INFO] ${message}`, data);
  }

  warn(message: string, data?: any): void {
    if (!this.shouldLog(LogLevel.WARN)) return;
    
    const entry = this.createLogEntry(LogLevel.WARN, message, data);
    this.addLog(entry);
    console.warn(`[WARN] ${message}`, data);
  }

  error(message: string, data?: any): void {
    if (!this.shouldLog(LogLevel.ERROR)) return;
    
    const entry = this.createLogEntry(LogLevel.ERROR, message, data);
    this.addLog(entry);
    console.error(`[ERROR] ${message}`, data);
  }

  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  clearLogs(): void {
    this.logs = [];
  }

  setLogLevel(level: LogLevel): void {
    this.logLevel = level;
  }
}

// ✅ Logger específico para autenticação
class AuthLogger extends Logger {
  constructor() {
    super();
  }

  authSuccess(message: string, data?: any): void {
    this.info(`[AUTH SUCCESS] ${message}`, data);
  }

  authError(message: string, data?: any): void {
    this.error(`[AUTH ERROR] ${message}`, data);
  }

  tokenSet(message: string = 'Token set successfully'): void {
    this.debug(`[TOKEN] ${message}`);
  }

  tokenRemoved(message: string = 'Token removed successfully'): void {
    this.debug(`[TOKEN] ${message}`);
  }

  syncStart(message: string = 'Token sync started'): void {
    this.debug(`[SYNC] ${message}`);
  }

  syncSuccess(message: string = 'Token sync completed successfully'): void {
    this.debug(`[SYNC] ${message}`);
  }

  syncError(message: string, error?: any): void {
    this.error(`[SYNC ERROR] ${message}`, error);
  }
}

// ✅ Instâncias singleton
export const logger = new Logger();
export const authLogger = new AuthLogger();

// ✅ Exportar enums e tipos
export { LogLevel };
export type { LogEntry };
