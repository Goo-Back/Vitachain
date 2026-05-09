"use client";

import React, { useState } from "react";

interface FarmerProfileProps {
  profile: {
    id: string;
    role: string;
    role_data?: {
      farm_location?: string;
      farm_size_hectares?: number;
      main_crops?: string[];
    };
  };
  isEditing: boolean;
  onUpdate: (data: any) => void;
}

export function FarmerProfile({ profile, isEditing, onUpdate }: FarmerProfileProps) {
  const [roleData, setRoleData] = useState({
    farm_location: profile.role_data?.farm_location || "",
    farm_size_hectares: profile.role_data?.farm_size_hectares || "",
    main_crops: profile.role_data?.main_crops?.join(", ") || ""
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

    // Farm location validation
    if (roleData.farm_location && roleData.farm_location.trim().length < 2) {
      errors.farm_location = "La localisation doit contenir au moins 2 caractères";
    }

    // Farm size validation
    if (roleData.farm_size_hectares) {
      const size = parseFloat(String(roleData.farm_size_hectares));
      if (isNaN(size) || size < 0) {
        errors.farm_size_hectares = "La taille doit être un nombre positif";
      } else if (size > 10000) {
        errors.farm_size_hectares = "La taille semble trop grande";
      }
    }

    // Main crops validation
    if (roleData.main_crops) {
      const crops = roleData.main_crops.split(",").map(crop => crop.trim()).filter(crop => crop);
      if (crops.length > 20) {
        errors.main_crops = "Trop de cultures spécifiées (maximum 20)";
      }
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = () => {
    if (!validateRoleData()) {
      return;
    }

    const updatedRoleData: any = {
      farm_location: roleData.farm_location.trim() || null,
      farm_size_hectares: roleData.farm_size_hectares ? parseFloat(String(roleData.farm_size_hectares)) : null,
      main_crops: roleData.main_crops 
        ? roleData.main_crops.split(",").map(crop => crop.trim()).filter(crop => crop)
        : []
    };

    onUpdate({ role_data: updatedRoleData });
  };

  const getCropsList = () => {
    if (!roleData.main_crops) return [];
    return roleData.main_crops.split(",").map(crop => crop.trim()).filter(crop => crop);
  };

  if (!isEditing) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Informations Agricole</h2>
        </div>
        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Localisation de la ferme</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {profile.role_data?.farm_location || "Non renseigné"}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Taille (hectares)</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {profile.role_data?.farm_size_hectares 
                  ? `${profile.role_data.farm_size_hectares} ha` 
                  : "Non renseigné"}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Principales cultures</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {profile.role_data?.main_crops && profile.role_data.main_crops.length > 0 
                  ? profile.role_data.main_crops.join(", ")
                  : "Non renseigné"}
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
        <h2 className="text-lg font-medium text-gray-900">Informations Agricole</h2>
      </div>
      <div className="px-6 py-4 space-y-6">
        {/* Farm Location */}
        <div>
          <label htmlFor="farm_location" className="block text-sm font-medium text-gray-700">
            Localisation de la ferme
          </label>
          <div className="mt-1">
            <input
              type="text"
              id="farm_location"
              name="farm_location"
              value={roleData.farm_location}
              onChange={handleInputChange}
              className={`block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                fieldErrors.farm_location ? 'border-red-500' : ''
              }`}
              placeholder="Ex: Casablanca, Rabat, Marrakech..."
            />
            {fieldErrors.farm_location && (
              <p className="mt-1 text-sm text-red-600">{fieldErrors.farm_location}</p>
            )}
          </div>
        </div>

        {/* Farm Size */}
        <div>
          <label htmlFor="farm_size_hectares" className="block text-sm font-medium text-gray-700">
            Taille de la ferme (hectares)
          </label>
          <div className="mt-1">
            <input
              type="number"
              id="farm_size_hectares"
              name="farm_size_hectares"
              value={roleData.farm_size_hectares}
              onChange={handleInputChange}
              step="0.1"
              min="0"
              className={`block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                fieldErrors.farm_size_hectares ? 'border-red-500' : ''
              }`}
              placeholder="Ex: 15.5"
            />
            {fieldErrors.farm_size_hectares && (
              <p className="mt-1 text-sm text-red-600">{fieldErrors.farm_size_hectares}</p>
            )}
          </div>
        </div>

        {/* Main Crops */}
        <div>
          <label htmlFor="main_crops" className="block text-sm font-medium text-gray-700">
            Principales cultures
          </label>
          <div className="mt-1">
            <textarea
              id="main_crops"
              name="main_crops"
              value={roleData.main_crops}
              onChange={handleInputChange}
              rows={3}
              className={`block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                fieldErrors.main_crops ? 'border-red-500' : ''
              }`}
              placeholder="tomates, pommes de terre, laitues..."
            />
            <p className="mt-1 text-xs text-gray-500">
              Séparez les cultures par des virgules
            </p>
            {fieldErrors.main_crops && (
              <p className="mt-1 text-sm text-red-600">{fieldErrors.main_crops}</p>
            )}
          </div>
          
          {/* Preview of crops */}
          {getCropsList().length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-600">Aperçu:</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {getCropsList().map((crop, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                  >
                    {crop}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Save Button */}
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={handleSave}
            className="bg-blue-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Enregistrer les informations agricoles
          </button>
        </div>
      </div>
    </div>
  );
}
