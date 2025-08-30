import { useState, useCallback } from 'react';
import type { AxiosError } from 'axios';
import type { ValidationErrorResponse, FormErrorContext, FieldErrors } from '../types/errors';
import { createErrorContext, getFieldError, hasFieldError, formatFieldErrors } from '../lib/errorUtils';

interface UseServerValidationReturn {
  fieldErrors: FieldErrors;
  generalError: string | null;
  hasErrors: boolean;
  setFieldError: (fieldName: string, error: string) => void;
  clearFieldError: (fieldName: string) => void;
  clearAllErrors: () => void;
  handleServerError: (error: AxiosError) => void;
  getFieldErrorMessage: (fieldName: string) => string | undefined;
  hasFieldErrorMessage: (fieldName: string) => boolean;
  getFormattedFieldError: (fieldName: string) => string;
}

/**
 * Custom hook for handling server validation errors
 */
export const useServerValidation = (): UseServerValidationReturn => {
  const [errorContext, setErrorContext] = useState<FormErrorContext>({
    fieldErrors: {},
    generalError: null,
    hasErrors: false,
  });

  const setFieldError = useCallback((fieldName: string, error: string) => {
    setErrorContext(prev => ({
      ...prev,
      fieldErrors: {
        ...prev.fieldErrors,
        [fieldName]: [error],
      },
      hasErrors: true,
    }));
  }, []);

  const clearFieldError = useCallback((fieldName: string) => {
    setErrorContext(prev => {
      const newFieldErrors = { ...prev.fieldErrors };
      delete newFieldErrors[fieldName];
      
      return {
        ...prev,
        fieldErrors: newFieldErrors,
        hasErrors: Object.keys(newFieldErrors).length > 0 || !!prev.generalError,
      };
    });
  }, []);

  const clearAllErrors = useCallback(() => {
    setErrorContext({
      fieldErrors: {},
      generalError: null,
      hasErrors: false,
    });
  }, []);

  const handleServerError = useCallback((error: AxiosError) => {
    // Check if it's a validation error (422 status code is common for validation errors)
    if (error.response?.status === 422 || error.response?.status === 400) {
      const errorData = error.response.data as ValidationErrorResponse;
      
      if (errorData && errorData.detail) {
        const newErrorContext = createErrorContext(errorData);
        setErrorContext(newErrorContext);
        return;
      }
    }

    // Handle other types of errors
    let generalError = 'An unexpected error occurred. Please try again.';
    
    if (error.response?.status === 401) {
      generalError = 'Authentication failed. Please check your credentials.';
    } else if (error.response?.status === 403) {
      generalError = 'You do not have permission to perform this action.';
    } else if (error.response?.status === 404) {
      generalError = 'The requested resource was not found.';
    } else if (error.response?.status === 409) {
      generalError = 'A conflict occurred. The resource may already exist.';
    } else if (error.response?.status === 500) {
      generalError = 'Server error. Please try again later.';
    } else if (error.response?.data && typeof error.response.data === 'object' && 'message' in error.response.data) {
      generalError = (error.response.data as any).message;
    } else if (error.response?.data && typeof error.response.data === 'object' && 'detail' in error.response.data && typeof (error.response.data as any).detail === 'string') {
      generalError = (error.response.data as any).detail;
    }

    setErrorContext({
      fieldErrors: {},
      generalError,
      hasErrors: true,
    });
  }, []);

  const getFieldErrorMessage = useCallback((fieldName: string): string | undefined => {
    return getFieldError(errorContext.fieldErrors, fieldName);
  }, [errorContext.fieldErrors]);

  const hasFieldErrorMessage = useCallback((fieldName: string): boolean => {
    return hasFieldError(errorContext.fieldErrors, fieldName);
  }, [errorContext.fieldErrors]);

  const getFormattedFieldError = useCallback((fieldName: string): string => {
    return formatFieldErrors(errorContext.fieldErrors, fieldName);
  }, [errorContext.fieldErrors]);

  return {
    fieldErrors: errorContext.fieldErrors,
    generalError: errorContext.generalError,
    hasErrors: errorContext.hasErrors,
    setFieldError,
    clearFieldError,
    clearAllErrors,
    handleServerError,
    getFieldErrorMessage,
    hasFieldErrorMessage,
    getFormattedFieldError,
  };
};