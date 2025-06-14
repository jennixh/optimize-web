class MolecularSystem {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.molecules = [];
        this.connections = [];

        this.setupCanvas();
        this.createMolecules();
        this.animate();

        window.addEventListener('resize', () => this.handleResize());
    }

    setupCanvas() {
        const container = document.getElementById('molecularBg');
        container.appendChild(this.canvas);
        this.handleResize();

        this.canvas.style.position = 'absolute';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.pointerEvents = 'none';
    }

    handleResize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createMolecules() {
        const count = Math.floor((this.canvas.width * this.canvas.height) / 15000);
        this.molecules = [];

        for (let i = 0; i < count; i++) {
            this.molecules.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1,
                opacity: Math.random() * 0.8 + 0.2
            });
        }
    }

    updateMolecules() {
        this.molecules.forEach(molecule => {
            molecule.x += molecule.vx;
            molecule.y += molecule.vy;

            if (molecule.x < 0 || molecule.x > this.canvas.width) molecule.vx *= -1;
            if (molecule.y < 0 || molecule.y > this.canvas.height) molecule.vy *= -1;

            molecule.x = Math.max(0, Math.min(this.canvas.width, molecule.x));
            molecule.y = Math.max(0, Math.min(this.canvas.height, molecule.y));
        });
    }

    drawConnections() {
        this.ctx.strokeStyle = 'rgba(0, 255, 135, 0.1)';
        this.ctx.lineWidth = 1;

        for (let i = 0; i < this.molecules.length; i++) {
            for (let j = i + 1; j < this.molecules.length; j++) {
                const dx = this.molecules[i].x - this.molecules[j].x;
                const dy = this.molecules[i].y - this.molecules[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 120) {
                    const opacity = 1 - distance / 120;
                    this.ctx.strokeStyle = `rgba(0, 255, 135, ${opacity * 0.15})`;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.molecules[i].x, this.molecules[i].y);
                    this.ctx.lineTo(this.molecules[j].x, this.molecules[j].y);
                    this.ctx.stroke();
                }
            }
        }
    }

    drawMolecules() {
        this.molecules.forEach(molecule => {
            this.ctx.beginPath();
            this.ctx.arc(molecule.x, molecule.y, molecule.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(0, 255, 135, ${molecule.opacity * 0.6})`;
            this.ctx.fill();

            this.ctx.beginPath();
            this.ctx.arc(molecule.x, molecule.y, molecule.radius * 2, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(0, 255, 135, ${molecule.opacity * 0.1})`;
            this.ctx.fill();
        });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.updateMolecules();
        this.drawConnections();
        this.drawMolecules();

        requestAnimationFrame(() => this.animate());
    }
}

