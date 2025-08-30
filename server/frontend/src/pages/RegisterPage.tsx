import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { registerSchema, formatPhoneNumber } from '../lib/validation';
import { useAuth } from '../contexts/AuthContext';
import { useServerValidation } from '../hooks/useServerValidation';
import { FormField } from '../components/forms/FormField';
import { PasswordField } from '../components/forms/PasswordField';
import { FormButton } from '../components/forms/FormButton';

interface RegisterFormData {
  email: string;
  phone_number: string;
  password: string;
  confirmPassword: string;
}

export const RegisterPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
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
  } = useForm<RegisterFormData>({
    resolver: yupResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    clearAllErrors();

    try {
      // Format phone number before sending
      const formattedPhone = formatPhoneNumber(data.phone_number);
      await registerUser(data.email, formattedPhone, data.password);
      navigate('/dashboard');
    } catch (err: any) {
      handleServerError(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link
              to="/login"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              sign in to your existing account
            </Link>
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <FormField
              {...register('email')}
              id="email"
              label="Email address"
              type="email"
              autoComplete="email"
              required
              error={errors.email?.message || getFieldErrorMessage('email')}
              placeholder="Enter your email"
            />
            
            <FormField
              {...register('phone_number')}
              id="phone_number"
              label="Phone number"
              type="tel"
              autoComplete="tel"
              required
              error={errors.phone_number?.message || getFieldErrorMessage('phone_number')}
              placeholder="+1234567890"
            />
            
            <PasswordField
              {...register('password')}
              id="password"
              label="Password"
              autoComplete="new-password"
              required
              error={errors.password?.message || getFieldErrorMessage('password')}
              placeholder="Create a strong password"
            />
            
            <PasswordField
              {...register('confirmPassword')}
              id="confirmPassword"
              label="Confirm password"
              autoComplete="new-password"
              required
              error={errors.confirmPassword?.message || getFieldErrorMessage('confirmPassword')}
              placeholder="Confirm your password"
            />
          </div>

          {generalError && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-400"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">{generalError}</h3>
                </div>
              </div>
            </div>
          )}

          <div>
            <FormButton
              type="submit"
              variant="primary"
              size="lg"
              loading={isLoading}
              className="w-full"
            >
              Create account
            </FormButton>
          </div>

          <div className="text-center">
            <p className="text-xs text-gray-600">
              By creating an account, you agree to our{' '}
              <Link to="/terms" className="text-primary-600 hover:text-primary-500">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link to="/privacy" className="text-primary-600 hover:text-primary-500">
                Privacy Policy
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};
