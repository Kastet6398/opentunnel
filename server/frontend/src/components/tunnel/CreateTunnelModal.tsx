import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { createTunnelSchema } from '../../lib/validation';
import { useServerValidation } from '../../hooks/useServerValidation';
import { FormField } from '../forms/FormField';
import { FormButton } from '../forms/FormButton';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface CreateTunnelFormData {
  route: string;
  description: string;
  is_public: boolean;
}

interface CreateTunnelModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateTunnel: (data: CreateTunnelFormData) => Promise<void>;
  isLoading: boolean;
}

export const CreateTunnelModal: React.FC<CreateTunnelModalProps> = ({
  isOpen,
  onClose,
  onCreateTunnel,
  isLoading,
}) => {
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
    reset,
  } = useForm<CreateTunnelFormData>({
    resolver: yupResolver(createTunnelSchema) as any,
  });

  const onSubmit = async (data: CreateTunnelFormData) => {
    clearAllErrors();
    try {
      await onCreateTunnel(data);
      reset();
      onClose();
    } catch (err: any) {
      handleServerError(err);
    }
  };

  const handleClose = () => {
    reset();
    clearAllErrors();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Create New Tunnel</h3>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              {...register('route')}
              id="route"
              label="Route"
              required
              error={errors.route?.message || getFieldErrorMessage('route')}
              placeholder="my-tunnel"
            />
            
            <FormField
              {...register('description')}
              id="description"
              label="Description"
              error={errors.description?.message || getFieldErrorMessage('description')}
              placeholder="Describe your tunnel"
            />

            <div className="flex items-center">
              <input
                {...register('is_public')}
                id="is_public"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="is_public" className="ml-2 block text-sm text-gray-900">
                Make this tunnel public
              </label>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Public tunnels are visible to all users and can be accessed without authentication.
            </p>

            {generalError && (
              <div className="rounded-md bg-red-50 p-3">
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

            <div className="flex space-x-3 pt-4">
              <FormButton
                type="button"
                variant="secondary"
                onClick={handleClose}
                className="flex-1"
              >
                Cancel
              </FormButton>
              <FormButton
                type="submit"
                variant="primary"
                loading={isLoading}
                className="flex-1"
              >
                Create Tunnel
              </FormButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};