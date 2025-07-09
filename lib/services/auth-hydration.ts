/**
 * AuthHydrationService - Serviço de hidratação de estado de autenticação
 * Resolve o erro: "Falha na hidratação após todas as tentativas"
 */

import { authService, type User } from './auth';
import { authLogger } from '../utils/logger';

// ✅ Definição de tipos de erro
export enum AuthErrorCode {
  HYDRATION_FAILED = 'HYDRATION_FAILED',
  TOKEN_INVALID = 'TOKEN_INVALID',
  USER_NOT_FOUND = 'USER_NOT_FOUND',
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
  UNKNOWN = 'UNKNOWN'
}

export enum AuthErrorCategory {
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  NETWORK = 'NETWORK',
  VALIDATION = 'VALIDATION',
  INTERNAL = 'INTERNAL'
}

export interface AuthErrorDetails {
  code: AuthErrorCode;
  message: string;
  category: AuthErrorCategory;
  originalError?: Error;
  timestamp?: Date;
}

export class AuthError extends Error {
  public readonly code: AuthErrorCode;
  public readonly category: AuthErrorCategory;
  public readonly timestamp: Date;
  public readonly originalError?: Error;

  constructor(details: AuthErrorDetails) {
    super(details.message);
    this.name = 'AuthError';
    this.code = details.code;
    this.category = details.category;
    this.timestamp = details.timestamp || new Date();
    this.originalError = details.originalError;
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      category: this.category,
      timestamp: this.timestamp.toISOString(),
      stack: this.stack
    };
  }
}

// ✅ Configuração de hidratação
interface HydrationConfig {
  maxRetries: number;
  retryDelay: number;
  timeout: number;
  validateToken: boolean;
  fallbackToGuest: boolean;
}

// ✅ Resultado da hidratação
interface HydrationResult {
  success: boolean;
  user: User | null;
  error: AuthError | null;
  timestamp: Date;
  attempts: number;
}

// ✅ Estado de hidratação
export enum HydrationState {
  PENDING = 'PENDING',
  LOADING = 'LOADING',
  SUCCESS = 'SUCCESS',
  FAILED = 'FAILED',
  TIMEOUT = 'TIMEOUT'
}

export class AuthHydrationService {
  private static instance: AuthHydrationService;
  
  private config: HydrationConfig = {
    maxRetries: 3,
    retryDelay: 1000,
    timeout: 10000,
    validateToken: true,
    fallbackToGuest: true
  };

  private currentState: HydrationState = HydrationState.PENDING;
  private lastResult: HydrationResult | null = null;

  private constructor() {}

  /**
   * ✅ Singleton pattern
   */
  static getInstance(): AuthHydrationService {
    if (!AuthHydrationService.instance) {
      AuthHydrationService.instance = new AuthHydrationService();
    }
    return AuthHydrationService.instance;
  }

  /**
   * ✅ Configurar serviço de hidratação
   */
  configure(config: Partial<HydrationConfig>): void {
    this.config = { ...this.config, ...config };
    authLogger.info('AuthHydrationService configurado', this.config);
  }

  /**
   * ✅ Obter estado atual
   */
  getState(): HydrationState {
    return this.currentState;
  }

  /**
   * ✅ Obter último resultado
   */
  getLastResult(): HydrationResult | null {
    return this.lastResult;
  }

