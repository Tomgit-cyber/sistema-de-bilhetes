import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { ArrowLeft, Plus, Trash2, MessageCircle, Printer, Trophy, DollarSign, User, LogOut, LogIn } from 'lucide-react'
import api from './api.js'
import './App.css'

function App() {
  const [telaAtual, setTelaAtual] = useState('login')
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  // Estados para apostas
  const [sorteioAtual, setSorteioAtual] = useState(null)
  const [numerosDisponiveis, setNumerosDisponiveis] = useState([])
  const [apostasHoje, setApostasHoje] = useState([])
  const [numeroSelecionado, setNumeroSelecionado] = useState('')
  
  // Estados para formulários
  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [registerForm, setRegisterForm] = useState({ nome: '', email: '', telefone: '', password: '' })

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await api.getCurrentUser()
      setUser(response.user)
      setTelaAtual('apostas')
      loadDashboardData()
    } catch (error) {
      setTelaAtual('login')
    }
  }

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [sorteioResponse, numerosResponse, apostasResponse] = await Promise.all([
        api.getCurrentSorteio(),
        api.getAvailableNumbers(),
        api.getTodayApostas()
      ])
      
      setSorteioAtual(sorteioResponse.sorteio)
      setNumerosDisponiveis(numerosResponse.numeros_disponiveis)
      setApostasHoje(apostasResponse.apostas)
    } catch (error) {
      setError('Erro ao carregar dados: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      setLoading(true)
      setError('')
      const response = await api.login(loginForm)
      setUser(response.user)
      setSuccess('Login realizado com sucesso!')
      setTelaAtual('apostas')
      loadDashboardData()
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    try {
      setLoading(true)
      setError('')
      const response = await api.register(registerForm)
      setUser(response.user)
      setSuccess('Cadastro realizado com sucesso!')
      setTelaAtual('apostas')
      loadDashboardData()
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await api.logout()
      setUser(null)
      setTelaAtual('login')
      setSorteioAtual(null)
      setNumerosDisponiveis([])
      setApostasHoje([])
    } catch (error) {
      setError('Erro ao fazer logout: ' + error.message)
    }
  }

  const handleMakeAposta = async () => {
    if (!numeroSelecionado || numeroSelecionado < 1 || numeroSelecionado > 500) {
      setError('Selecione um número válido entre 1 e 500')
      return
    }

    try {
      setLoading(true)
      setError('')
      const response = await api.makeAposta(parseInt(numeroSelecionado))
      setSuccess(`Aposta realizada no número ${numeroSelecionado}!`)
      setNumeroSelecionado('')
      
      // Atualiza os dados
      await loadDashboardData()
      
      // Atualiza o saldo do usuário
      const userResponse = await api.getCurrentUser()
      setUser(userResponse.user)
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const addBalance = async (valor) => {
    try {
      setLoading(true)
      setError('')
      await api.addBalance(valor)
      setSuccess(`R$ ${valor.toFixed(2)} adicionados ao saldo!`)
      
      // Atualiza o saldo do usuário
      const userResponse = await api.getCurrentUser()
      setUser(userResponse.user)
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  // Componente de Login
  const TelaLogin = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-blue-600">2 pra 500</CardTitle>
          <p className="text-gray-600">Faça login para apostar</p>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
              {success}
            </div>
          )}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={loginForm.email}
                onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                required
              />
            </div>
            <div>
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
          <div className="mt-4 text-center">
            <Button 
              variant="link" 
              onClick={() => setTelaAtual('register')}
              className="text-blue-600"
            >
              Não tem conta? Cadastre-se
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  // Componente de Cadastro
  const TelaCadastro = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-blue-600">Cadastro</CardTitle>
          <p className="text-gray-600">Crie sua conta para apostar</p>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <Label htmlFor="nome">Nome</Label>
              <Input
                id="nome"
                type="text"
                value={registerForm.nome}
                onChange={(e) => setRegisterForm({...registerForm, nome: e.target.value})}
                required
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                required
              />
            </div>
            <div>
              <Label htmlFor="telefone">Telefone</Label>
              <Input
                id="telefone"
                type="tel"
                value={registerForm.telefone}
                onChange={(e) => setRegisterForm({...registerForm, telefone: e.target.value})}
                required
              />
            </div>
            <div>
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                value={registerForm.password}
                onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Cadastrando...' : 'Cadastrar'}
            </Button>
          </form>
          <div className="mt-4 text-center">
            <Button 
              variant="link" 
              onClick={() => setTelaAtual('login')}
              className="text-blue-600"
            >
              Já tem conta? Faça login
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  // Componente principal de apostas
  const TelaApostas = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-blue-600">2 pra 500</h1>
            {sorteioAtual && (
              <Badge variant="outline" className="text-green-600 border-green-600">
                Sorteio: {new Date(sorteioAtual.data_sorteio).toLocaleDateString('pt-BR')}
              </Badge>
            )}
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <User className="h-4 w-4" />
              <span className="font-medium">{user?.nome}</span>
            </div>
            <div className="flex items-center space-x-2">
              <DollarSign className="h-4 w-4 text-green-600" />
              <span className="font-bold text-green-600">R$ {user?.saldo?.toFixed(2) || '0.00'}</span>
            </div>
            <Button variant="outline" size="sm" onClick={() => addBalance(10)}>
              +R$ 10
            </Button>
            <Button variant="outline" size="sm" onClick={() => addBalance(50)}>
              +R$ 50
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 space-y-6">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Informações do Sorteio */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Trophy className="h-5 w-5 text-yellow-500" />
                <span>Sorteio Atual</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {sorteioAtual ? (
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Data do Sorteio</p>
                    <p className="font-bold">{new Date(sorteioAtual.data_sorteio).toLocaleDateString('pt-BR')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Arrecadado</p>
                    <p className="font-bold text-green-600">R$ {sorteioAtual.total_arrecadado?.toFixed(2) || '0.00'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Prêmio Estimado (90%)</p>
                    <p className="font-bold text-blue-600">R$ {(sorteioAtual.total_arrecadado * 0.9)?.toFixed(2) || '0.00'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total de Apostas</p>
                    <p className="font-bold">{sorteioAtual.total_apostas || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Status</p>
                    <Badge variant={sorteioAtual.status === 'aberto' ? 'default' : 'secondary'}>
                      {sorteioAtual.status === 'aberto' ? 'Aberto' : sorteioAtual.status}
                    </Badge>
                  </div>
                  {sorteioAtual.numero_sorteado && (
                    <div>
                      <p className="text-sm text-gray-600">Número Sorteado</p>
                      <p className="text-2xl font-bold text-red-600">{sorteioAtual.numero_sorteado}</p>
                    </div>
                  )}
                </div>
              ) : (
                <p>Carregando informações do sorteio...</p>
              )}
            </CardContent>
          </Card>

          {/* Fazer Aposta */}
          <Card>
            <CardHeader>
              <CardTitle>Fazer Aposta</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="numero">Escolha um número (1-500)</Label>
                  <Input
                    id="numero"
                    type="number"
                    min="1"
                    max="500"
                    value={numeroSelecionado}
                    onChange={(e) => setNumeroSelecionado(e.target.value)}
                    placeholder="Digite um número"
                  />
                </div>
                <div className="bg-blue-50 p-3 rounded">
                  <p className="text-sm text-blue-800">
                    <strong>Valor da aposta:</strong> R$ 2,00<br />
                    <strong>Seu saldo:</strong> R$ {user?.saldo?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <Button 
                  onClick={handleMakeAposta} 
                  className="w-full" 
                  disabled={loading || !numeroSelecionado || (user?.saldo || 0) < 2}
                >
                  {loading ? 'Apostando...' : 'Apostar R$ 2,00'}
                </Button>
                {(user?.saldo || 0) < 2 && (
                  <p className="text-sm text-red-600">Saldo insuficiente. Adicione créditos para apostar.</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Minhas Apostas de Hoje */}
          <Card>
            <CardHeader>
              <CardTitle>Minhas Apostas de Hoje</CardTitle>
            </CardHeader>
            <CardContent>
              {apostasHoje.length > 0 ? (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {apostasHoje.map((aposta) => (
                    <div key={aposta.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span className="font-bold text-lg">{aposta.numero_escolhido}</span>
                      <div className="text-right">
                        <p className="text-sm text-gray-600">R$ {aposta.valor_aposta.toFixed(2)}</p>
                        <Badge variant={
                          aposta.status === 'ganhadora' ? 'default' : 
                          aposta.status === 'perdedora' ? 'destructive' : 'secondary'
                        }>
                          {aposta.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">Nenhuma aposta feita hoje</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Botões de navegação */}
        <div className="flex justify-center space-x-4">
          <Button variant="outline" onClick={() => setTelaAtual('historico')}>
            Ver Histórico
          </Button>
          <Button variant="outline" onClick={() => setTelaAtual('estatisticas')}>
            Estatísticas
          </Button>
        </div>
      </div>
    </div>
  )

  // Renderização condicional baseada na tela atual
  const renderTela = () => {
    switch (telaAtual) {
      case 'login':
        return <TelaLogin />
      case 'register':
        return <TelaCadastro />
      case 'apostas':
        return <TelaApostas />
      default:
        return <TelaLogin />
    }
  }

  return renderTela()
}

export default App

