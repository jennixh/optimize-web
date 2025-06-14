class MolecularSystem {
    // ... seu código do MolecularSystem aqui (sem mudanças) ...
}

// Inicializa o sistema molecular assim que o script roda
new MolecularSystem();

// Efeitos de hover nos botões
document.querySelectorAll('.btn-primary, .btn-secondary').forEach(btn => {
    btn.addEventListener('mouseenter', function () {
        this.style.transform = 'translateY(-3px) scale(1.05)';
    });
    btn.addEventListener('mouseleave', function () {
        this.style.transform = 'translateY(0) scale(1)';
    });
});

// Sistema de Métodos de Programação Linear
class LinearProgrammingMethods {
    constructor() {
        this.currentMethod = null;
        this.init();
    }

    init() {
        this.createSolverContainers();
        this.addEventListeners();
    }

    createSolverContainers() {
        const container = document.querySelector('.container');

        const solverSection = document.createElement('div');
        solverSection.className = 'solver-section';
        solverSection.innerHTML = `
            <div id="graficoSolver" class="solver-container">
                ${this.createGraficoForm()}
            </div>
            <div id="simplexSolver" class="solver-container">
                ${this.createSimplexForm()}
            </div>
            <div id="bigmSolver" class="solver-container">
                ${this.createBigMForm()}
            </div>
            <div id="minimizacaoSolver" class="solver-container">
                ${this.createMinimizacaoForm()}
            </div>
        `;

        container.appendChild(solverSection);
    }

    createGraficoForm() {
        return `
            <div class="solver-header">
                <h2><i class="fas fa-chart-line"></i> Método Gráfico</h2>
                <p>Para problemas com exatamente 2 variáveis (X₁ e X₂)</p>
            </div>
            <div class="form-section">
                <h3>Função Objetivo</h3>
                <div class="objective-function">
                    <select id="grafico-objetivo-tipo">
                        <option value="max">Maximizar</option>
                        <option value="min">Minimizar</option>
                    </select>
                    <span>Z = </span>
                    <input type="number" id="grafico-c1" placeholder="C₁" step="any">
                    <span>X₁ + </span>
                    <input type="number" id="grafico-c2" placeholder="C₂" step="any">
                    <span>X₂</span>
                </div>
            </div>
            <div class="form-section">
                <h3>Restrições</h3>
                <div id="grafico-restricoes">
                    <div class="restricao-row">
                        <input type="number" placeholder="a₁₁" step="any">
                        <span>X₁ + </span>
                        <input type="number" placeholder="a₁₂" step="any">
                        <span>X₂ ≤ </span>
                        <input type="number" placeholder="b₁" step="any">
                        <button type="button" class="btn-remove" onclick="this.parentElement.remove()">×</button>
                    </div>
                </div>
                <button type="button" class="btn-add" onclick="linearProgramming.addGraficoRestriction()">
                    <i class="fas fa-plus"></i> Adicionar Restrição
                </button>
            </div>
            <div class="solver-actions">
                <button type="button" class="btn-primary" onclick="linearProgramming.resolverGrafico()">
                    <i class="fas fa-chart-line"></i> Resolver Graficamente
                </button>
                <button type="button" class="btn-secondary" onclick="linearProgramming.limparFormulario('grafico')">
                    Limpar
                </button>
            </div>
            <div id="grafico-solucao"></div>
        `;
    }
            createSimplexForm() {
                return `
            <div class="solver-header">
                <h2><i class="fas fa-project-diagram"></i> Método Simplex Padrão</h2>
                <p>Para problemas com restrições do tipo ≤ (menor ou igual)</p>
            </div>
            
            <div class="form-section">
                <h3>Configuração do Problema</h3>
                <div class="problem-config">
                    <label>Número de variáveis:</label>
                    <input type="number" id="simplex-num-vars" min="2" max="10" value="2" 
                           onchange="linearProgramming.updateSimplexForm()">
                    
                    <label>Número de restrições:</label>
                    <input type="number" id="simplex-num-restrictions" min="1" max="10" value="2" 
                           onchange="linearProgramming.updateSimplexForm()">
                </div>
            </div>
            
            <div class="form-section">
                <h3>Função Objetivo</h3>
                <div class="objective-function">
                    <select id="simplex-objetivo-tipo">
                        <option value="max">Maximizar</option>
                        <option value="min">Minimizar</option>
                    </select>
                    <span>Z = </span>
                    <div id="simplex-objetivo-inputs"></div>
                </div>
            </div>
            
            <div class="form-section">
                <h3>Restrições (todas do tipo ≤)</h3>
                <div id="simplex-restricoes-container"></div>
            </div>
            
            <div class="solver-actions">
                <button type="button" class="btn-primary" onclick="linearProgramming.resolverSimplex()">
                    <i class="fas fa-calculator"></i> Resolver pelo Simplex
                </button>
                <button type="button" class="btn-secondary" onclick="linearProgramming.limparFormulario('simplex')">
                    Limpar
                </button>
            </div>
        `;
            }

