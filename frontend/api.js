// Configuração da API para comunicação com o backend
const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Para incluir cookies de sessão
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Erro na requisição');
      }

      return data;
    } catch (error) {
      console.error('Erro na API:', error);
      throw error;
    }
  }

  // Métodos de autenticação
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async logout() {
    return this.request('/auth/logout', {
      method: 'POST',
    });
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  // Métodos de usuário
  async getUserProfile() {
    return this.request('/user/perfil');
  }

  async updateProfile(profileData) {
    return this.request('/user/perfil', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async changePassword(passwordData) {
    return this.request('/user/alterar-senha', {
      method: 'PUT',
      body: JSON.stringify(passwordData),
    });
  }

  async getUserBalance() {
    return this.request('/user/saldo');
  }

  async addBalance(amount) {
    return this.request('/user/adicionar-saldo', {
      method: 'POST',
      body: JSON.stringify({ valor: amount }),
    });
  }

  async getTransactionHistory(page = 1, perPage = 20) {
    return this.request(`/user/historico-transacoes?page=${page}&per_page=${perPage}`);
  }

  // Métodos de apostas
  async makeAposta(numero) {
    return this.request('/apostas/fazer-aposta', {
      method: 'POST',
      body: JSON.stringify({ numero }),
    });
  }

  async getMyApostas(page = 1, perPage = 10) {
    return this.request(`/apostas/minhas-apostas?page=${page}&per_page=${perPage}`);
  }

  async getTodayApostas() {
    return this.request('/apostas/apostas-hoje');
  }

  async getAvailableNumbers() {
    return this.request('/apostas/numeros-disponiveis');
  }

  // Métodos de sorteios
  async getCurrentSorteio() {
    return this.request('/sorteios/sorteio-atual');
  }

  async getSorteioHistory(page = 1, perPage = 10) {
    return this.request(`/sorteios/historico?page=${page}&per_page=${perPage}`);
  }

  async getSorteioResult(sorteioId) {
    return this.request(`/sorteios/resultado/${sorteioId}`);
  }

  async getStatistics() {
    return this.request('/sorteios/estatisticas');
  }

  // Métodos administrativos (se necessário)
  async executeManualSorteio(dataSorteio = null) {
    const body = dataSorteio ? { data_sorteio: dataSorteio } : {};
    return this.request('/admin/executar-sorteio', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getSchedulerStatus() {
    return this.request('/admin/status-scheduler');
  }

  async getAdminStatistics() {
    return this.request('/admin/estatisticas-admin');
  }
}

// Instância global da API
const api = new ApiService();

export default api;

