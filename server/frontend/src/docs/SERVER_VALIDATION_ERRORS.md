# Server Validation Error Handling

This document explains how to handle server validation errors in the frontend application, specifically for the error format returned by FastAPI/Pydantic validation.

## Error Format

The server returns validation errors in the following format:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "phone_number"],
      "msg": "Value error, Invalid phone number",
      "input": "+11234567890",
      "ctx": {
        "error": {}
      }
    }
  ]
}
```

## Components

### 1. Types (`src/types/errors.ts`)

Defines TypeScript interfaces for server validation errors:

- `ValidationErrorDetail`: Individual error details
- `ValidationErrorResponse`: Complete error response structure
- `FieldErrors`: Field-specific error mapping
- `FormErrorContext`: Error context for forms

### 2. Utility Functions (`src/lib/errorUtils.ts`)

Provides functions to parse and format server validation errors:

- `parseValidationErrors()`: Extracts field-specific errors from server response
- `extractGeneralError()`: Gets general error messages
- `createErrorContext()`: Creates comprehensive error context
- `getFieldError()`: Gets first error for a specific field
- `hasFieldError()`: Checks if field has errors
- `formatFieldErrors()`: Formats multiple field errors for display

### 3. Custom Hook (`src/hooks/useServerValidation.ts`)

The `useServerValidation` hook provides a complete solution for handling server validation errors:

```typescript
const {
  fieldErrors,           // Object with field-specific errors
  generalError,          // General error message
  hasErrors,            // Boolean indicating if there are any errors
  setFieldError,        // Function to set field-specific error
  clearFieldError,      // Function to clear field-specific error
  clearAllErrors,       // Function to clear all errors
  handleServerError,    // Function to handle Axios error responses
  getFieldErrorMessage, // Function to get first error message for a field
  hasFieldErrorMessage, // Function to check if field has error message
  getFormattedFieldError, // Function to get formatted error message for field
} = useServerValidation();
```

## Usage Examples

### Basic Form with Server Validation

```typescript
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { useServerValidation } from '../hooks/useServerValidation';
import { FormField } from '../components/forms/FormField';

const MyForm = () => {
  const [isLoading, setIsLoading] = useState(false);
  const {
    generalError,
    clearAllErrors,
    handleServerError,
    getFieldErrorMessage,
  } = useServerValidation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(mySchema),
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    clearAllErrors();

    try {
      await apiClient.submitData(data);
      // Handle success
    } catch (err) {
      handleServerError(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <FormField
        {...register('email')}
        label="Email"
        error={errors.email?.message || getFieldErrorMessage('email')}
      />
      
      {generalError && (
        <div className="error-message">
          {generalError}
        </div>
      )}
      
      <button type="submit" disabled={isLoading}>
        Submit
      </button>
    </form>
  );
};
```

### Handling Different Error Types

The `handleServerError` function automatically handles different HTTP status codes:

- **422/400**: Validation errors (parsed and mapped to fields)
- **401**: Authentication errors
- **403**: Permission errors
- **404**: Not found errors
- **409**: Conflict errors
- **500**: Server errors
- **Other**: Generic error messages

### Field-Specific Error Display

```typescript
// Get the first error message for a field
const emailError = getFieldErrorMessage('email');

// Check if a field has errors
const hasEmailError = hasFieldErrorMessage('email');

// Get formatted error message (handles multiple errors)
const formattedError = getFormattedFieldError('email');
```

### Manual Error Management

```typescript
const {
  setFieldError,
  clearFieldError,
  clearAllErrors,
} = useServerValidation();

// Set a field-specific error
setFieldError('email', 'This email is already taken');

// Clear a specific field error
clearFieldError('email');

// Clear all errors
clearAllErrors();
```

## Integration with Existing Forms

The system is designed to work seamlessly with existing forms that use:

- **react-hook-form**: For form state management
- **yup**: For client-side validation
- **FormField components**: For consistent error display

### Before (Basic Error Handling)

```typescript
const [error, setError] = useState(null);

try {
  await apiClient.submit(data);
} catch (err) {
  if (err.response?.status === 400) {
    setError('Validation failed');
  }
}
```

### After (Advanced Error Handling)

```typescript
const { generalError, handleServerError, getFieldErrorMessage } = useServerValidation();

try {
  await apiClient.submit(data);
} catch (err) {
  handleServerError(err);
}

// In JSX
<FormField
  error={errors.field?.message || getFieldErrorMessage('field')}
/>
```

## Error Display Components

The system works with existing error display components:

- **FormField**: Shows field-specific errors
- **General error display**: Shows non-field-specific errors
- **Consistent styling**: Uses existing error styling classes

## Best Practices

1. **Always clear errors** before submitting forms
2. **Use field-specific errors** for better UX
3. **Combine client and server validation** for comprehensive validation
4. **Handle different error types** appropriately
5. **Provide clear error messages** to users

## Testing

The system includes a comprehensive example component (`ServerValidationExample`) that demonstrates:

- Field-specific error handling
- General error handling
- Error simulation
- Integration with react-hook-form

Use this component to test and understand the error handling behavior.