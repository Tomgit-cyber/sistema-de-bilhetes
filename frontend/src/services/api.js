// Local: frontend/src/services/api.js

// Configuração da API para comunicação com o backend
const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  constructor( ) {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Método central para fazer requisições à API.
   * @param {string} endpoint - O endpoint da API (ex: '/apostas/modalidades').
   * @param {object} options - Opções da requisição (method, headers, body, etc.).
   * @returns {Promise<any>} - A resposta da API em formato JSON.
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    // Configuração padrão para todas as requisições
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        // Se a resposta não for OK (status 2xx), lança um erro com a mensagem do backend
        throw new Error(data.error || 'Ocorreu um erro na comunicação com o servidor.');
      }

      return data;
    } catch (error) {
      console.error('Erro na chamada da API:', error);
      // Re-lança o erro para que o componente que chamou a função possa tratá-lo
      throw error;
    }
  }
}

// Cria uma instância única da classe para ser usada em toda a aplicação
const api = new ApiService();

export default api;
