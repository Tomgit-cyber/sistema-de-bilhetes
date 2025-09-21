// Local: frontend/src/App.jsx (Versão Robusta)

import React, { useState, useEffect } from 'react';
// Supondo que você tenha um api.js em src/services/
import api from './services/api'; 
// Supondo que você tenha componentes de Login e Register
import Login from './components/Login'; 
import Register from './components/Register';

// Um componente simples para o painel principal
function Dashboard({ user, onLogout }) {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Bem-vindo, {user.nome}!</h1>
          <button 
            onClick={onLogout}
            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            Sair
          </button>
        </div>
        <p>Seu saldo atual é: <span className="font-semibold">R$ {user.saldo.toFixed(2)}</span></p>
        {/* Aqui entrarão os componentes de aposta, histórico, etc. */}
      </div>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tela, setTela] = useState('login'); // 'login' ou 'register'

  // Função para verificar a autenticação quando o App carrega
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Tenta buscar o usuário logado
        const userData = await api.getCurrentUser();
        if (userData && userData.user) {
          setUser(userData.user);
        }
      } catch (error) {
        // Se falhar (ex: token expirado ou backend offline), não faz nada.
        // O usuário continuará como 'null'.
        console.log("Nenhum usuário logado ou erro na verificação:", error.message);
      } finally {
        // Independentemente do resultado, para de carregar
        setLoading(false);
      }
    };

    checkAuth();
  }, []); // O array vazio [] garante que isso rode apenas uma vez

  const handleLogin = (loggedInUser) => {
    setUser(loggedInUser);
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (error) {
      console.error("Erro ao fazer logout:", error);
    } finally {
      setUser(null);
      setTela('login');
    }
  };

  // Se ainda estiver verificando a autenticação, mostra uma tela de loading
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-200 flex justify-center items-center">
        <p className="text-xl">Carregando...</p>
      </div>
    );
  }

  // Se não houver usuário logado, mostra Login ou Registro
  if (!user) {
    if (tela === 'login') {
      return <Login onLogin={handleLogin} onNavigateToRegister={() => setTela('register')} />;
    }
    if (tela === 'register') {
      return <Register onNavigateToLogin={() => setTela('login')} />;
    }
  }

  // Se houver um usuário logado, mostra o Dashboard
  return <Dashboard user={user} onLogout={handleLogout} />;
}

export default App;