// Inicializar sistema molecular
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

        // Container principal para os métodos
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
            
            <div class="result-section" id="grafico-result-section" style="display: none;">
                <h3>Visualização Gráfica</h3>
                <div class="graph-container" id="grafico-graph-container">
                    <canvas id="grafico-graph-canvas" width="600" height="400"></canvas>
                </div>
                
                <div class="solution-display">
                    <h3>Solução Ótima</h3>
                    <div class="solution-content" id="grafico-solution-content">
                        <!-- Resultado será exibido aqui -->
                    </div>
                </div>
            </div>
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
                <h3>Restrições</h3>
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
            
            <div class="result-section" id="simplex-result-section" style="display: none;">
                <h3>Visualização Gráfica</h3>
                <div class="graph-container" id="simplex-graph-container">
                    <canvas id="simplex-graph-canvas"></canvas>
                </div>
                
                <div class="solution-display">
                    <h3>Solução Ótima</h3>
                    <div class="solution-content" id="simplex-solution-content">
                        <!-- Resultado será exibido aqui -->
                    </div>
                </div>
            </div>
        `;
    }

    createBigMForm() {
        return `
        <div class="solver-header">
            <h2><i class="fas fa-infinity"></i> Método Big M</h2>
            <p>Para problemas de MAXIMIZAÇÃO com restrições mistas (≤, ≥, =)</p>
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
            <h3>Função Objetivo (Maximização)</h3>
            <div class="objective-function">
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
        
        <div class="result-section" id="bigm-result-section" style="display: none;">
            <h3>Visualização Gráfica</h3>
            <div class="graph-container" id="bigm-graph-container">
                <canvas id="bigm-graph-canvas"></canvas>
            </div>
            
            <div class="solution-display">
                <h3>Solução Ótima</h3>
                <div class="solution-content" id="bigm-solution-content">
                    <!-- Resultado será exibido aqui -->
                </div>
            </div>
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
            
            <div class="form-section">
                <h3>Restrições (≤, ≥ ou =)</h3>
                <div id="min-restricoes-container"></div>
            </div>
            
            <div class="solver-actions">
                <button type="button" class="btn-primary" onclick="linearProgramming.resolverMinimizacao()">
                    <i class="fas fa-layer-group"></i> Resolver Minimização
                </button>
                <button type="button" class="btn-secondary" onclick="linearProgramming.limparFormulario('minimizacao')">
                    Limpar
                </button>
            </div>
            
            <div class="result-section" id="min-result-section" style="display: none;">
                <h3>Visualização Gráfica</h3>
                <div class="graph-container" id="min-graph-container">
                    <canvas id="min-graph-canvas"></canvas>
                </div>
                
                <div class="solution-display">
                    <h3>Solução Ótima</h3>
                    <div class="solution-content" id="min-solution-content">
                        <!-- Resultado será exibido aqui -->
                    </div>
                </div>
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

        // Atualizar restrições - APENAS ≤ (Simplex padrão)
        const restricoesContainer = document.getElementById('simplex-restricoes-container');
        restricoesContainer.innerHTML = '';

        for (let i = 1; i <= numRestrictions; i++) {
            const restricaoDiv = document.createElement('div');
            restricaoDiv.className = 'restricao-row';

            let html = '';
            for (let j = 1; j <= numVars; j++) {
                html += `
                <select class="coefficient-sign">
                    <option value="+">+</option>
                    <option value="-">-</option>
                </select>
                <input type="number" placeholder="a${i}${j}" step="any">
                <span>X${j} </span>
            `;
            }
            html += `
            <span>≤</span>
            <input type="number" placeholder="b${i}" step="any">
        `;

            restricaoDiv.innerHTML = html;
            restricoesContainer.appendChild(restricaoDiv);
        }
    }

    updateBigMForm() {
        const numVars = parseInt(document.getElementById('bigm-num-vars').value);
        const numRestrictions = parseInt(document.getElementById('bigm-num-restrictions').value);

        // Atualizar função objetivo (apenas maximização)
        const objetivoContainer = document.getElementById('bigm-objetivo-inputs');
        objetivoContainer.innerHTML = '<span>Maximizar Z = </span>';

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

        for (let i = 1; i <= numRestrictions; i++) {
            const restricaoDiv = document.createElement('div');
            restricaoDiv.className = 'restricao-row';

            let html = '';
            for (let j = 1; j <= numVars; j++) {
                html += `
                <select class="coefficient-sign">
                    <option value="+">+</option>
                    <option value="-">-</option>
                </select>
                <input type="number" placeholder="a${i}${j}" step="any">
                <span>X${j} </span>
            `;
            }
            html += `
            <select class="constraint-type">
                <option value="<=">≤</option>
                <option value=">=">≥</option>
                <option value="=">=</option>
            </select>
            <input type="number" placeholder="b${i}" step="any">
        `;

            restricaoDiv.innerHTML = html;
            restricoesContainer.appendChild(restricaoDiv);
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
                <select class="coefficient-sign">
                    <option value="+">+</option>
                    <option value="-">-</option>
                </select>
                <input type="number" placeholder="a${i}${j}" step="any">
                <span>X${j} </span>
            `;
            }
            html += `
            <select class="constraint-type">
                <option value="<=">≤</option>
                <option value=">=">≥</option>
                <option value="=">=</option>
            </select>
            <input type="number" placeholder="b${i}" step="any">
        `;

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
        console.log('Resolvendo pelo método gráfico...');
        // Aqui seria implementada a lógica de resolução
        alert('Formulário configurado! Implementar lógica de resolução gráfica.');
    }

    resolverSimplex() {
        console.log('Resolvendo pelo método Simplex...');
        // Aqui seria implementada a lógica de resolução
        alert('Formulário configurado! Implementar lógica de resolução Simplex.');
    }

    resolverBigM() {
        console.log('Resolvendo pelo método Big M...');
        // Aqui seria implementada a lógica de resolução
        alert('Formulário configurado! Implementar lógica de resolução Big M.');
    }

    resolverMinimizacao() {
        console.log('Resolvendo pelo método de Minimização...');
        // Aqui seria implementada a lógica de resolução
        alert('Formulário configurado! Implementar lógica de resolução por Minimização.');
    }

    displaySolution(method, optimalValue, variables, graphData = null) {
        const resultSection = document.getElementById(`${method}-result-section`);
        const solutionContent = document.getElementById(`${method}-solution-content`);

        // Mostrar seção de resultado
        resultSection.style.display = 'block';

        // Construir HTML da solução
        let variablesHtml = '';
        variables.forEach((value, index) => {
            variablesHtml += `<div class="variable-result">X${index + 1} = ${value.toFixed(4)}</div>`;
        });

        solutionContent.innerHTML = `
            <div class="optimal-value">
                <strong>Valor Ótimo de Z: ${optimalValue.toFixed(4)}</strong>
            </div>
            <div class="variables-container">
                <h4>Valores das Variáveis:</h4>
                ${variablesHtml}
            </div>
        `;

        // Se houver dados do gráfico, desenhar
        if (graphData && method === 'grafico') {
            this.drawGraph(method, graphData);
        }
    }

    drawGraph(method, data) {
        const canvas = document.getElementById(`${method}-graph-canvas`);
        const ctx = canvas.getContext('2d');

        // Limpar canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Desenhar eixos
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;

        // Eixo X
        ctx.beginPath();
        ctx.moveTo(50, canvas.height - 50);
        ctx.lineTo(canvas.width - 50, canvas.height - 50);
        ctx.stroke();

        // Eixo Y
        ctx.beginPath();
        ctx.moveTo(50, 50);
        ctx.lineTo(50, canvas.height - 50);
        ctx.stroke();

        // Adicionar labels
        ctx.fillStyle = '#ffffff';
        ctx.font = '14px Arial';
        ctx.fillText('X₁', canvas.width - 40, canvas.height - 30);
        ctx.fillText('X₂', 30, 40);

        // Aqui você adicionaria a lógica específica para desenhar as restrições e região viável
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