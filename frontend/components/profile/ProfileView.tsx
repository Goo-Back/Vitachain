"use client";

import React from "react";

interface ProfileViewProps {
  profile: {
    id: string;
    email: string;
    full_name: string;
    phone?: string;
    role: string;
    created_at: string;
    updated_at: string;
    role_data?: any;
  };
  onEdit: () => void;
}

export function ProfileView({ profile, onEdit }: ProfileViewProps) {
  const formatPhoneNumber = (phone?: string) => {
    if (!phone) return "Non renseigné";
    
    // Format Moroccan phone numbers
    if (phone.startsWith("+212")) {
      return phone.replace("+212", "+212 ");
    }
    
    return phone;
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "FARMER":
        return "Agriculteur";
      case "RESTAURANT":
        return "Restaurateur";
      case "CITIZEN":
        return "Citoyen";
      case "ADMIN":
        return "Administrateur";
      default:
        return role;
    }
  };

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="flex items-center space-x-4">
        <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center">
          <span className="text-2xl font-bold text-blue-600">
            {profile.full_name.charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900">{profile.full_name}</h3>
          <p className="text-sm text-gray-500">{getRoleLabel(profile.role)}</p>
        </div>
        <button
          onClick={onEdit}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          Modifier
        </button>
      </div>

      {/* Profile Information */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-500">Nom complet</label>
          <div className="mt-1 text-sm text-gray-900">{profile.full_name}</div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-500">Téléphone</label>
          <div className="mt-1 text-sm text-gray-900">
            {formatPhoneNumber(profile.phone)}
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-500">Email</label>
          <div className="mt-1 text-sm text-gray-900">{profile.email}</div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-500">Rôle</label>
          <div className="mt-1">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {getRoleLabel(profile.role)}
            </span>
          </div>
        </div>
      </div>

      {/* Profile Completion Status */}
      <div className="border-t border-gray-200 pt-6">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Complétude du profil</h4>
            <p className="text-sm text-gray-500">
              {profile.phone ? 'Profil complet' : 'Profil incomplet - ajoutez votre numéro de téléphone'}
            </p>
          </div>
          <div className="flex items-center">
            <div className={`h-2 w-2 rounded-full mr-2 ${profile.phone ? 'bg-green-400' : 'bg-yellow-400'}`}></div>
            <span className={`text-sm font-medium ${profile.phone ? 'text-green-600' : 'text-yellow-600'}`}>
              {profile.phone ? 'Complet' : 'Incomplet'}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="border-t border-gray-200 pt-6">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Actions rapides</h4>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={onEdit}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Modifier le profil
          </button>
          
          <button className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            Sécurité
          </button>
          
          <button className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Aide
          </button>
        </div>
      </div>
    </div>
  );
}
