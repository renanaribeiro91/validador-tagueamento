/**
 * Namespace para organizar o código do dashboard
 * Depende do módulo dashboard-utils.js que deve ser carregado primeiro
 */
const DashboardApp = {
  // Objeto para armazenar dados e estado da aplicação
  state: {
    dados: null,
    mainChart: null,
    dadosFiltrados: null
  },

  /**
   * Módulo para inicialização e configuração da aplicação
   */
  init: {
    /**
     * Inicializa a aplicação
     */
    setup() {
      // Carregar os dados da validação
      DashboardApp.state.dados = window.__DADOS_DASHBOARD__;
      DashboardApp.state.dadosFiltrados = DashboardApp.state.dados;

      // Configurar timestamps
      DashboardApp.init.configurarTimestamps();

      // Inicializar componentes
      DashboardApp.resumo.atualizarContadores();
      DashboardApp.resumo.configurarAnaliseIA();
      DashboardApp.eventos.preencherConteudo();
      DashboardApp.graficos.renderizar('distribuicao');

      // Configurar interatividade
      DashboardApp.ui.configurarAbas();
      DashboardApp.ui.configurarAbasGraficos();
    },

    /**
     * Configura os timestamps do dashboard e da análise de IA
     */
    configurarTimestamps() {
      const agora = new Date();
      const formatoData = {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };

      const dataFormatada = agora.toLocaleDateString('pt-BR', formatoData);
      const ids = DashboardUtils.ELEMENT_IDS;
      
      document.getElementById(ids.DASHBOARD_TIMESTAMP).textContent = dataFormatada;
      document.getElementById(ids.AI_ANALYSIS_TIMESTAMP).textContent = `Atualizado em: ${dataFormatada}`;
    }
  },

  /**
   * Módulo para gerenciar o resumo de dados
   */
  resumo: {
    /**
     * Atualiza os contadores no resumo
     */
    atualizarContadores() {
      const { dadosFiltrados } = DashboardApp.state;
      const ids = DashboardUtils.ELEMENT_IDS;

      this.animarContador(ids.TOTAL_CORRETOS, dadosFiltrados.resumo.corretos);
      this.animarContador(ids.TOTAL_AUSENTES, dadosFiltrados.resumo.ausentes);
      this.animarContador(ids.TOTAL_COM_ERRO, dadosFiltrados.resumo.com_erro);
      this.animarContador(ids.TOTAL_EVENTOS, dadosFiltrados.resumo.total);
    },

    /**
     * Anima a contagem de um valor
     * @param {string} elementId - ID do elemento que mostrará o contador
     * @param {number} valorFinal - Valor final do contador
     */
    animarContador(elementId, valorFinal) {
      const elemento = document.getElementById(elementId);
      const valorAtual = parseInt(elemento.textContent) || 0;
      const incremento = Math.ceil(valorFinal / 25);
      let contador = valorAtual;

      const timer = setInterval(() => {
        contador += incremento;
        if (contador >= valorFinal) {
          elemento.textContent = valorFinal;
          clearInterval(timer);
        } else {
          elemento.textContent = contador;
        }
      }, 20);
    },

    /**
     * Configura a seção de análise de IA
     */
    configurarAnaliseIA() {
      const { dadosFiltrados } = DashboardApp.state;
      const ids = DashboardUtils.ELEMENT_IDS;
      const aiAnalysisEl = document.getElementById(ids.AI_ANALYSIS);
      const aiAnalysisContentEl = document.getElementById(ids.AI_ANALYSIS_CONTENT);

      // Atualizar conteúdo
      aiAnalysisContentEl.textContent = dadosFiltrados.analise_ia ?? 
        'Nenhuma análise de IA disponível para os erros encontrados.';

      // Ocultar análise de IA se não houver erros
      aiAnalysisEl.style.display = (dadosFiltrados.resumo.com_erro === 0 && 
        dadosFiltrados.resumo.ausentes === 0) ? 'none' : 'block';
    }
  },

  /**
   * Módulo para gerenciar gráficos
   */
  graficos: {
    /**
     * Obtém dados para os gráficos a partir dos dados da aplicação
     * @returns {Object} Dados formatados para diferentes tipos de gráficos
     */
    obterDados() {
      const { dadosFiltrados } = DashboardApp.state;

      return {
        distribuicao: {
          labels: ['Corretos', 'Ausentes', 'Com Erros'],
          datasets: [{
            data: [
              dadosFiltrados.resumo.corretos,
              dadosFiltrados.resumo.ausentes,
              dadosFiltrados.resumo.com_erro
            ],
            backgroundColor: ['rgba(39, 174, 96, 0.9)', 'rgba(231, 76, 60, 0.9)', 'rgba(243, 156, 18, 0.9)'],
            borderColor: ['rgba(39, 174, 96, 1)', 'rgba(231, 76, 60, 1)', 'rgba(243, 156, 18, 1)'],
            borderWidth: 2,
            hoverOffset: 15
          }]
        },
        erros: {
          labels: Object.keys(dadosFiltrados.erros_por_campo || {}),
          datasets: [{
            label: 'Quantidade de Erros',
            data: Object.values(dadosFiltrados.erros_por_campo || {}),
            backgroundColor: 'rgba(243, 156, 18, 0.7)',
            borderColor: 'rgba(230, 126, 34, 1)',
            borderWidth: 1,
            borderRadius: 5,
            hoverBackgroundColor: 'rgba(243, 156, 18, 0.9)'
          }]
        },
        telas: {
          labels: Object.keys(dadosFiltrados.eventos_por_tela || {}),
          datasets: [{
            label: 'Quantidade de Eventos',
            data: Object.values(dadosFiltrados.eventos_por_tela || {}),
            backgroundColor: 'rgba(52, 152, 219, 0.7)',
            borderColor: 'rgba(41, 128, 185, 1)',
            borderWidth: 1,
            borderRadius: 5,
            hoverBackgroundColor: 'rgba(52, 152, 219, 0.9)'
          }]
        },
      };
    },

    /**
     * Renderiza um gráfico específico
     * @param {string} tipo - Tipo de gráfico a ser renderizado
     */
    renderizar(tipo) {
      const ids = DashboardUtils.ELEMENT_IDS;
      const ctx = document.getElementById(ids.MAIN_CHART).getContext('2d');
      const chartData = this.obterDados()[tipo];
      const chartConfig = DashboardUtils.graficos.obterConfiguracoes()[tipo];

      // Destruir o gráfico existente se houver
      if (DashboardApp.state.mainChart) {
        DashboardApp.state.mainChart.destroy();
      }

      // Criar o novo gráfico
      DashboardApp.state.mainChart = new Chart(ctx, {
        type: chartConfig.type,
        data: chartData,
        options: chartConfig.options
      });
    }
  },

  /**
   * Módulo para gerenciar eventos e sua exibição
   */
  eventos: {
  
    /**
     * Formata dados de um evento para exibição na UI
     * @param {Object} eventoWrapper - Objeto contendo dados do evento
     * @param {string} tipo - Tipo do evento (correto, ausente, com-erro)
     * @returns {string} HTML formatado para o evento
     */
    formatarEvento(eventoWrapper, tipo) {
      const evento = eventoWrapper?.evento || eventoWrapper;
      const formatadores = DashboardUtils.formatadores;

      // Extrair e normalizar propriedades principais
      const id = formatadores.obterValorPropriedade(evento, ['id', 'ID', 'Id']) ?? 
                formatadores.obterValorPropriedade(eventoWrapper, ['id', 'ID', 'Id'], '');
      
      const nomeEvento = formatadores.obterValorPropriedade(
        evento, 
        ['nome do evento', 'NOME DO EVENTO', 'Nome do Evento', 'nome_evento'], 
        'Evento Sem Nome'
      );

      const tela = formatadores.obterValorPropriedade(
        evento,
        ['tela', 'TELA', 'Tela'],
        'Tela Não Especificada'
      );

      // Obter e formatar timestamp atual
      const timestamp = new Date().toISOString();
      const dataFormatada = formatadores.formatarData(timestamp);
      
      // Gerar identificadores e elementos de UI
      const statusBadge = DashboardUtils.ui.gerarStatusBadge(tipo);
      const eventId = `evento-${tipo}-${id}`;

      // Construir o HTML do evento
      let html = `
        <div class="evento ${tipo}" id="${eventId}" onclick="DashboardApp.ui.toggleEventoDetalhes('${eventId}')">
          <div class="evento-info">
            ${statusBadge}
            <span class="evento-id"><i class="fas fa-fingerprint"></i> ID: ${id}</span>
            <span class="evento-tela"><i class="fas fa-mobile-alt"></i> ${tela}</span>
            <span class="evento-nome"><i class="fas fa-tag"></i> ${nomeEvento}</span>
            <span class="evento-data"><i class="far fa-clock"></i> ${dataFormatada}</span>
          </div>
          <div class="evento-detalhes" id="${eventId}-detalhes">
      `;

      // Adicionar diferenças se for um evento com erro
      if (tipo === 'com-erro' && eventoWrapper.diferencas) {
        html += DashboardUtils.ui.gerarHtmlDiferencas(eventoWrapper.diferencas);
      }

      // Adicionar detalhes completos
      html += DashboardUtils.ui.gerarHtmlDetalhesCompletos(eventoWrapper);

      html += '</div></div>';
      return html;
    },

    /**
     * Preenche os containers de eventos com os dados formatados
     */
    preencherConteudo() {
      const { dadosFiltrados } = DashboardApp.state;
      const ids = DashboardUtils.ELEMENT_IDS;

      // Eventos corretos
      this.preencherContainer(ids.CORRETOS_CONTAINER, dadosFiltrados.eventos.corretos, 'correto');

      // Eventos ausentes
      this.preencherContainer(ids.AUSENTES_CONTAINER, dadosFiltrados.eventos.ausentes, 'ausente');

      // Eventos com erro
      this.preencherContainer(ids.COM_ERRO_CONTAINER, dadosFiltrados.eventos.com_erro, 'com-erro');
    },

    /**
     * Gera conteúdo HTML para um container de eventos
     * @param {Array} eventos - Lista de eventos a serem exibidos
     * @param {string} tipo - Tipo de eventos (correto, ausente, com-erro)
     * @returns {string} HTML gerado para o container
     */
    gerarConteudoContainer(eventos, tipo) {
      if (!eventos || eventos.length === 0) {
        return `<div class="sem-itens"><i class="far fa-smile"></i> Nenhum evento ${tipo.replace('-', ' ')} encontrado.</div>`;
      }
      
      return eventos
        .map(evento => this.formatarEvento(evento, tipo))
        .join('');
    },

    /**
     * Preenche um container específico com eventos formatados
     * @param {string} containerId - ID do container a ser preenchido
     * @param {Array} eventos - Lista de eventos a serem exibidos
     * @param {string} tipo - Tipo de eventos (correto, ausente, com-erro)
     */
    preencherContainer(containerId, eventos, tipo) {
      const container = document.getElementById(containerId);
      container.innerHTML = this.gerarConteudoContainer(eventos, tipo);
    }
  },

  /**
   * Módulo para gerenciar interface do usuário e interações
   */
  ui: {
    /**
     * Configura as abas principais de conteúdo
     */
    configurarAbas() {
      const tabs = document.querySelectorAll('.tab');
      
      tabs.forEach(tab => {
        tab.addEventListener('click', () => {
          // Remover classe active de todas as abas e conteúdos
          document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
          document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

          // Adicionar classe active na aba clicada e no conteúdo correspondente
          const tabId = tab.getAttribute('data-tab');
          tab.classList.add('active');
          document.getElementById(`${tabId}-content`).classList.add('active');
        });
      });
    },

    /**
     * Configura as abas dos gráficos
     */
    configurarAbasGraficos() {
      const chartTabs = document.querySelectorAll('.chart-tab');
      
      chartTabs.forEach(tab => {
        tab.addEventListener('click', () => {
          // Remover classe active de todas as abas
          document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));

          // Adicionar classe active na aba clicada
          tab.classList.add('active');
          
          // Renderizar o gráfico correspondente
          const chartType = tab.getAttribute('data-chart');
          DashboardApp.graficos.renderizar(chartType);
        });
      });
    },

    /**
     * Alterna a visibilidade dos detalhes de um evento
     * @param {string} eventoId - ID do evento cujos detalhes serão alternados
     */
    toggleEventoDetalhes(eventoId) {
      const detalhesEl = document.getElementById(`${eventoId}-detalhes`);

      if (detalhesEl.style.display === 'block') {
        // Fechando os detalhes
        DashboardUtils.ui.resetarAnimacao(detalhesEl, 'slideDown 0.3s ease reverse');

        setTimeout(() => {
          detalhesEl.style.display = 'none';
        }, 280);
      } else {
        // Abrindo os detalhes
        detalhesEl.style.display = 'block';
        detalhesEl.style.animation = 'slideDown 0.3s ease forwards';
      }
    },

    /**
     * Navega para a aba correspondente ao clicar no box de resumo
     * @param {string} tabId - ID da aba de destino
     */
    navegarParaAba(tabId) {
      const ids = DashboardUtils.ELEMENT_IDS;
      
      // 1. Selecionar a aba correspondente
      const tab = document.querySelector(`.tab[data-tab="${tabId}"]`);
      if (!tab) return;

      // 2. Ativar a aba programaticamente
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      
      tab.classList.add('active');
      document.getElementById(`${tabId}-content`).classList.add('active');

      // 3. Rolar até a seção de eventos
      document.getElementById(ids.EVENTOS_CARD).scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  }
};

// Expor funções necessárias para o escopo global
window.DashboardApp = {
  ui: {
    toggleEventoDetalhes: function(eventoId) {
      DashboardApp.ui.toggleEventoDetalhes(eventoId);
    },
    navegarParaAba: function(tabId) {
      DashboardApp.ui.navegarParaAba(tabId);
    }
  }
};

// Inicializar a aplicação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', DashboardApp.init.setup);