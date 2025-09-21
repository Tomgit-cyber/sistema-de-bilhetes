// src\components\ui\badge.jsx
import React from 'react';

const Badge = ({ children, className = '', variant = 'default', ...props }) => {
  // Classes base comuns a todos os badges
  const baseClasses = 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2';
  
  // Classes para diferentes variantes visuais
  const variantClasses = {
    default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
    secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
    destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
    outline: 'text-foreground',
  };

  // Combina todas as classes
  const classes = `${baseClasses} ${variantClasses[variant]} ${className}`;

  // Renderiza o badge
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

export { Badge };
