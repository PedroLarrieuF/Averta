declare module 'jest-axe' {
  export function toHaveNoViolations(): {
    pass: boolean
    message: () => string
  }
  export function toHaveViolations(): {
    pass: boolean
    message: () => string
  }
}