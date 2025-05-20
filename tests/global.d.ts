import '@testing-library/jest-dom';

declare global {
  // Adiciona os matchers personalizados do jest-dom ao escopo global
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R;
      toHaveStyle(style: string): R;
    }
  }
}
