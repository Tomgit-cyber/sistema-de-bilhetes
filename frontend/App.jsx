// Local: frontend/src/App.jsx (Código de Teste)

import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-900 flex flex-col justify-center items-center p-4">
      <div className="bg-white text-gray-900 p-8 rounded-lg shadow-lg max-w-sm w-full text-center">
        
        <h1 className="text-3xl font-bold text-blue-600 mb-4">
          FUNCIONOU!
        </h1>
        
        <p className="text-gray-700 mb-6">
          Se você está vendo esta caixa com fundo branco, cantos arredondados e texto estilizado, o Tailwind CSS está funcionando!
        </p>
        
        <button className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Botão de Teste
        </button>

      </div>
    </div>
  );
}

export default App;
