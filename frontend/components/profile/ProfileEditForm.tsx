"use client";

import React, { useState, useEffect } from "react";
import { PhoneInput } from "@/components/ui/PhoneInput";

interface ProfileEditFormProps {
  profile: {
    id: string;
    email: string;
    full_name: string;
    phone?: string;
    role: string;
    role_data?: any;
  };
  onUpdate: (data: any) => void;
  onCancel: () => void;
  loading: boolean;
}

export function ProfileEditForm({ profile, onUpdate, onCancel, loading }: ProfileEditFormProps) {
  const [formData, setFormData] = useState({
    full_name: profile.full_name || "",
    phone: profile.phone || "",
    role_data: profile.role_data || {}
  });
  
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [phoneValidation, setPhoneValidation] = useState<{
    isValid: boolean;
    formattedPhone?: string;
    error?: string;
  }>({ isValid: true });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: "" }));
    }
  };

  const handlePhoneChange = (phone: string, validation: any) => {
    setFormData(prev => ({ ...prev, phone }));
    setPhoneValidation(validation);
    
    // Clear phone error when user starts typing
    if (fieldErrors.phone) {
      setFieldErrors(prev => ({ ...prev, phone: "" }));
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // Full name validation
    if (!formData.full_name.trim()) {
      errors.full_name = "Le nom complet est requis";
    } else if (formData.full_name.trim().length < 2) {
      errors.full_name = "Le nom complet doit contenir au moins 2 caractères";
    } else if (formData.full_name.trim().length > 100) {
      errors.full_name = "Le nom complet ne peut pas dépasser 100 caractères";
    }

    // Phone validation (optional but if provided, must be valid)
    if (formData.phone && !phoneValidation.isValid) {
      errors.phone = phoneValidation.error || "Format de numéro de téléphone invalide";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const updateData: any = {
      full_name: formData.full_name.trim(),
    };

    // Only include phone if it's provided and valid
    if (formData.phone && phoneValidation.isValid) {
      updateData.phone = phoneValidation.formattedPhone || formData.phone;
    } else if (!formData.phone) {
      // Allow clearing phone number
      updateData.phone = null;
    }

    // Include role data if changed
    if (JSON.stringify(formData.role_data) !== JSON.stringify(profile.role_data || {})) {
      updateData.role_data = formData.role_data;
    }

    await onUpdate(updateData);
  };

  const handleCancel = () => {
    // Reset form to original values
    setFormData({
      full_name: profile.full_name || "",
      phone: profile.phone || "",
      role_data: profile.role_data || {}
    });
    setFieldErrors({});
    onCancel();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Full Name Field */}
      <div>
        <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
          Nom complet <span className="text-red-500">*</span>
        </label>
        <div className="mt-1">
          <input
            type="text"
            id="full_name"
            name="full_name"
            value={formData.full_name}
            onChange={handleInputChange}
            className={`block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
              fieldErrors.full_name ? 'border-red-500' : ''
            }`}
            placeholder="Entrez votre nom complet"
            disabled={loading}
          />
          {fieldErrors.full_name && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.full_name}</p>
          )}
        </div>
      </div>

      {/* Phone Field */}
      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
          Téléphone
        </label>
        <div className="mt-1">
          <PhoneInput
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handlePhoneChange}
            placeholder="+212 6XX-XXXXXXX"
            disabled={loading}
            error={fieldErrors.phone}
          />
          <p className="mt-1 text-xs text-gray-500">
            Formats acceptés: +212 6XX-XXXXXXX, +212 7XX-XXXXXXX, 06XX-XXXXXXX, 07XX-XXXXXXX
          </p>
        </div>
      </div>

      {/* Role-specific fields will be handled by parent components */}

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
        <button
          type="button"
          onClick={handleCancel}
          className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading}
        >
          Annuler
        </button>
        <button
          type="submit"
          className="bg-blue-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading}
        >
          {loading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V8c0 2.29-1.02 4.34-2.62 5.73L12 21l2.62-3.27C16.98 16.34 18 14.29 18 12V4a8 8 0 00-8 8z"></path>
              </svg>
              Enregistrement...
            </span>
          ) : (
            "Enregistrer les modifications"
          )}
        </button>
      </div>
    </form>
  );
}
