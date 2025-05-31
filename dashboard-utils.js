/**
 * Módulo de utilidades para o Dashboard
 * Contém funções auxiliares reutilizáveis
 */
const DashboardUtils = {
  /**
   * Constantes para IDs de elementos
   */
  ELEMENT_IDS: {
    DASHBOARD_TIMESTAMP: 'dashboard-timestamp',
    AI_ANALYSIS_TIMESTAMP: 'ai-analysis-timestamp',
    AI_ANALYSIS: 'ai-analysis',
    AI_ANALYSIS_CONTENT: 'ai-analysis-content',
    MAIN_CHART: 'main-chart',
    CORRETOS_CONTAINER: 'corretos-container',
    AUSENTES_CONTAINER: 'ausentes-container',
    COM_ERRO_CONTAINER: 'com-erro-container',
    DATE_START: 'date-start',
    DATE_END: 'date-end',
    APPLY_FILTER: 'apply-filter',
    EVENTOS_CARD: 'eventos-card',
    TOTAL_CORRETOS: 'total-corretos',
    TOTAL_AUSENTES: 'total-ausentes',
    TOTAL_COM_ERRO: 'total-com-erro',
    TOTAL_EVENTOS: 'total-eventos'
  },

  /**
   * Formatadores e transformadores de dados
   */
  formatadores: {
    /**
     * Formata data para exibição
     * @param {string} dataStr - String de data a ser formatada
     * @returns {string} Data formatada
     */
    formatarData(dataStr) {
      if (!dataStr) return 'N/A';

      try {
        const data = new Date(dataStr);
        if (isNaN(data.getTime())) {
          throw new Error('Invalid date format');
        }
        return data.toLocaleDateString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });
      } catch (e) {
        console.warn(`Error formatting date: ${e.message}`);
        return dataStr;
      }
    },
    
    /**
     * Converte objeto para string JSON de forma segura
     * @param {*} valor - Valor a ser convertido
     * @returns {string} Representação do valor como string
     */
    converterParaString(valor) {
      if (typeof valor === 'object' && valor !== null) {
        try {
          return JSON.stringify(valor, null, 2);
        } catch {
          return '[Objeto complexo]';
        }
      }
      return String(valor);
    },

    /**
     * Extrai propriedade de objeto independente de case-sensitivity
     * @param {Object} obj - Objeto a ser inspecionado
     * @param {string[]} possiveisPropNames - Possíveis nomes da propriedade
     * @param {*} valorPadrao - Valor padrão caso a propriedade não seja encontrada
     * @returns {*} Valor da propriedade ou valor padrão
     */
    obterValorPropriedade(obj, possiveisPropNames, valorPadrao) {
      // Verificação rápida para evitar trabalho desnecessário
      if (!obj || typeof obj !== 'object') {
        return valorPadrao;
      }
      
      // Lista de possíveis variações de case
      const variacoes = possiveisPropNames.flatMap(propName => [
        propName.toLowerCase(),
        propName.toUpperCase(),
        propName.charAt(0).toUpperCase() + propName.slice(1).toLowerCase(),
        propName
      ]);

      // Tenta encontrar qualquer variação da propriedade
      for (const prop of variacoes) {
        if (obj[prop] !== undefined) {
          return obj[prop];
        }
      }

      return valorPadrao;
    }
  },

  /**
   * Funções para geração de componentes UI
   */
  ui: {
    /**
     * Gera o badge de status para o evento
     * @param {string} tipo - Tipo do evento
     * @returns {string} HTML do badge
     */
    gerarStatusBadge(tipo) {
      const statusMap = {
        'correto': { texto: 'Correto', icone: 'check' },
        'ausente': { texto: 'Ausente', icone: 'times' },
        'com-erro': { texto: 'Com Erro', icone: 'exclamation' }
      };
      
      const { texto, icone } = statusMap[tipo] || { texto: '', icone: '' };
      
      return `<span class="evento-badge ${tipo}"><i class="fas fa-${icone}"></i> ${texto}</span>`;
    },

    /**
     * Gera HTML para mostrar diferenças encontradas
     * @param {Object} diferencas - Objeto com diferenças encontradas
     * @returns {string} HTML formatado para exibir as diferenças
     */
    gerarHtmlDiferencas(diferencas) {
      const titulo = '<div class="evento-detalhes-titulo"><i class="fas fa-not-equal"></i> Diferenças Encontradas</div>';
      
      const diferencasHtml = Object.entries(diferencas).map(([campo, diferenca]) => `
        <div class="diferenca">
          <div class="diferenca-titulo"><i class="fas fa-exclamation-triangle"></i> ${campo}</div>
          <div class="valores">
            <div class="valor-label"><i class="fas fa-check-circle"></i> Esperado:</div>
            <div class="valor-conteudo valor-esperado">${diferenca.esperado}</div>
            <div class="valor-label"><i class="fas fa-times-circle"></i> Log:</div>
            <div class="valor-conteudo valor-log">${diferenca.log}</div>
          </div>
        </div>
      `).join('');
      
      return `${titulo}<div class="diferencas">${diferencasHtml}</div>`;
    },

 /**
 * Gera HTML para mostrar detalhes completos do evento
 * @param {Object} eventoWrapper - Objeto completo do evento
 * @returns {string} HTML formatado para exibir detalhes
 */
gerarHtmlDetalhesCompletos(eventoWrapper) {
  const titulo = '<div class="evento-detalhes-titulo"><i class="fas fa-info-circle"></i> Detalhes Completos</div>';
  let html = '<div class="evento-detalhes-tabela">';
  
  // Função para processar um objeto e gerar linhas da tabela
  const processarObjeto = (obj, prefix = '') => {
    let result = '';
    
    // Obtém evento do wrapper se existir
    const evento = obj.evento || obj;
    
    // Para objetos "evento" e "log", formata de maneira especial
    if (obj.evento && obj.log && prefix === '') {
      // Primeiro processa os campos do evento
      Object.entries(evento).forEach(([campo, valor]) => {
        const valorFormatado = typeof valor === 'object' && valor !== null ? 
          JSON.stringify(valor) : String(valor);
        
        result += `
          <div class="evento-detalhes-item">
            <div class="evento-detalhes-chave">${campo.toUpperCase()}:</div>
            <div class="evento-detalhes-valor">${valorFormatado}</div>
          </div>
        `;
      });
      
      // Depois processa os campos do log, mas apenas se não estiver nas diferenças
      if (!obj.diferencas) {
        result += `
          <div class="evento-detalhes-item evento-detalhes-separator">
            <div class="evento-detalhes-chave">LOG:</div>
            <div class="evento-detalhes-valor"></div>
          </div>
        `;
        
        Object.entries(obj.log).forEach(([campo, valor]) => {
          const valorFormatado = typeof valor === 'object' && valor !== null ? 
            JSON.stringify(valor) : String(valor);
          
          result += `
            <div class="evento-detalhes-item">
              <div class="evento-detalhes-chave">${campo.toUpperCase()}:</div>
              <div class="evento-detalhes-valor">${valorFormatado}</div>
            </div>
          `;
        });
      }
    } else {
      // Para outros objetos, processa normalmente cada campo
      Object.entries(obj).forEach(([campo, valor]) => {
        // Pula campos especiais que serão tratados separadamente
        if (campo === 'diferencas' || campo === 'evento' || campo === 'log') {
          return;
        }
        
        const campoFormatado = prefix + campo.toUpperCase();
        const valorFormatado = typeof valor === 'object' && valor !== null ? 
          JSON.stringify(valor) : String(valor);
        
        result += `
          <div class="evento-detalhes-item">
            <div class="evento-detalhes-chave">${campoFormatado}:</div>
            <div class="evento-detalhes-valor">${valorFormatado}</div>
          </div>
        `;
      });
    }
    
    return result;
  };
  
  html += processarObjeto(eventoWrapper);
  html += '</div>';
  
  return titulo + html;
}
  },

  /**
   * Funções para manipulação de dados de gráficos
   */
  graficos: {
    /**
     * Obtém configurações para os gráficos
     * @returns {Object} Configurações para diferentes tipos de gráficos
     */
    obterConfiguracoes() {
      return {
        distribuicao: {
          type: 'doughnut',
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'right',
                labels: {
                  font: {
                    family: 'Poppins',
                    size: 13
                  },
                  padding: 15
                }
              },
              title: {
                display: true,
                text: 'Distribuição de Status dos Eventos',
                font: {
                  family: 'Poppins',
                  size: 16,
                  weight: '500'
                },
                padding: {
                  bottom: 20
                }
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || '';
                    const value = context.raw || 0;
                    const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                    const percentage = Math.round((value / total) * 100);
                    return `${label}: ${value} (${percentage}%)`;
                  }
                }
              }
            },
            animation: {
              animateScale: true,
              animateRotate: true,
              duration: 2000,
              easing: 'easeOutQuart'
            },
            cutout: '60%'
          }
        },
        erros: {
          type: 'bar',
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  precision: 0,
                  font: { family: 'Poppins' }
                },
                grid: { color: 'rgba(0,0,0,0.05)' }
              },
              x: {
                ticks: { font: { family: 'Poppins' } },
                grid: { display: false }
              }
            },
            plugins: {
              legend: { display: false },
              title: {
                display: true,
                text: 'Distribuição de Erros por Campo',
                font: {
                  family: 'Poppins',
                  size: 16,
                  weight: '500'
                },
                padding: { bottom: 20 }
              }
            },
            animation: {
              duration: 1500,
              easing: 'easeInOutQuart'
            }
          }
        },
        telas: {
          type: 'bar',
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  precision: 0,
                  font: { family: 'Poppins' }
                },
                grid: { color: 'rgba(0,0,0,0.05)' }
              },
              x: {
                ticks: { font: { family: 'Poppins' } },
                grid: { display: false }
              }
            },
            plugins: {
              legend: { display: false },
              title: {
                display: true,
                text: 'Quantidade de Eventos por Tela',
                font: {
                  family: 'Poppins',
                  size: 16,
                  weight: '500'
                },
                padding: { bottom: 20 }
              }
            },
            animation: {
              duration: 1500,
              easing: 'easeInOutQuart'
            }
          }
        },
      };
    }
  }
};

// Exportar para uso global
window.DashboardUtils = DashboardUtils;