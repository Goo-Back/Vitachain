import React from "react";

const Alert = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { variant?: "default" | "destructive" }
>(({ className, variant = "default", ...props }, ref) => {
  const baseClasses = "relative w-full rounded-lg border p-4";
  const variantClasses = variant === "destructive" 
    ? "border-red-200 bg-red-50 text-red-800"
    : "border-gray-200 bg-gray-50 text-gray-800";
  
  return (
    <div
      ref={ref}
      className={`${baseClasses} ${variantClasses} ${className || ''}`}
      {...props}
    />
  );
});
Alert.displayName = "Alert";

const AlertDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={`text-sm ${className || ''}`}
    {...props}
  />
));
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertDescription };
