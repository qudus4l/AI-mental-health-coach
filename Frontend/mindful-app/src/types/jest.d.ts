/// <reference types="jest" />

// Extend Jest's expect
interface CustomMatchers<R = unknown> {
  toBeInTheDocument(): R;
  toHaveAttribute(attr: string, value?: string | RegExp): R;
  toHaveClass(className: string): R;
  toHaveTextContent(text: string | RegExp): R;
}

declare global {
  namespace jest {
    interface Expect extends CustomMatchers {}
    interface Matchers<R> extends CustomMatchers<R> {}
    interface InverseAsymmetricMatchers extends CustomMatchers {}
  }
} 