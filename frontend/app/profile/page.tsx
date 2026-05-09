"use client";

import { useState, useEffect } from "react";
import { ProfileView } from "@/components/profile/ProfileView";
import { ProfileEditForm } from "@/components/profile/ProfileEditForm";
import { FarmerProfile } from "@/components/profile/FarmerProfile";
import { RestaurantProfile } from "@/components/profile/RestaurantProfile";
import { CitizenProfile } from "@/components/profile/CitizenProfile";

interface ProfileData {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: "FARMER" | "RESTAURANT" | "CITIZEN" | "ADMIN" | "SUPPORT";
  created_at: string;
  updated_at: string;
  role_data?: any;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch("/api/profile/", {
        headers: {
          "Authorization": `Bearer ${getAuthToken()}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error?.message || "Failed to fetch profile");
      }

      const data = await response.json();
      setProfile(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (updateData: Partial<ProfileData>) => {
    try {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);

      const response = await fetch("/api/profile/", {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${getAuthToken()}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error?.message || "Failed to update profile");
      }

      const data = await response.json();
      setProfile(data.profile);
      setIsEditing(false);
      setSuccessMessage("Profil mis à jour avec succès");
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getAuthToken = (): string => {
    // Get auth token from cookies or localStorage
    // This implementation depends on your auth setup
    return document.cookie
      .split('; ')
      .find(row => row.startsWith('sb-access-token='))
      ?.split('=')[1] || '';
  };

  const renderRoleSpecificSection = () => {
    if (!profile) return null;

    switch (profile.role) {
      case "FARMER":
        return <FarmerProfile profile={profile} isEditing={isEditing} onUpdate={handleProfileUpdate} />;
      case "RESTAURANT":
        return <RestaurantProfile profile={profile} isEditing={isEditing} onUpdate={handleProfileUpdate} />;
      case "CITIZEN":
        return <CitizenProfile profile={profile} isEditing={isEditing} onUpdate={handleProfileUpdate} />;
      default:
        return null;
    }
  };

  if (loading && !profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du profil...</p>
        </div>
      </div>
    );
  }

  if (error && !profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <p className="font-medium">Erreur</p>
            <p className="text-sm">{error}</p>
          </div>
          <button
            onClick={fetchProfile}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Mon Profil</h1>
          <p className="mt-2 text-gray-600">
            Gérez vos informations personnelles et vos préférences
          </p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            <p className="font-medium">{successMessage}</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p className="font-medium">Erreur</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Profile Content */}
        {profile && (
          <div className="space-y-6">
            {/* Basic Profile Information */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-medium text-gray-900">Informations Personnelles</h2>
                  {!isEditing && (
                    <button
                      onClick={() => setIsEditing(true)}
                      className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 transition-colors"
                      disabled={loading}
                    >
                      Modifier
                    </button>
                  )}
                </div>
              </div>
              
              <div className="px-6 py-4">
                {isEditing ? (
                  <ProfileEditForm
                    profile={profile}
                    onUpdate={handleProfileUpdate}
                    onCancel={() => setIsEditing(false)}
                    loading={loading}
                  />
                ) : (
                  <ProfileView profile={profile} onEdit={() => setIsEditing(true)} />
                )}
              </div>
            </div>

            {/* Role-Specific Section */}
            {renderRoleSpecificSection()}

            {/* Account Information */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Informations du Compte</h2>
              </div>
              <div className="px-6 py-4">
                <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Email</dt>
                    <dd className="mt-1 text-sm text-gray-900">{profile.email}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Rôle</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {profile.role === "FARMER" && "Agriculteur"}
                        {profile.role === "RESTAURANT" && "Restaurateur"}
                        {profile.role === "CITIZEN" && "Citoyen"}
                        {profile.role === "ADMIN" && "Administrateur"}
                        {profile.role === "SUPPORT" && "Support"}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Date de création</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {new Date(profile.created_at).toLocaleDateString('fr-FR')}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Dernière mise à jour</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {new Date(profile.updated_at).toLocaleDateString('fr-FR')}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