            createBigMForm() {
                return `
            <div class="solver-header">
                <h2><i class="fas fa-infinity"></i> Método Big M</h2>
                <p>Para problemas com restrições mistas (≤, ≥, =)</p>
            </div>
            
            <div class="form-section">
                <h3>Configuração do Problema</h3>
                <div class="problem-config">
                    <label>Número de variáveis:</label>
                    <input type="number" id="bigm-num-vars" min="2" max="10" value="2" 
                           onchange="linearProgramming.updateBigMForm()">
                    
                    <label>Número de restrições:</label>
                    <input type="number" id="bigm-num-restrictions" min="1" max="10" value="2" 
                           onchange="linearProgramming.updateBigMForm()">
                </div>
            </div>
            
            <div class="form-section">
                <h3>Função Objetivo</h3>
                <div class="objective-function">
                    <select id="bigm-objetivo-tipo">
                        <option value="max">Maximizar</option>
                        <option value="min">Minimizar</option>
                    </select>
                    <span>Z = </span>
                    <div id="bigm-objetivo-inputs"></div>
                </div>
            </div>
            
            <div class="form-section">
                <h3>Restrições (≤, ≥ ou =)</h3>
                <div id="bigm-restricoes-container"></div>
            </div>
            
                  
            <div class="solver-actions">
                <button type="button" class="btn-primary" onclick="linearProgramming.resolverBigM()">
                    <i class="fas fa-infinity"></i> Resolver pelo Big M
                </button>
                <button type="button" class="btn-secondary" onclick="linearProgramming.limparFormulario('bigm')">
                    Limpar
                </button>
            </div>
        `;
            }

            createMinimizacaoForm() {
                return `
            <div class="solver-header">
                <h2><i class="fas fa-layer-group"></i> Método Simplex para Minimização</h2>
                <p>Especializado em problemas de minimização com método dual</p>
            </div>
            
            <div class="form-section">
                <h3>Configuração do Problema</h3>
                <div class="problem-config">
                    <label>Número de variáveis:</label>
                    <input type="number" id="min-num-vars" min="2" max="10" value="2" 
                           onchange="linearProgramming.updateMinimizacaoForm()">
                    
                    <label>Número de restrições:</label>
                    <input type="number" id="min-num-restrictions" min="1" max="10" value="2" 
                           onchange="linearProgramming.updateMinimizacaoForm()">
                </div>
            </div>
            
            <div class="form-section">
                <h3>Função Objetivo (Minimização)</h3>
                <div class="objective-function">
                    <span>Minimizar Z = </span>
                    <div id="min-objetivo-inputs"></div>
                </div>
            </div>
            
            <div class="solver-actions">
                <button type="button" class="btn-primary" onclick="linearProgramming.resolverMinimizacao()">
                    <i class="fas fa-layer-group"></i> Resolver Minimização
                </button>
                <button type="button" class="btn-secondary" onclick="linearProgramming.limparFormulario('minimizacao')">
                    Limpar
                </button>
            </div>
        `;
            }