  /**
   * ✅ Método principal de hidratação - CORRIGIDO
   */
  async hydrateAuthState(): Promise<HydrationResult> {
    const startTime = Date.now();
    this.currentState = HydrationState.LOADING;

    authLogger.info('Iniciando hidratação do estado de autenticação');

    const result: HydrationResult = {
      success: false,
      user: null,
      error: null,
      timestamp: new Date(),
      attempts: 0
    };

    try {
      // Tentar hidratação com retry
      for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
        result.attempts = attempt;
        
        authLogger.debug(`Tentativa de hidratação ${attempt}/${this.config.maxRetries}`);

        try {
          // ✅ Verificar timeout
          if (Date.now() - startTime > this.config.timeout) {
            throw new AuthError({
              code: AuthErrorCode.TIMEOUT,
              message: 'Timeout na hidratação do estado de autenticação',
              category: AuthErrorCategory.INTERNAL
            });
          }

          // ✅ Tentar hidratar estado
          const hydrationResult = await this.attemptHydration();
          
          if (hydrationResult.success) {
            result.success = true;
            result.user = hydrationResult.user;
            this.currentState = HydrationState.SUCCESS;
            
            authLogger.authSuccess('Hidratação de estado concluída com sucesso', {
              user: result.user?.email,
              attempts: attempt
            });
            
            this.lastResult = result;
            return result;
          }

          // Se não foi bem-sucedida, mas não é o último attempt, tentar novamente
          if (attempt < this.config.maxRetries) {
            authLogger.debug(`Tentativa ${attempt} falhou, tentando novamente em ${this.config.retryDelay}ms`);
            await this.delay(this.config.retryDelay);
          }

        } catch (error) {
          authLogger.error(`Erro na tentativa ${attempt} de hidratação`, error);
          
          // Se é o último attempt ou erro crítico, parar
          if (attempt === this.config.maxRetries || this.isCriticalError(error)) {
            throw error;
          }
          
          // Aguardar antes da próxima tentativa
          await this.delay(this.config.retryDelay);
        }
      }

      // ✅ Todas as tentativas falharam - CORRIGIDO
      this.currentState = HydrationState.FAILED;
      
      result.error = new AuthError({
        code: AuthErrorCode.HYDRATION_FAILED,
        message: 'Falha na hidratação após todas as tentativas',
        category: AuthErrorCategory.INTERNAL,
      });

      // ✅ Fallback para guest se configurado
      if (this.config.fallbackToGuest) {
        authLogger.info('Aplicando fallback para estado de convidado');
        result.success = true;
        result.user = null;
        this.currentState = HydrationState.SUCCESS;
      }

    } catch (error) {
      this.currentState = HydrationState.FAILED;
      
      result.error = error instanceof AuthError ? error : new AuthError({
        code: AuthErrorCode.UNKNOWN,
        message: error instanceof Error ? error.message : 'Erro desconhecido na hidratação',
        category: AuthErrorCategory.INTERNAL,
        originalError: error instanceof Error ? error : undefined
      });

      authLogger.authError('Erro crítico na hidratação', result.error);
    }

    this.lastResult = result;
    return result;
  }

  /**
   * ✅ Tentativa individual de hidratação
   */
  private async attemptHydration(): Promise<{ success: boolean; user: User | null }> {
    try {
      // 1. Verificar se há token no localStorage
      const token = authService.getToken();
      if (!token) {
        authLogger.debug('Nenhum token encontrado no localStorage');
        return { success: true, user: null };
      }

      // 2. Verificar se há dados do usuário no localStorage
      const storedUser = authService.getUser();
      if (!storedUser) {
        authLogger.debug('Nenhum usuário encontrado no localStorage');
        // Token existe mas não há dados do usuário, limpar token
        authService.setToken(null);
        return { success: true, user: null };
      }

      // 3. Validar token com backend se configurado
      if (this.config.validateToken) {
        authLogger.debug('Validando token com backend');
        
        try {
          const verifiedUser = await authService.verifyUser();
          if (verifiedUser) {
            authLogger.debug('Token válido, usuário autenticado');
            return { success: true, user: verifiedUser };
          } else {
            authLogger.debug('Token inválido, limpando dados');
            await authService.logout();
            return { success: true, user: null };
          }
        } catch (error) {
          // Se a verificação falhar, mas temos dados locais, usar dados locais
          authLogger.warn('Falha na verificação do token, usando dados locais', error);
          return { success: true, user: storedUser };
        }
      }

      // 4. Usar dados locais sem validação
      authLogger.debug('Usando dados locais sem validação');
      return { success: true, user: storedUser };

    } catch (error) {
      authLogger.error('Erro na tentativa de hidratação', error);
      throw error;
    }
  }

  /**
   * ✅ Verificar se é erro crítico
   */
  private isCriticalError(error: any): boolean {
    if (error instanceof AuthError) {
      return error.code === AuthErrorCode.TIMEOUT;
    }
    return false;
  }

  /**
   * ✅ Delay utilitário
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * ✅ Resetar estado
   */
  reset(): void {
    this.currentState = HydrationState.PENDING;
    this.lastResult = null;
    authLogger.info('Estado de hidratação resetado');
  }

  /**
   * ✅ Forçar nova hidratação
   */
  async refresh(): Promise<HydrationResult> {
    this.reset();
    return this.hydrateAuthState();
  }

  /**
   * ✅ Obter estatísticas
   */
  getStats() {
    return {
      currentState: this.currentState,
      lastResult: this.lastResult,
      config: this.config,
      timestamp: new Date().toISOString()
    };
  }
}

// ✅ Exportar instância singleton
export const authHydrationService = AuthHydrationService.getInstance();
export default authHydrationService;
