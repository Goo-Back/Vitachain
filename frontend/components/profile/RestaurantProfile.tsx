"use client";

import React, { useState } from "react";

interface RestaurantProfileProps {
  profile: {
    id: string;
    role: string;
    role_data?: {
      restaurant_name?: string;
      address?: string;
      cuisine_type?: string;
    };
  };
  isEditing: boolean;
  onUpdate: (data: any) => void;
}

export function RestaurantProfile({ profile, isEditing, onUpdate }: RestaurantProfileProps) {
  const [roleData, setRoleData] = useState({
    restaurant_name: profile.role_data?.restaurant_name || "",
    address: profile.role_data?.address || "",
    cuisine_type: profile.role_data?.cuisine_type || ""
  });

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setRoleData(prev => ({ ...prev, [name]: value }));
    
    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: "" }));
    }
  };

  const validateRoleData = (): boolean => {
    const errors: Record<string, string> = {};

    // Restaurant name validation
    if (roleData.restaurant_name && roleData.restaurant_name.trim().length < 2) {
      errors.restaurant_name = "Le nom du restaurant doit contenir au moins 2 caractères";
    } else if (roleData.restaurant_name && roleData.restaurant_name.trim().length > 100) {
      errors.restaurant_name = "Le nom du restaurant ne peut pas dépasser 100 caractères";
    }

    // Address validation
    if (roleData.address && roleData.address.trim().length < 5) {
      errors.address = "L'adresse doit contenir au moins 5 caractères";
    }

    // Cuisine type validation
    if (roleData.cuisine_type && roleData.cuisine_type.trim().length < 2) {
      errors.cuisine_type = "Le type de cuisine doit contenir au moins 2 caractères";
    } else if (roleData.cuisine_type && roleData.cuisine_type.trim().length > 50) {
      errors.cuisine_type = "Le type de cuisine ne peut pas dépasser 50 caractères";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = () => {
    if (!validateRoleData()) {
      return;
    }

    const updatedRoleData = {
      restaurant_name: roleData.restaurant_name.trim() || null,
      address: roleData.address.trim() || null,
      cuisine_type: roleData.cuisine_type.trim() || null
    };

    onUpdate({ role_data: updatedRoleData });
  };

  if (!isEditing) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Informations Restaurant</h2>
        </div>
        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Nom du restaurant</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {profile.role_data?.restaurant_name || "Non renseigné"}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Adresse</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {profile.role_data?.address || "Non renseigné"}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Type de cuisine</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {profile.role_data?.cuisine_type || "Non renseigné"}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">Informations Restaurant</h2>
      </div>
      <div className="px-6 py-4 space-y-6">
        {/* Restaurant Name */}
        <div>
          <label htmlFor="restaurant_name" className="block text-sm font-medium text-gray-700">
            Nom du restaurant
          </label>
          <div className="mt-1">
            <input
              type="text"
              id="restaurant_name"
              name="restaurant_name"
              value={roleData.restaurant_name}
              onChange={handleInputChange}
              className={`block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                fieldErrors.restaurant_name ? 'border-red-500' : ''
              }`}
              placeholder="Ex: Restaurant Al Mounia"
            />
            {fieldErrors.restaurant_name && (
              <p className="mt-1 text-sm text-red-600">{fieldErrors.restaurant_name}</p>
            )}
          </div>
        </div>

        {/* Address */}
        <div>
          <label htmlFor="address" className="block text-sm font-medium text-gray-700">
            Adresse
          </label>
          <div className="mt-1">
            <textarea
              id="address"
              name="address"
              value={roleData.address}
              onChange={handleInputChange}
              rows={3}
              className={`block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                fieldErrors.address ? 'border-red-500' : ''
              }`}
              placeholder="Ex: 123 Rue Mohammed, Casablanca 20000"
            />
            {fieldErrors.address && (
              <p className="mt-1 text-sm text-red-600">{fieldErrors.address}</p>
            )}
          </div>
        </div>

        {/* Cuisine Type */}
        <div>
          <label htmlFor="cuisine_type" className="block text-sm font-medium text-gray-700">
            Type de cuisine
          </label>
          <div className="mt-1">
            <input
              type="text"
              id="cuisine_type"
              name="cuisine_type"
              value={roleData.cuisine_type}
              onChange={handleInputChange}
              className={`block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                fieldErrors.cuisine_type ? 'border-red-500' : ''
              }`}
              placeholder="Ex: Marocaine, Méditerranéenne, Italienne..."
            />
            {fieldErrors.cuisine_type && (
              <p className="mt-1 text-sm text-red-600">{fieldErrors.cuisine_type}</p>
            )}
          </div>
        </div>

        {/* Save Button */}
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={handleSave}
            className="bg-blue-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Enregistrer les informations restaurant
          </button>
        </div>
      </div>
    </div>
  );
}
