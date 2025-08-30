import React, { forwardRef } from 'react';

interface FormFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  required?: boolean;
  type?: 'text' | 'email' | 'password' | 'tel' | 'url';
}

export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
  ({ label, error, required, type = 'text', className = '', ...props }, ref) => {
    const inputClasses = `input-field ${error ? 'input-error' : ''} ${className}`;

    return (
      <div className="space-y-1">
        <label htmlFor={props.id} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        <input
          ref={ref}
          type={type}
          className={inputClasses}
          {...props}
        />
        {error && <p className="error-message">{error}</p>}
      </div>
    );
  }
);

FormField.displayName = 'FormField';