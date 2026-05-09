"use client";

import React, { useState, useEffect } from "react";

interface PhoneInputProps {
  id?: string;
  name?: string;
  value: string;
  onChange: (phone: string, validation: any) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
}

export function PhoneInput({ id, name, value, onChange, placeholder, disabled, error }: PhoneInputProps) {
  const [validation, setValidation] = useState({
    isValid: true,
    formattedPhone: value,
    error: null
  });

  const validateMoroccanPhone = (phone: string) => {
    if (!phone) {
      return { isValid: true, formattedPhone: "", error: null };
    }

    // Remove spaces and special characters
    const cleanPhone = phone.replace(/[^\d+]/g, '');

    // Moroccan phone patterns
    const patterns = [
      /^\+2126\d{8}$/,    // +2126XXXXXXXX
      /^\+2127\d{8}$/,    // +2127XXXXXXXX
      /^06\d{8}$/,      // 06XXXXXXXX
      /^07\d{8}$/       // 07XXXXXXXX
    ];

    const isValid = patterns.some(pattern => pattern.test(cleanPhone));
    
    let formattedPhone = cleanPhone;
    if (isValid) {
      // Format to international format
      if (cleanPhone.startsWith('06') || cleanPhone.startsWith('07')) {
        formattedPhone = `+212${cleanPhone.substring(1)}`;
      } else if (cleanPhone.startsWith('2126') || cleanPhone.startsWith('2127')) {
        formattedPhone = `+${cleanPhone}`;
      }
    }

    return {
      isValid,
      formattedPhone,
      error: isValid ? null : "Format de téléphone marocain invalide"
    };
  };

  const formatPhoneDisplay = (phone: string) => {
    if (!phone) return phone;
    
    // Format for display: +212 6XX-XXXXXXX
    if (phone.startsWith('+2126') && phone.length === 13) {
      return `+212 ${phone.substring(4, 7)}-${phone.substring(7)}`;
    }
    if (phone.startsWith('+2127') && phone.length === 13) {
      return `+212 ${phone.substring(4, 7)}-${phone.substring(7)}`;
    }
    
    return phone;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    const validation = validateMoroccanPhone(inputValue);
    
    setValidation(validation);
    onChange(inputValue, validation);
  };

  useEffect(() => {
    const validation = validateMoroccanPhone(value);
    setValidation(validation);
  }, [value]);

  return (
    <div>
      <input
        type="tel"
        id={id}
        name={name}
        value={formatPhoneDisplay(value)}
        onChange={handleChange}
        placeholder={placeholder || "+212 6XX-XXXXXXX"}
        disabled={disabled}
        className={`block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
          error || !validation.isValid ? 'border-red-500' : ''
        } ${disabled ? 'bg-gray-100' : ''}`}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
      {!error && !validation.isValid && validation.error && (
        <p className="mt-1 text-sm text-red-600">{validation.error}</p>
      )}
    </div>
  );
}
