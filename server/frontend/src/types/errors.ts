// Server validation error types
export interface ValidationErrorDetail {
  type: string;
  loc: (string | number)[];
  msg: string;
  input: any;
  ctx?: Record<string, any>;
}

export interface ValidationErrorResponse {
  detail: ValidationErrorDetail[];
}

// Field-specific error mapping
export interface FieldErrors {
  [fieldName: string]: string[];
}

// Error context for forms
export interface FormErrorContext {
  fieldErrors: FieldErrors;
  generalError: string | null;
  hasErrors: boolean;
}