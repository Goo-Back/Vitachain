"use client";

import { useState, useEffect } from "react";
import { UserRole, UserRegistrationRequest, UserRegistrationResponse, RoleInfo, FormState, FormErrors } from "@/types/auth";

interface RegisterFormProps {
  onSuccess: (message: string) => void;
  onError: (error: string) => void;
  onLoadingChange: (loading: boolean) => void;
  disabled?: boolean;
}

const roleInfos: RoleInfo[] = [
  {
    value: UserRole.FARMER,
    label: "Agriculteur",
    description: "Propriétaire de ferme ou exploitant agricole",
    icon: "🌾",
    benefits: [
      "Surveiller vos cultures avec IoT",
      "Recevoir des alertes intelligentes", 
      "Vendre directement aux restaurants",
      "Obtenir des recommandations IA"
    ]
  },
  {
    value: UserRole.RESTAURANT,
    label: "Restaurant",
    description: "Gérant de restaurant ou établissement Horeca",
    icon: "🍽️",
    benefits: [
      "Acheter des produits locaux",
      "Vendre vos repas invendus",
      "Réduire le gaspillage alimentaire",
      "Accéder aux solutions IoT"
    ]
  },
  {
    value: UserRole.CITIZEN,
    label: "Citoyen",
    description: "Particulier cherchant des repas locaux",
    icon: "👤",
    benefits: [
      "Découvrir des repas disponibles",
      "Réserver à prix réduit",
      "Soutenir l'économie locale",
      "Réduire le gaspillage"
    ]
  },
  {
    value: UserRole.ADMIN,
    label: "Administrateur",
    description: "Gestionnaire de plateforme VitaChain",
    icon: "⚙️",
    benefits: [
      "Gérer les utilisateurs",
      "Surveiller la plateforme",
      "Accéder aux statistiques",
      "Administrer tous les modules"
    ]
  }
];

