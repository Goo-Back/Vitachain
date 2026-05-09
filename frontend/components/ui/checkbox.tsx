// Checkbox component - basic implementation
import React, { forwardRef } from 'react';

interface CheckboxProps {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  disabled?: boolean;
  className?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(({ 
  checked = false, 
  onCheckedChange, 
  disabled = false,
  className = ""
}, ref) => {
  return (
    <input
      ref={ref}
      type="checkbox"
      checked={checked}
      onChange={(e) => onCheckedChange?.(e.target.checked)}
      disabled={disabled}
      className={`form-checkbox h-4 w-4 text-blue-600 ${className}`}
    />
  );
});

Checkbox.displayName = "Checkbox";
