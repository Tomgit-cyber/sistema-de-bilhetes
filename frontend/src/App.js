import React, { useState, useEffect } from 'react';
import { Button } from './components/ui/button.jsx';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card.jsx';
import { Badge } from './components/ui/badge.jsx';
import { Separator } from './components/ui/separator.jsx';
import { ArrowLeft, Plus, Trash2, Trophy, DollarSign, LogOut, Wallet, History } from 'lucide-react';
import './App.css';
import Login from './components/Login.jsx';
import Register from './components/Register.jsx';
import api from './api';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authScreen, setAuthScreen] = useState('login');
  const [telaAtual, setTelaAtual] = useState('home');
  const [numerosSelecionados, setNumerosSelecionados] = useState([]);
  const [sorteioAtual, setSorteioAtual] = useState(null);
  const [minhasApostas, setMinhasApostas] = useState([]);
  const [comprovante, setComprovante] = useState(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await api.getCurrentUser();
        setCurrentUser(response.user);
        await carregarDados();
      } catch (error) {
        console.error('Nenhum usuário logado', error);
        setCurrentUser(null);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const carregarDados = async () => {
    try {
      const sorteio = await api.getCurrentSorteio();
      setSorteioAtual(sorteio.sorteio);
      
      const apostas = await api.getMyApostas();
      setMinhasApostas(apostas);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setTelaAtual('home');
    carregarDados();
  };

  const handleRegisterSuccess = () => {
    alert('Registro bem-sucedido! Faça login para continuar.');
    setAuthScreen('login');
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      setCurrentUser(null);
      setTelaAtual('home');
      setAuthScreen('login');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      alert('Erro ao fazer logout.');
    }
  };

  const selecionarNumero = (numero) => {
    if (numerosSelecionados.includes(numero)) {
      setNumerosSelecionados(numerosSelecionados.filter(n => n !== numero));
    } else if (numerosSelecionados.length < 2) {
      setNumerosSelecionados([...numerosSelecionados, numero]);
    } else {
      alert('Você pode selecionar apenas 2 números!');
    }
  };

  const limparSelecao = () => {
    setNumerosSelecionados([]);
  };

  const fazerAposta = async () => {
    if (numerosSelecionados.length !== 2) {
      alert('Você deve selecionar exatamente 2 números!');
      return;
    }

    if (currentUser.saldo < 2.0) {
      alert('Saldo insuficiente! Você precisa de R$ 2,00 para fazer uma aposta.');
      return;
    }

    try {
      const response = await api.makeAposta(numerosSelecionados);
      setComprovante(response.comprovante);
      setTelaAtual('comprovante');
      
      // Atualizar dados
      const userResponse = await api.getCurrentUser();
      setCurrentUser(userResponse.user);
      await carregarDados();
      
      // Limpar seleção
      setNumerosSelecionados([]);
      
    } catch (error) {
      console.error('Erro ao fazer aposta:', error);
      alert(error.message || 'Erro ao fazer aposta');
    }
  };

  const adicionarSaldo = async () => {
    const valor = prompt('Digite o valor a ser adicionado (R$):');
    if (valor && !isNaN(valor) && parseFloat(valor) > 0) {
      try {
        await api.addBalance(parseFloat(valor));
        const userResponse = await api.getCurrentUser();
        setCurrentUser(userResponse.user);
        alert('Saldo adicionado com sucesso!');
      } catch (error) {
        console.error('Erro ao adicionar saldo:', error);
        alert('Erro ao adicionar saldo');
      }
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-xl">Carregando...</div>;
  }

  if (!currentUser) {
    return authScreen === 'login' ? (
      <Login onLoginSuccess={handleLoginSuccess} onSwitchToRegister={() => setAuthScreen('register')} />
    ) : (
      <Register onRegisterSuccess={handleRegisterSuccess} onSwitchToLogin={() => setAuthScreen('login')} />
    );
  }

  // Tela Principal
  if (telaAtual === 'home') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800">2 pra 500</h1>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-600">Olá, {currentUser.nome}</p>
                <p className="text-lg font-bold text-green-600">R$ {currentUser.saldo?.toFixed(2) || '0,00'}</p>
              </div>
              <Button variant="outline" onClick={adicionarSaldo}>
                <Wallet className="w-4 h-4 mr-2" />
                Adicionar Saldo
              </Button>
              <Button variant="outline" onClick={() => setTelaAtual('historico')}>
                <History className="w-4 h-4 mr-2" />
                Histórico
              </Button>
              <Button variant="outline" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>

          {/* Informações do Sorteio */}
          {sorteioAtual && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-yellow-500" />
                  Sorteio de Hoje - {new Date(sorteioAtual.data_sorteio).toLocaleDateString('pt-BR')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Prêmio</p>
                    <p className="text-2xl font-bold text-green-600">R$ 500,00</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Total de Apostas</p>
                    <p className="text-2xl font-bold">{sorteioAtual.total_apostas || 0}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Status</p>
                    <Badge variant={sorteioAtual.status === 'aberto' ? 'default' : 'secondary'}>
                      {sorteioAtual.status === 'aberto' ? 'Aberto' : 'Finalizado'}
                    </Badge>
                  </div>
                </div>
                {sorteioAtual.numeros_sorteados && sorteioAtual.numeros_sorteados.length > 0 && (
                  <div className="mt-4 text-center">
                    <p className="text-sm text-gray-600 mb-2">Números Sorteados:</p>
                    <div className="flex justify-center gap-2">
                      {sorteioAtual.numeros_sorteados.map((numero, index) => (
                        <Badge key={index} variant="secondary" className="text-lg px-4 py-2">
                          {numero.toString().padStart(2, '0')}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Seleção de Números */}
          <Card>
            <CardHeader>
              <CardTitle>Escolha seus 2 números (1-60)</CardTitle>
              <p className="text-sm text-gray-600">Cada aposta custa R$ 2,00</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-10 gap-2 mb-6">
                {Array.from({ length: 60 }, (_, i) => i + 1).map((numero) => (
                  <Button
                    key={numero}
                    variant={numerosSelecionados.includes(numero) ? "default" : "outline"}
                    className="aspect-square p-0"
                    onClick={() => selecionarNumero(numero)}
                  >
                    {numero.toString().padStart(2, '0')}
                  </Button>
                ))}
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Números selecionados:</p>
                    <div className="flex gap-1 mt-1">
                      {numerosSelecionados.length === 0 ? (
                        <span className="text-gray-400">Nenhum</span>
                      ) : (
                        numerosSelecionados.map((numero, index) => (
                          <Badge key={index} variant="secondary">
                            {numero.toString().padStart(2, '0')}
                          </Badge>
                        ))
                      )}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Valor:</p>
                    <p className="text-lg font-bold text-green-600">
                      R$ {numerosSelecionados.length === 2 ? '2,00' : '0,00'}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={limparSelecao}>
                    Limpar
                  </Button>
                  <Button 
                    onClick={fazerAposta}
                    disabled={numerosSelecionados.length !== 2 || currentUser.saldo < 2.0}
                  >
                    Apostar R$ 2,00
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Tela de Histórico
  if (telaAtual === 'historico') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-6">
            <Button variant="outline" onClick={() => setTelaAtual('home')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar
            </Button>
            <h1 className="text-3xl font-bold text-gray-800">Minhas Apostas</h1>
          </div>

          <div className="space-y-4">
            {minhasApostas.length === 0 ? (
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-gray-500">Você ainda não fez nenhuma aposta.</p>
                </CardContent>
              </Card>
            ) : (
              minhasApostas.map((aposta) => (
                <Card key={aposta.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div>
                          <p className="font-semibold">Aposta #{aposta.id}</p>
                          <p className="text-sm text-gray-600">
                            {new Date(aposta.data_criacao).toLocaleDateString('pt-BR')} às{' '}
                            {new Date(aposta.data_criacao).toLocaleTimeString('pt-BR')}
                          </p>
                        </div>
                        <div className="flex gap-1">
                          {aposta.numeros_escolhidos.map((numero, index) => (
                            <Badge key={index} variant="secondary">
                              {numero.toString().padStart(2, '0')}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">R$ {aposta.valor_aposta.toFixed(2)}</p>
                        <Badge 
                          variant={
                            aposta.status === 'ganhadora' ? 'default' : 
                            aposta.status === 'perdedora' ? 'destructive' : 'secondary'
                          }
                        >
                          {aposta.status === 'ganhadora' ? 'Ganhadora' : 
                           aposta.status === 'perdedora' ? 'Perdedora' : 'Ativa'}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
      </div>
    );
  }

  // Tela de Comprovante
  if (telaAtual === 'comprovante' && comprovante) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-4">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-green-800 mb-2">Aposta Realizada!</h1>
            <p className="text-green-600">Sua aposta foi registrada com sucesso</p>
          </div>

          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-xl">Comprovante de Aposta</CardTitle>
              <p className="text-sm text-gray-500">#{comprovante.id}</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <p className="text-sm text-gray-600">Data: {comprovante.data}</p>
                <p className="text-sm text-gray-600">Usuário: {comprovante.usuario}</p>
              </div>

              <Separator />

              <div className="text-center">
                <h3 className="font-semibold mb-3">Seus Números:</h3>
                <div className="flex justify-center gap-2 mb-4">
                  {comprovante.numeros.map((numero, index) => (
                    <Badge key={index} variant="secondary" className="text-lg px-4 py-2">
                      {numero.toString().padStart(2, '0')}
                    </Badge>
                  ))}
                </div>
              </div>

              <Separator />

              <div className="flex justify-between items-center text-lg font-bold">
                <span>Valor Pago:</span>
                <span className="text-green-600">{comprovante.valor}</span>
              </div>

              <div className="text-center text-sm text-gray-600">
                <p>Sorteio: {comprovante.sorteio_data}</p>
                <p className="mt-2">Boa sorte! O resultado será divulgado às 20:00h.</p>
              </div>

              <div className="flex gap-2">
                <Button 
                  className="flex-1" 
                  onClick={() => setTelaAtual('home')}
                >
                  Fazer Nova Aposta
                </Button>
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => setTelaAtual('historico')}
                >
                  Ver Histórico
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return null;
}

export default App;

