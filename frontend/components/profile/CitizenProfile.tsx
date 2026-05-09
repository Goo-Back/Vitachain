"use client";

import React, { useState } from "react";

interface CitizenProfileProps {
  profile: {
    id: string;
    role: string;
    role_data?: {
      preferred_pickup_locations?: string[];
    };
  };
  isEditing: boolean;
  onUpdate: (data: any) => void;
}

export function CitizenProfile({ profile, isEditing, onUpdate }: CitizenProfileProps) {
  const [roleData, setRoleData] = useState({
    preferred_pickup_locations: profile.role_data?.preferred_pickup_locations?.join(", ") || ""
  });

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setRoleData(prev => ({ ...prev, [name]: value }));
    
    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: "" }));
    }
  };

  const validateRoleData = (): boolean => {
    const errors: Record<string, string> = {};

    // Preferred pickup locations validation
    if (roleData.preferred_pickup_locations) {
      const locations = roleData.preferred_pickup_locations.split(",").map(loc => loc.trim()).filter(loc => loc);
      if (locations.length > 10) {
        errors.preferred_pickup_locations = "Trop de lieux spécifiés (maximum 10)";
      }
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = () => {
    if (!validateRoleData()) {
      return;
    }

    const updatedRoleData = {
      preferred_pickup_locations: roleData.preferred_pickup_locations 
        ? roleData.preferred_pickup_locations.split(",").map(loc => loc.trim()).filter(loc => loc)
        : []
    };

    onUpdate({ role_data: updatedRoleData });
  };

  const getLocationsList = () => {
    if (!roleData.preferred_pickup_locations) return [];
    return roleData.preferred_pickup_locations.split(",").map(loc => loc.trim()).filter(loc => loc);
  };

  if (!isEditing) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Préférences de Livraison</h2>
        </div>
        <div className="px-6 py-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">Lieux de retrait préférés</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {profile.role_data?.preferred_pickup_locations && profile.role_data.preferred_pickup_locations.length > 0 
                ? (
                  <div className="flex flex-wrap gap-2">
                    {profile.role_data.preferred_pickup_locations.map((location, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {location}
                      </span>
                    ))}
                  </div>
                )
                : "Non renseigné"}
            </dd>
          </div>
          
          {profile.role_data?.preferred_pickup_locations && profile.role_data.preferred_pickup_locations.length > 0 && (
            <div className="mt-4 p-3 bg-blue-50 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>Conseil:</strong> Vos lieux de retrait préférés nous aideront à vous proposer les meilleures options de livraison.
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">Préférences de Livraison</h2>
      </div>
      <div className="px-6 py-4 space-y-6">
        {/* Preferred Pickup Locations */}
        <div>
          <label htmlFor="preferred_pickup_locations" className="block text-sm font-medium text-gray-700">
            Lieux de retrait préférés
          </label>
          <div className="mt-1">
            <textarea
              id="preferred_pickup_locations"
              name="preferred_pickup_locations"
              value={roleData.preferred_pickup_locations}
              onChange={handleInputChange}
              rows={4}
              className={`block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                fieldErrors.preferred_pickup_locations ? 'border-red-500' : ''
              }`}
              placeholder="Casablanca, Rabat, Marrakech, Tanger..."
            />
            <p className="mt-1 text-xs text-gray-500">
              Entrez vos villes ou quartiers préférés, séparés par des virgules
            </p>
            {fieldErrors.preferred_pickup_locations && (
              <p className="mt-1 text-sm text-red-600">{fieldErrors.preferred_pickup_locations}</p>
            )}
          </div>
          
          {/* Preview of locations */}
          {getLocationsList().length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-600">Aperçu:</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {getLocationsList().map((location, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {location}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Helpful Tips */}
        <div className="p-4 bg-gray-50 rounded-md">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Conseils pour les lieux de retrait:</h4>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>• Choisissez des lieux proches de votre domicile ou travail</li>
            <li>• Privilégiez les zones avec plusieurs restaurants partenaires</li>
            <li>• Vous pouvez modifier ces préférences à tout moment</li>
            <li>• Maximum 10 lieux de retrait préférés</li>
          </ul>
        </div>

        {/* Save Button */}
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={handleSave}
            className="bg-blue-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Enregistrer les préférences de livraison
          </button>
        </div>
      </div>
    </div>
  );
}
