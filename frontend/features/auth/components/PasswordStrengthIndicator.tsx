"use client";

import { useEffect, useState } from "react";
import { Progress } from "@/components/ui/progress";
import { CheckCircle, XCircle, AlertCircle } from "lucide-react";

interface PasswordStrengthIndicatorProps {
  password: string;
}

interface PasswordRequirement {
  regex: RegExp;
  text: string;
  met: boolean;
}

export function PasswordStrengthIndicator({ password }: PasswordStrengthIndicatorProps) {
  const [strength, setStrength] = useState({
    score: 0,
    strength: "very_weak" as "very_weak" | "weak" | "medium" | "strong" | "very_strong",
    feedback: [] as string[],
  });

  const [requirements, setRequirements] = useState<PasswordRequirement[]>([
    { regex: /.{8,}/, text: "Au moins 8 caractères", met: false },
    { regex: /[A-Z]/, text: "Au moins une lettre majuscule", met: false },
    { regex: /[a-z]/, text: "Au moins une lettre minuscule", met: false },
    { regex: /\d/, text: "Au moins un chiffre", met: false },
    { regex: /[!@#$%^&*(),.?":{}|<>]/, text: "Caractère spécial (recommandé)", met: false },
  ]);

  useEffect(() => {
    if (!password) {
      setStrength({ score: 0, strength: "very_weak", feedback: [] });
      setRequirements(reqs => reqs.map(req => ({ ...req, met: false })));
      return;
    }

    // Check requirements
    const updatedRequirements = requirements.map(req => ({
      ...req,
      met: req.regex.test(password),
    }));
    setRequirements(updatedRequirements);

    // Calculate strength score
    let score = 0;
    const feedback: string[] = [];

    // Length scoring
    if (password.length >= 8) score += 20;
    if (password.length >= 12) score += 10;
    if (password.length >= 16) score += 10;

    // Character variety scoring
    if (/[a-z]/.test(password)) {
      score += 15;
      feedback.push("Contient des lettres minuscules");
    } else {
      feedback.push("Ajoutez des lettres minuscules");
    }

    if (/[A-Z]/.test(password)) {
      score += 15;
      feedback.push("Contient des lettres majuscules");
    } else {
      feedback.push("Ajoutez des lettres majuscules");
    }

    if (/\d/.test(password)) {
      score += 15;
      feedback.push("Contient des chiffres");
    } else {
      feedback.push("Ajoutez des chiffres");
    }

    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      score += 15;
      feedback.push("Contient des caractères spéciaux");
    } else {
      feedback.push("Ajoutez des caractères spéciaux");
    }

    // Common patterns penalty
    if (/(.)\1{2,}/.test(password)) {
      score -= 10;
      feedback.push("Évitez les caractères répétés");
    }

    if (/123456|qwerty|password|admin/i.test(password)) {
      score -= 20;
      feedback.push("Évitez les mots de passe communs");
    }

    // Determine strength level
    let strengthLevel: "very_weak" | "weak" | "medium" | "strong" | "very_strong" = "very_weak";
    if (score >= 80) strengthLevel = "very_strong";
    else if (score >= 60) strengthLevel = "strong";
    else if (score >= 40) strengthLevel = "medium";
    else if (score >= 20) strengthLevel = "weak";

    setStrength({
      score: Math.max(0, Math.min(100, score)),
      strength: strengthLevel,
      feedback,
    });
  }, [password]);

  const getStrengthColor = () => {
    switch (strength.strength) {
      case "very_weak":
        return "bg-red-500";
      case "weak":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      case "strong":
        return "bg-green-500";
      case "very_strong":
        return "bg-emerald-500";
      default:
        return "bg-gray-300";
    }
  };

  const getStrengthTextColor = () => {
    switch (strength.strength) {
      case "very_weak":
        return "text-red-600";
      case "weak":
        return "text-orange-600";
      case "medium":
        return "text-yellow-600";
      case "strong":
        return "text-green-600";
      case "very_strong":
        return "text-emerald-600";
      default:
        return "text-gray-600";
    }
  };

  const getStrengthText = () => {
    switch (strength.strength) {
      case "very_weak":
        return "Très faible";
      case "weak":
        return "Faible";
      case "medium":
        return "Moyen";
      case "strong":
        return "Fort";
      case "very_strong":
        return "Très fort";
      default:
        return "";
    }
  };

  const getStrengthIcon = () => {
    switch (strength.strength) {
      case "very_weak":
      case "weak":
        return <XCircle className="h-4 w-4" />;
      case "medium":
        return <AlertCircle className="h-4 w-4" />;
      case "strong":
      case "very_strong":
        return <CheckCircle className="h-4 w-4" />;
      default:
        return null;
    }
  };

  if (!password) {
    return null;
  }

  return (
    <div className="space-y-3">
      {/* Strength bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium">Force du mot de passe</span>
          <span className={`flex items-center gap-1 ${getStrengthTextColor()}`}>
            {getStrengthIcon()}
            {getStrengthText()}
          </span>
        </div>
        <Progress 
          value={strength.score} 
          className="h-2"
        />
        <div className={`h-1 rounded-full ${getStrengthColor()} transition-all duration-300`} 
             style={{ width: `${strength.score}%` }} />
      </div>

      {/* Requirements checklist */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-700">Exigences:</p>
        <div className="space-y-1">
          {requirements.map((req, index) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              {req.met ? (
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
              ) : (
                <XCircle className="h-4 w-4 text-gray-300 flex-shrink-0" />
              )}
              <span className={req.met ? "text-green-700" : "text-gray-500"}>
                {req.text}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Feedback messages */}
      {strength.feedback.length > 0 && (
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-700">Conseils:</p>
          <div className="text-xs text-gray-600 space-y-1">
            {strength.feedback.map((feedback, index) => (
              <div key={index}>• {feedback}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
