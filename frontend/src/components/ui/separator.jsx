// src\components\ui\separator.jsx
import React from 'react';

const Separator = ({ className, orientation = 'horizontal', decorative = true, ...props }) => {
  // Determina as classes base com base na orientação
  const orientationClasses = orientation === 'horizontal' ? 'h-px w-full' : 'h-full w-px';
  
  // Classe base comum
  const baseClasses = 'shrink-0 bg-border';
  
  // Combina as classes
  const classes = `${baseClasses} ${orientationClasses} ${className}`;

  // Se for apenas decorativo, renderiza um <hr>
  if (decorative) {
    return <hr className={classes} {...props} />;
  }

  // Se não for decorativo, renderiza um <div> com role="separator"
  return (
    <div
      role="separator"
      aria-orientation={orientation}
      className={classes}
      {...props}
    />
  );
};

export { Separator };
