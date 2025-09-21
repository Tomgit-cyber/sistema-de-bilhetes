// src\components\ui\card.jsx
import React from 'react';

// Componente Card principal
const Card = ({ className, ...props }) => (
  <div className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`} {...props} />
);

// Cabeçalho do Card
const CardHeader = ({ className, ...props }) => (
  <div className={`flex flex-col space-y-1.5 p-6 ${className}`} {...props} />
);

// Título do Card
const CardTitle = ({ className, ...props }) => (
  <h3 className={`text-2xl font-semibold leading-none tracking-tight ${className}`} {...props} />
);

// Descrição do Card (opcional)
const CardDescription = ({ className, ...props }) => (
  <p className={`text-sm text-muted-foreground ${className}`} {...props} />
);

// Conteúdo principal do Card
const CardContent = ({ className, ...props }) => (
  <div className={`p-6 pt-0 ${className}`} {...props} />
);

// Rodapé do Card (opcional)
const CardFooter = ({ className, ...props }) => (
  <div className={`flex items-center p-6 pt-0 ${className}`} {...props} />
);

// Exporta todos os componentes
export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