            addEventListeners() {
                // Efeitos de hover nos botões
                document.addEventListener('click', (e) => {
                    if (e.target.classList.contains('btn-primary') || e.target.classList.contains('btn-secondary')) {
                        e.target.style.transform = 'translateY(-3px) scale(1.05)';
                        setTimeout(() => {
                            e.target.style.transform = 'translateY(0) scale(1)';
                        }, 150);
                    }
                });
            }

            selectModel(method) {
                // Esconder todos os containers
                document.querySelectorAll('.solver-container').forEach(container => {
                    container.classList.remove('active');
                });

                // Mostrar o container selecionado
                const selectedContainer = document.getElementById(`${method}Solver`);
                if (selectedContainer) {
                    selectedContainer.classList.add('active');
                    this.currentMethod = method;

                    // Scroll suave para o formulário
                    selectedContainer.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });

                    // Inicializar formulários dinâmicos
                    if (method === 'simplex') {
                        this.updateSimplexForm();
                    } else if (method === 'bigm') {
                        this.updateBigMForm();
                    } else if (method === 'minimizacao') {
                        this.updateMinimizacaoForm();
                    }
                }
            }

            addGraficoRestriction() {
                const container = document.getElementById('grafico-restricoes');
                const newRestriction = document.createElement('div');
                newRestriction.className = 'restricao-row';
                newRestriction.innerHTML = `
            <input type="number" placeholder="a₁" step="any">
            <span>X₁ + </span>
            <input type="number" placeholder="a₂" step="any">
            <span>X₂ ≤ </span>
            <input type="number" placeholder="b" step="any">
            <button type="button" class="btn-remove" onclick="this.parentElement.remove()">×</button>
        `;
                container.appendChild(newRestriction);
            }

            updateSimplexForm() {
                const numVars = parseInt(document.getElementById('simplex-num-vars').value);
                const numRestrictions = parseInt(document.getElementById('simplex-num-restrictions').value);

                // Atualizar função objetivo
                const objetivoContainer = document.getElementById('simplex-objetivo-inputs');
                objetivoContainer.innerHTML = '';

                for (let i = 1; i <= numVars; i++) {
                    const input = document.createElement('input');
                    input.type = 'number';
                    input.placeholder = `C${i}`;
                    input.step = 'any';
                    input.id = `simplex-c${i}`;

                    const span = document.createElement('span');
                    span.textContent = i < numVars ? `X${i} + ` : `X${i}`;

                    objetivoContainer.appendChild(input);
                    objetivoContainer.appendChild(span);
                }

                // Atualizar restrições
                const restricoesContainer = document.getElementById('simplex-restricoes-container');
                restricoesContainer.innerHTML = '';

                for (let i = 1; i <= numRestrictions; i++) {
                    const restricaoDiv = document.createElement('div');
                    restricaoDiv.className = 'restricao-row';

                    let html = '';
                    for (let j = 1; j <= numVars; j++) {
                        html += `
                    <input type="number" placeholder="a${i}${j}" step="any">
                    <span>X${j} ${j < numVars ? '+ ' : '≤ '}</span>
                `;
                    }
                    html += `<input type="number" placeholder="b${i}" step="any">`;

                    restricaoDiv.innerHTML = html;
                    restricoesContainer.appendChild(restricaoDiv);
                }
            }

            updateBigMForm() {
                const numVars = parseInt(document.getElementById('bigm-num-vars').value);
                const numRestrictions = parseInt(document.getElementById('bigm-num-restrictions').value);
            
                // Atualizar função objetivo
                const objetivoContainer = document.getElementById('bigm-objetivo-inputs');
                objetivoContainer.innerHTML = '';
            
                for (let i = 1; i <= numVars; i++) {
                    const input = document.createElement('input');
                    input.type = 'number';
                    input.placeholder = `C${i}`;
                    input.step = 'any';
                    input.id = `bigm-c${i}`;
            
                    const span = document.createElement('span');
                    span.textContent = i < numVars ? `X${i} + ` : `X${i}`;
            
                    objetivoContainer.appendChild(input);
                    objetivoContainer.appendChild(span);
                }
            
                // Atualizar restrições
                const restricoesContainer = document.getElementById('bigm-restricoes-container');
                restricoesContainer.innerHTML = '';
            
                for (let i = 0; i < numRestrictions; i++) {
                    const linha = document.createElement('div');
                    linha.className = 'restricao-row';
            
                    for (let j = 1; j <= numVars; j++) {
                        const input = document.createElement('input');
                        input.type = 'number';
                        input.placeholder = `A${i+1}${j}`;
                        input.step = 'any';
                        input.id = `bigm-a${i}-${j}`;
            
                        linha.appendChild(input);
            
                        const span = document.createElement('span');
                        span.textContent = j < numVars ? `X${j} + ` : `X${j}`;
                        linha.appendChild(span);
                    }
            
                    // Select para tipo de restrição
                    const select = document.createElement('select');
                    select.id = `bigm-op${i}`;
                    ['<=', '>=', '='].forEach(op => {
                        const option = document.createElement('option');
                        option.value = op;
                        option.textContent = op;
                        select.appendChild(option);
                    });
                    linha.appendChild(select);
            
                    // RHS
                    const bInput = document.createElement('input');
                    bInput.type = 'number';
                    bInput.placeholder = `B${i+1}`;
                    bInput.step = 'any';
                    bInput.id = `bigm-b${i}`;
                    linha.appendChild(bInput);
            
                    restricoesContainer.appendChild(linha);
                }
            }            

            updateMinimizacaoForm() {
                const numVars = parseInt(document.getElementById('min-num-vars').value);
                const numRestrictions = parseInt(document.getElementById('min-num-restrictions').value);

                // Atualizar função objetivo
                const objetivoContainer = document.getElementById('min-objetivo-inputs');
                objetivoContainer.innerHTML = '';

                for (let i = 1; i <= numVars; i++) {
                    const input = document.createElement('input');
                    input.type = 'number';
                    input.placeholder = `C${i}`;
                    input.step = 'any';
                    input.id = `min-c${i}`;

                    const span = document.createElement('span');
                    span.textContent = i < numVars ? `X${i} + ` : `X${i}`;

                    objetivoContainer.appendChild(input);
                    objetivoContainer.appendChild(span);
                }

                // Atualizar restrições
                const restricoesContainer = document.getElementById('min-restricoes-container');
                restricoesContainer.innerHTML = '';

                for (let i = 1; i <= numRestrictions; i++) {
                    const restricaoDiv = document.createElement('div');
                    restricaoDiv.className = 'restricao-row';

                    let html = '';
                    for (let j = 1; j <= numVars; j++) {
                        html += `
                    <input type="number" placeholder="a${i}${j}" step="any">
                    <span>X${j} ${j < numVars ? '+ ' : '≥ '}</span>
                `;
                    }
                    html += `<input type="number" placeholder="b${i}" step="any">`;

                    restricaoDiv.innerHTML = html;
                    restricoesContainer.appendChild(restricaoDiv);
                }
            }

            limparFormulario(method) {
                const container = document.getElementById(`${method}Solver`);
                const inputs = container.querySelectorAll('input[type="number"]');
                inputs.forEach(input => input.value = '');

                if (method === 'grafico') {
                    // Manter apenas uma restrição
                    const restricoesContainer = document.getElementById('grafico-restricoes');
                    const restricoes = restricoesContainer.querySelectorAll('.restricao-row');
                    for (let i = 1; i < restricoes.length; i++) {
                        restricoes[i].remove();
                    }
                }
            }

            resolverGrafico() {
                const tipo = document.getElementById('grafico-objetivo-tipo').value;
                const c1 = parseFloat(document.getElementById('grafico-c1').value);
                const c2 = parseFloat(document.getElementById('grafico-c2').value);
            
                const A = [];
                const b = [];
                const constraints_type = [];
            
                const linhas = document.querySelectorAll('#grafico-restricoes .restricao-row');
                linhas.forEach(linha => {
                    const inputs = linha.querySelectorAll('input');
                    if (inputs.length === 3) {
                        const a1 = parseFloat(inputs[0].value);
                        const a2 = parseFloat(inputs[1].value);
                        const bi = parseFloat(inputs[2].value);
                        A.push([a1, a2]);
                        b.push(bi);
                        constraints_type.push('<='); // ajuste se seu frontend tem outro tipo de restrição
                    }
                });
            
                fetch('/api/grafico/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        c: [c1, c2],
                        A: A,
                        b: b,
                        sense: tipo === 'max' ? 'max' : 'min',  // ajuste conforme seu select
                        constraints_type: constraints_type
                    })
                })
                .then(response => response.json())
               .then(data => {
                if (data.error) {
                    console.error("Erro:", data.error);
                    alert("Erro: " + data.error);
                    return;
                }

                alert(`Solução: ponto ${data.solution_point}, valor ótimo ${data.optimal_value}`);

                // Exibir gráfico
                if (data.plot_image) {
                    const imgTag = `<img src="data:image/png;base64,${data.plot_image}" alt="Gráfico da Solução" style="max-width: 100%; border: 1px solid #ccc; margin-top: 15px;" />`;
                    document.getElementById('grafico-solucao').innerHTML = imgTag;
                }
            })

            }               

            // resolverSimplex() {
            //     console.log('Resolvendo pelo método Simplex...');
            //     // Aqui seria implementada a lógica de resolução
            //     alert('Formulário configurado! Implementar lógica de resolução Simplex.');
            // }

            resolverBigM() {
                const numVars = parseInt(document.getElementById('bigm-num-vars').value);
                const numRestrictions = parseInt(document.getElementById('bigm-num-restrictions').value);
                const tipo = document.getElementById('bigm-objetivo-tipo').value;
            
                const c = [];
                for (let i = 1; i <= numVars; i++) {
                    const val = parseFloat(document.getElementById(`bigm-c${i}`).value);
                    c.push(isNaN(val) ? 0 : val);
                }
            
                const A = [];
                const b = [];
                const constraints_type = [];
            
                for (let i = 0; i < numRestrictions; i++) {
                    const linha = [];
                    for (let j = 1; j <= numVars; j++) {
                        const val = parseFloat(document.getElementById(`bigm-a${i}-${j}`).value);
                        linha.push(isNaN(val) ? 0 : val);
                    }
                    A.push(linha);
            
                    const bi = parseFloat(document.getElementById(`bigm-b${i}`).value);
                    b.push(isNaN(bi) ? 0 : bi);
            
                    const tipoRestricao = document.getElementById(`bigm-op${i}`).value;
                    constraints_type.push(tipoRestricao);
                }
            
                const payload = {
                    c: c,
                    A: A,
                    b: b,
                    sense: tipo,
                    constraints_type: constraints_type
                };
            
                fetch('/api/bigm/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        alert("Erro: " + data.error);
                    } else {
                        alert(`Solução: ${data.solution}, Valor ótimo: ${data.optimal_value}`);
                        // Mostrar gráfico se for o caso
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert("Erro na requisição.");
                });
            }            

            resolverMinimizacao() {
                console.log('Resolvendo pelo método de Minimização...');
                // Aqui seria implementada a lógica de resolução
                alert('Formulário configurado! Implementar lógica de resolução por Minimização.');
            }
        }

        // Instanciar e tornar acessível globalmente
        const linearProgramming = new LinearProgrammingMethods();
        window.linearProgramming = linearProgramming;

        // Tornar selectModel acessível globalmente
        window.selectModel = function (method) {
            linearProgramming.selectModel(method);
        };

        // Inicializar formulários se necessário
        document.addEventListener('DOMContentLoaded', function () {
            linearProgramming.updateSimplexForm();
            linearProgramming.updateBigMForm();
            linearProgramming.updateMinimizacaoForm();
        });

        window.addEventListener('DOMContentLoaded', () => {
            linearProgramming = new LinearProgrammingMethods();
        });