export function RegisterForm({ onSuccess, onError, onLoadingChange, disabled = false }: RegisterFormProps) {
  const [formState, setFormState] = useState<FormState>({
    email: "",
    role: "",
    full_name: ""
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [selectedRoleInfo, setSelectedRoleInfo] = useState<RoleInfo | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Email validation regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // Validate individual fields
  const validateField = (name: keyof FormState, value: string): string | undefined => {
    switch (name) {
      case "email":
        if (!value.trim()) {
          return "L'email est requis";
        }
        if (!emailRegex.test(value)) {
          return "Format d'email invalide";
        }
        break;
      
      case "full_name":
        if (!value.trim()) {
          return "Le nom complet est requis";
        }
        if (value.trim().length < 2) {
          return "Le nom doit contenir au moins 2 caractères";
        }
        if (value.trim().length > 100) {
          return "Le nom ne peut pas dépasser 100 caractères";
        }
        break;
      
      case "role":
        if (!value) {
          return "Le rôle est requis";
        }
        break;
    }
  };

  // Validate entire form
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    // Validate each field
    Object.keys(formState).forEach((key) => {
      const error = validateField(key as keyof FormState, formState[key as keyof FormState]);
      if (error) {
        newErrors[key as keyof FormErrors] = error;
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle input changes
  const handleInputChange = (name: keyof FormState, value: string) => {
    setFormState(prev => ({ ...prev, [name]: value }));
    
    // Clear error for this field when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
    
    // Update selected role info when role changes
    if (name === "role") {
      const roleInfo = roleInfos.find(r => r.value === value);
      setSelectedRoleInfo(roleInfo || null);
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    onLoadingChange(true);
    
    try {
      const registrationData: UserRegistrationRequest = {
        email: formState.email.trim(),
        role: formState.role as UserRole,
        full_name: formState.full_name.trim()
      };
      
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(registrationData),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        // Handle different error types
        if (data.error?.code === "VALIDATION_ERROR") {
          const validationErrors: FormErrors = {};
          if (data.error.details?.field) {
            validationErrors[data.error.details.field as keyof FormErrors] = data.error.message;
          } else {
            validationErrors.general = data.error.message;
          }
          setErrors(validationErrors);
          onError(data.error.message);
        } else if (data.error?.code === "EMAIL_EXISTS") {
          setErrors({ email: "Cet email est déjà enregistré" });
          onError("Cet email est déjà enregistré");
        } else if (data.error?.code === "RATE_LIMIT_EXCEEDED") {
          setErrors({ general: "Trop de tentatives. Veuillez réessayer plus tard." });
          onError("Trop de tentatives. Veuillez réessayer plus tard.");
        } else {
          setErrors({ general: data.error?.message || "Une erreur est survenue" });
          onError(data.error?.message || "Une erreur est survenue");
        }
        return;
      }
      
      // Success
      const successData = data as UserRegistrationResponse;
      onSuccess(successData.message);
      
    } catch (error) {
      console.error("Registration error:", error);
      setErrors({ general: "Erreur de connexion. Veuillez réessayer." });
      onError("Erreur de connexion. Veuillez réessayer.");
    } finally {
      setIsSubmitting(false);
      onLoadingChange(false);
    }
  };

  // Check if form is valid for submission
  const isFormValid = formState.email.trim() && 
                     formState.role && 
                     formState.full_name.trim() &&
                     Object.keys(errors).length === 0;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Adresse email *
        </label>
        <div className="mt-1">
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            value={formState.email}
            onChange={(e) => handleInputChange("email", e.target.value)}
            disabled={disabled || isSubmitting}
            className={`appearance-none block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
              errors.email ? "border-red-300" : "border-gray-300"
            }`}
            placeholder="votre@email.com"
            aria-invalid={errors.email ? "true" : "false"}
            aria-describedby={errors.email ? "email-error" : undefined}
          />
          {errors.email && (
            <p className="mt-2 text-sm text-red-600" id="email-error">
              {errors.email}
            </p>
          )}
        </div>
      </div>

      {/* Full Name Field */}
      <div>
        <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
          Nom complet *
        </label>
        <div className="mt-1">
          <input
            id="full_name"
            name="full_name"
            type="text"
            autoComplete="name"
            value={formState.full_name}
            onChange={(e) => handleInputChange("full_name", e.target.value)}
            disabled={disabled || isSubmitting}
            className={`appearance-none block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
              errors.full_name ? "border-red-300" : "border-gray-300"
            }`}
            placeholder="Ahmed Benkiran"
            aria-invalid={errors.full_name ? "true" : "false"}
            aria-describedby={errors.full_name ? "full_name-error" : undefined}
          />
          {errors.full_name && (
            <p className="mt-2 text-sm text-red-600" id="full_name-error">
              {errors.full_name}
            </p>
          )}
        </div>
      </div>

      {/* Role Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Votre rôle *
        </label>
        <div className="space-y-3">
          {roleInfos.map((roleInfo) => (
            <div
              key={roleInfo.value}
              className={`relative border rounded-lg p-4 cursor-pointer transition-all ${
                formState.role === roleInfo.value
                  ? "border-green-500 bg-green-50"
                  : "border-gray-300 hover:border-gray-400"
              } ${disabled || isSubmitting ? "cursor-not-allowed opacity-50" : ""}`}
              onClick={() => !disabled && !isSubmitting && handleInputChange("role", roleInfo.value)}
            >
              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id={`role-${roleInfo.value}`}
                    name="role"
                    type="radio"
                    value={roleInfo.value}
                    checked={formState.role === roleInfo.value}
                    onChange={(e) => handleInputChange("role", e.target.value)}
                    disabled={disabled || isSubmitting}
                    className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300"
                    aria-describedby={`role-description-${roleInfo.value}`}
                  />
                </div>
                <div className="ml-3 flex-1">
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">{roleInfo.icon}</span>
                    <div>
                      <label
                        htmlFor={`role-${roleInfo.value}`}
                        className="font-medium text-gray-900 cursor-pointer"
                      >
                        {roleInfo.label}
                      </label>
                      <p className="text-sm text-gray-500" id={`role-description-${roleInfo.value}`}>
                        {roleInfo.description}
                      </p>
                    </div>
                  </div>
                  
                  {/* Show benefits when role is selected */}
                  {formState.role === roleInfo.value && (
                    <div className="mt-3 p-3 bg-white rounded border border-green-200">
                      <p className="text-sm font-medium text-green-800 mb-2">
                        Avec ce rôle, vous pourrez :
                      </p>
                      <ul className="text-sm text-green-700 space-y-1">
                        {roleInfo.benefits.map((benefit, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-green-500 mr-1">•</span>
                            {benefit}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        {errors.role && (
          <p className="mt-2 text-sm text-red-600">
            {errors.role}
          </p>
        )}
      </div>

      {/* General Error */}
      {errors.general && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Erreur
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{errors.general}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <div>
        <button
          type="submit"
          disabled={!isFormValid || disabled || isSubmitting}
          className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors ${
            isFormValid && !disabled && !isSubmitting
              ? "bg-green-600 hover:bg-green-700"
              : "bg-gray-400 cursor-not-allowed"
          }`}
        >
          {isSubmitting ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Inscription en cours...
            </>
          ) : (
            "Créer mon compte"
          )}
        </button>
      </div>
    </form>
  );
}
