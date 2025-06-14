from django.db import models
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# MÉTODO GRÁFICO - VERSÃO COMPLETA CORRIGIDA
# ============================================================================
class GraphicalMethod:
    def __init__(self, c, A, b, sense='max', constraints_type=None):
        self.c_original = np.array(c, dtype=float)
        self.A_original = np.array(A, dtype=float)  
        self.b_original = np.array(b, dtype=float)
        self.sense = sense
        self.constraints_type = constraints_type or ['<='] * len(b)
        
        # Converter para forma padrão (max com <=)
        if sense == 'min':
            self.c = -self.c_original
        else:
            self.c = self.c_original.copy()
            
        self.A = self.A_original.copy()
        self.b = self.b_original.copy()
        
        # TRATAMENTO COMPLETO DE RESTRIÇÕES (incluindo igualdade)
        self.display_constraints = self.constraints_type.copy()
        
        # Expandir restrições de igualdade
        expanded_A = []
        expanded_b = []
        expanded_display = []
        expanded_original_A = []
        expanded_original_b = []
        
        for i, constraint in enumerate(self.constraints_type):
            if constraint == '=':
                # Converter A[i]x = b[i] em duas restrições:
                # A[i]x <= b[i] e A[i]x >= b[i] (-A[i]x <= -b[i])
                expanded_A.append(self.A[i])        # A[i]x <= b[i]
                expanded_A.append(-self.A[i])       # -A[i]x <= -b[i]
                expanded_b.append(self.b[i])
                expanded_b.append(-self.b[i])
                expanded_display.append('<=')
                expanded_display.append('>=')
                # Preservar originais para display
                expanded_original_A.append(self.A_original[i])
                expanded_original_A.append(self.A_original[i])
                expanded_original_b.append(self.b_original[i])
                expanded_original_b.append(self.b_original[i])
            else:
                expanded_A.append(self.A[i])
                expanded_b.append(self.b[i])
                expanded_display.append(constraint)
                expanded_original_A.append(self.A_original[i])
                expanded_original_b.append(self.b_original[i])
        
        # Atualizar matrizes com restrições expandidas
        self.A = np.array(expanded_A, dtype=float)
        self.b = np.array(expanded_b, dtype=float)
        self.display_constraints = expanded_display
        self.A_display = np.array(expanded_original_A, dtype=float)
        self.b_display = np.array(expanded_original_b, dtype=float)
        
        # Aplicar transformação para >= (converter para <=)
        for i, constraint in enumerate(self.display_constraints):
            if constraint == '>=':
                self.A[i] *= -1
                self.b[i] *= -1
        
        self.m, self.n = self.A.shape
        
        # Validação de entrada
        if self.m == 0 or self.n == 0:
            raise ValueError("Matriz A não pode ser vazia")
        if len(self.c) != self.n:
            raise ValueError("Dimensões incompatíveis entre A e c")
    
    def solve(self):
        """Método Gráfico (apenas para 2 variáveis)"""
        if self.n != 2:
            raise ValueError("Método gráfico só funciona para 2 variáveis")
        
        print("\n=== MÉTODO GRÁFICO ===")
        print(f"Problema: {'Minimizar' if self.sense == 'min' else 'Maximizar'} f(x) = {self.c_original[0]}x₁ + {self.c_original[1]}x₂")
        print("Sujeito a:")
        
        # Mostrar restrições originais (antes da expansão)
        constraint_index = 0
        for i, constraint_type in enumerate(self.constraints_type):
            if constraint_type == '=':
                print(f"  {self.A_original[i,0]}x₁ + {self.A_original[i,1]}x₂ = {self.b_original[i]}")
                constraint_index += 2  # Pula 2 porque igualdade vira 2 restrições
            else:
                print(f"  {self.A_original[i,0]}x₁ + {self.A_original[i,1]}x₂ {constraint_type} {self.b_original[i]}")
                constraint_index += 1
        
        print("  x₁, x₂ ≥ 0")
        
        # Encontrar vértices da região factível
        vertices = self._find_vertices()
        
        if not vertices:
            raise ValueError("Região factível vazia - o problema é inviável")
        
        # Verificar se região é limitada para problemas de maximização
        if self.sense == 'max' and self._is_unbounded(vertices):
            print("ATENÇÃO: A região factível pode ser ilimitada!")
            print("Verificando se a função objetivo é limitada...")
        
        # Avaliar função objetivo em cada vértice
        best_value = float('-inf') if self.sense == 'max' else float('inf')
        best_point = None
        
        print(f"\nVértices da região factível ({len(vertices)} encontrados):")
        for i, (x_val, y_val) in enumerate(vertices):
            # Usar função objetivo original para avaliação final
            obj_value_original = self.c_original[0] * x_val + self.c_original[1] * y_val
            obj_value_internal = self.c[0] * x_val + self.c[1] * y_val
            
            print(f"Vértice {i+1}: ({x_val:.4f}, {y_val:.4f}) -> f = {obj_value_original:.4f}")
            
            # Usar valor interno para comparação (já ajustado para max)
            if obj_value_internal > best_value:
                best_value = obj_value_internal
                best_point = (x_val, y_val)
        
        # Plotar gráfico
        self._plot_solution(vertices, best_point)
        
        # Retornar valor original da função objetivo
        if self.sense == 'min':
            final_value = -best_value
        else:
            final_value = best_value
        
        print(f"\nSolução ótima: x₁ = {best_point[0]:.4f}, x₂ = {best_point[1]:.4f}")
        print(f"Valor ótimo: f* = {final_value:.4f}")
        
        return np.array(best_point), final_value
    
    def _find_vertices(self):
        """Encontra os vértices da região factível"""
        lines = []
        line_labels = []
        
        # Adicionar eixos (restrições de não-negatividade)
        lines.append((1, 0, 0))  # x₁ = 0
        lines.append((0, 1, 0))  # x₂ = 0
        line_labels.extend(['x₁ = 0', 'x₂ = 0'])
        
        # Adicionar restrições funcionais (já expandidas)
        constraint_counter = 1
        original_index = 0
        
        for i in range(self.m):
            lines.append((self.A[i, 0], self.A[i, 1], self.b[i]))
            
            # Identificar se é de igualdade original
            if (original_index < len(self.constraints_type) and 
                self.constraints_type[original_index] == '=' and 
                i < len(self.display_constraints)):
                
                if self.display_constraints[i] == '<=':
                    line_labels.append(f'R{constraint_counter}(=)')
                else:
                    line_labels.append(f'R{constraint_counter}(=)')
                    constraint_counter += 1
                    original_index += 1
            else:
                line_labels.append(f'R{constraint_counter}')
                constraint_counter += 1
                original_index += 1
        
        vertices = []
        
        # Encontrar todas as interseções possíveis
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                vertex = self._line_intersection(lines[i], lines[j])
                if vertex is not None:
                    x_val, y_val = vertex
                    
                    # Tolerância mais rigorosa para não-negatividade
                    if x_val >= -1e-10 and y_val >= -1e-10:
                        # Verificar se satisfaz todas as restrições
                        if self._is_feasible(x_val, y_val):
                            vertices.append((max(0, x_val), max(0, y_val)))  # Garantir não-negatividade
        
        # Remover duplicatas com tolerância apropriada
        return self._remove_duplicates(vertices)
    
    def _line_intersection(self, line1, line2):
        """Calcula interseção entre duas retas ax + by = c"""
        a1, b1, c1 = line1
        a2, b2, c2 = line2
        
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-12:  # Tolerância rigorosa
            return None  # Linhas paralelas
        
        x_int = (c1 * b2 - c2 * b1) / det
        y_int = (a1 * c2 - a2 * c1) / det
        
        return (x_int, y_int)
    
    def _is_feasible(self, x, y, tolerance=1e-10):
        """Verifica se um ponto satisfaz todas as restrições"""
        if x < -tolerance or y < -tolerance:  # Verificação de não-negatividade
            return False
        
        for i in range(self.m):
            constraint_value = self.A[i, 0] * x + self.A[i, 1] * y
            if constraint_value > self.b[i] + tolerance:
                return False
        
        return True
    
    def _remove_duplicates(self, vertices, tolerance=1e-8):
        """Remove vértices duplicados"""
        unique_vertices = []
        for v in vertices:
            is_duplicate = False
            for uv in unique_vertices:
                if abs(v[0] - uv[0]) < tolerance and abs(v[1] - uv[1]) < tolerance:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_vertices.append(v)
        
        return unique_vertices
    
    def _is_unbounded(self, vertices):
        """Verifica se a região factível é ilimitada (verificação básica)"""
        if len(vertices) < 3:
            return True
        
        # Verifica se existe algum vértice muito distante da origem
        max_distance = max(np.sqrt(v[0]**2 + v[1]**2) for v in vertices)
        return max_distance > 1e6  # Heurística simples
    
    def _plot_solution(self, vertices, best_point):
        """Plota a solução gráfica"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Determinar limites do gráfico
        if vertices:
            max_coord = max(max(v[0], v[1]) for v in vertices)
            plot_limit = max(10, max_coord * 1.3)
        else:
            plot_limit = 10
        
        # Plotar região factível
        if len(vertices) >= 3:
            sorted_vertices = self._sort_vertices_ccw(vertices)
            polygon = Polygon(sorted_vertices, alpha=0.3, color='lightblue', 
                            label='Região Factível', edgecolor='blue', linewidth=2)
            ax.add_patch(polygon)
        elif len(vertices) == 2:
            # Caso especial: região factível é uma linha
            ax.plot([vertices[0][0], vertices[1][0]], [vertices[0][1], vertices[1][1]], 
                   'b-', linewidth=3, alpha=0.7, label='Região Factível (linha)')
        
        # Plotar vértices
        for i, (x_val, y_val) in enumerate(vertices):
            ax.plot(x_val, y_val, 'ro', markersize=8)
            ax.annotate(f'V{i+1}\n({x_val:.2f}, {y_val:.2f})', 
                       (x_val, y_val), xytext=(8, 8), 
                       textcoords='offset points', fontsize=9,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Destacar solução ótima
        if best_point:
            ax.plot(best_point[0], best_point[1], 'go', markersize=15, 
                   label=f'Solução Ótima\n({best_point[0]:.3f}, {best_point[1]:.3f})', 
                   markeredgecolor='darkgreen', markeredgewidth=2)
        
        # Plotar linhas das restrições originais
        x_plot = np.linspace(-1, plot_limit, 200)
        colors = ['red', 'purple', 'orange', 'brown', 'pink', 'gray', 'olive']
        
        # Plotar restrições originais (não expandidas)
        for i, constraint_type in enumerate(self.constraints_type):
            color = colors[i % len(colors)]
            
            if abs(self.A_original[i, 1]) > 1e-8:
                y_plot = (self.b_original[i] - self.A_original[i, 0] * x_plot) / self.A_original[i, 1]
                mask = (y_plot >= -1) & (y_plot <= plot_limit * 1.2)
                
                if constraint_type == '=':
                    # Linha sólida para igualdade
                    ax.plot(x_plot[mask], y_plot[mask], '-', color=color, linewidth=2.5,
                           label=f'R{i+1}: {self.A_original[i,0]}x₁ + {self.A_original[i,1]}x₂ = {self.b_original[i]}')
                else:
                    # Linha tracejada para desigualdades
                    ax.plot(x_plot[mask], y_plot[mask], '--', color=color, linewidth=2,
                           label=f'R{i+1}: {self.A_original[i,0]}x₁ + {self.A_original[i,1]}x₂ {constraint_type} {self.b_original[i]}')
                    
            elif abs(self.A_original[i, 0]) > 1e-8:
                x_line = self.b_original[i] / self.A_original[i, 0]
                if 0 <= x_line <= plot_limit:
                    if constraint_type == '=':
                        ax.axvline(x=x_line, color=color, linestyle='-', linewidth=2.5,
                                 label=f'R{i+1}: {self.A_original[i,0]}x₁ = {self.b_original[i]}')
                    else:
                        ax.axvline(x=x_line, color=color, linestyle='--', linewidth=2,
                                 label=f'R{i+1}: {self.A_original[i,0]}x₁ {constraint_type} {self.b_original[i]}')
        
        # Plotar curvas de nível da função objetivo
        if best_point:
            obj_at_optimum = self.c_original[0] * best_point[0] + self.c_original[1] * best_point[1]
            levels = [obj_at_optimum * 0.25, obj_at_optimum * 0.5, 
                     obj_at_optimum * 0.75, obj_at_optimum]
            
            for level in levels:
                if abs(self.c_original[1]) > 1e-8:
                    y_obj = (level - self.c_original[0] * x_plot) / self.c_original[1]
                    mask = (y_obj >= -1) & (y_obj <= plot_limit * 1.2)
                    alpha = 1.0 if level == obj_at_optimum else 0.5
                    linestyle = '-' if level == obj_at_optimum else ':'
                    label = f'f = {level:.2f}' if level == obj_at_optimum else None
                    ax.plot(x_plot[mask], y_obj[mask], linestyle, 
                           color='green', alpha=alpha, linewidth=2, label=label)
                elif abs(self.c_original[0]) > 1e-8:
                    # Caso especial: função objetivo vertical (c[1] ≈ 0)
                    x_obj = level / self.c_original[0]
                    if 0 <= x_obj <= plot_limit:
                        alpha = 1.0 if level == obj_at_optimum else 0.5
                        linestyle = '-' if level == obj_at_optimum else ':'
                        label = f'f = {level:.2f}' if level == obj_at_optimum else None
                        ax.axvline(x=x_obj, color='green', alpha=alpha, 
                                 linestyle=linestyle, linewidth=2, label=label)
        
        # Configurações do gráfico
        ax.set_xlim(-0.5, plot_limit)
        ax.set_ylim(-0.5, plot_limit)
        ax.set_xlabel('x₁', fontsize=12)
        ax.set_ylabel('x₂', fontsize=12)
        ax.set_title(f'Método Gráfico - Programação Linear\n'
                    f'{"Minimizar" if self.sense == "min" else "Maximizar"}: '
                    f'f(x) = {self.c_original[0]}x₁ + {self.c_original[1]}x₂', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()
    
    def _sort_vertices_ccw(self, vertices):
        """Ordena vértices no sentido anti-horário para formar polígono convexo"""
        if len(vertices) < 3:
            return vertices
        
        # Calcular centroide
        center = np.mean(vertices, axis=0)
        
        # Calcular ângulos em relação ao centroide
        def angle_from_center(vertex):
            return np.arctan2(vertex[1] - center[1], vertex[0] - center[0])
        
        # Ordenar por ângulo
        sorted_vertices = sorted(vertices, key=angle_from_center)
        return sorted_vertices
    
# ============================================================================
# MÉTODO SIMPLEX PADRÃO - INÍCIO
# ============================================================================

class SimplexStandard:
    def __init__(self, c, A, b, sense='max', constraints_type=None):
        self.c_original = np.array(c, dtype=float)
        self.A_original = np.array(A, dtype=float)
        self.b_original = np.array(b, dtype=float)
        self.sense = sense
        self.constraints_type = constraints_type or ['<='] * len(b)
        
        # Converter para forma padrão (max com <=)
        if sense == 'min':
            self.c = -self.c_original
        else:
            self.c = self.c_original.copy()
            
        self.A = self.A_original.copy()
        self.b = self.b_original.copy()
        
        self.m, self.n = self.A.shape
    
    def solve(self):
        """Simplex padrão (assume forma canônica)"""
        print("\n=== MÉTODO SIMPLEX PADRÃO ===")
        
        # Verificar se todas as restrições são <=
        if not all(ct == '<=' for ct in self.constraints_type):
            raise ValueError("Simplex padrão requer todas as restrições do tipo <=")
        
        # Verificar se todos os b são não-negativos
        if not all(bi >= 0 for bi in self.b):
            raise ValueError("Simplex padrão requer todos os termos b ≥ 0")
        
        # Adicionar variáveis de folga
        tableau = np.hstack([self.A, np.eye(self.m)])
        c_extended = np.hstack([self.c, np.zeros(self.m)])
        
        # Base inicial (variáveis de folga)
        base = list(range(self.n, self.n + self.m))
        
        iteration = 0
        print(f"Tableau inicial:")
        self._print_tableau(tableau, c_extended, self.b, base)
        
        while True:
            iteration += 1
            print(f"\n--- Iteração {iteration} ---")
            
            # Calcular custos reduzidos
            reduced_costs = []
            for j in range(len(c_extended)):
                if j not in base:
                    rc = c_extended[j]
                    for i, var in enumerate(base):
                        rc -= c_extended[var] * tableau[i, j]
                    reduced_costs.append((j, rc))
            
            # Teste de otimalidade
            max_rc = max(reduced_costs, key=lambda x: x[1])
            if max_rc[1] <= 1e-8:
                print("Solução ótima encontrada!")
                break
            
            # Variável entrante
            entering = max_rc[0]
            print(f"Variável entrante: x_{entering + 1}")
            
            # Teste de ilimitação
            if all(tableau[i, entering] <= 1e-8 for i in range(self.m)):
                raise ValueError("Problema ilimitado")
            
            # Variável sainte (teste da razão)
            ratios = []
            for i in range(self.m):
                if tableau[i, entering] > 1e-8:
                    ratios.append((i, self.b[i] / tableau[i, entering]))
                else:
                    ratios.append((i, float('inf')))
            
            leaving_idx = min(ratios, key=lambda x: x[1])[0]
            leaving = base[leaving_idx]
            print(f"Variável sainte: x_{leaving + 1}")
            
            # Pivotamento
            pivot = tableau[leaving_idx, entering]
            tableau[leaving_idx, :] /= pivot
            self.b[leaving_idx] /= pivot
            
            for i in range(self.m):
                if i != leaving_idx and abs(tableau[i, entering]) > 1e-8:
                    factor = tableau[i, entering]
                    tableau[i, :] -= factor * tableau[leaving_idx, :]
                    self.b[i] -= factor * self.b[leaving_idx]
            
            # Atualizar base
            base[leaving_idx] = entering
            
            self._print_tableau(tableau, c_extended, self.b, base)
        
        # Extrair solução
        solution = np.zeros(self.n + self.m)
        for i, var in enumerate(base):
            solution[var] = self.b[i]
        
        obj_value = sum(c_extended[var] * solution[var] for var in base)
        
        if self.sense == 'min':
            obj_value = -obj_value
        
        return solution[:self.n], obj_value
    
    def _print_tableau(self, tableau, c, b, base):
        """Imprime o tableau do simplex"""
        print("\nTableau:")
        print("Base\t", end="")
        for j in range(tableau.shape[1]):
            print(f"x_{j+1}\t", end="")
        print("RHS")
        
        for i in range(len(base)):
            print(f"x_{base[i]+1}\t", end="")
            for j in range(tableau.shape[1]):
                print(f"{tableau[i,j]:.3f}\t", end="")
            print(f"{b[i]:.3f}")
        
        print("z\t", end="")
        for j in range(len(c)):
            if j not in base:
                rc = c[j] - sum(c[base[i]] * tableau[i,j] for i in range(len(base)))
                print(f"{rc:.3f}\t", end="")
            else:
                print("0.000\t", end="")
        
        obj_value = sum(c[base[i]] * b[i] for i in range(len(base)))
        print(f"{obj_value:.3f}")

# ============================================================================
# MÉTODO SIMPLEX PADRÃO - FIM
# ============================================================================

# ============================================================================
# MÉTODO BIG M - INÍCIO
# ============================================================================

class SimplexBigM:
    def __init__(self, c, A, b, sense='max', constraints_type=None):
        self.c_original = np.array(c, dtype=float)
        self.A_original = np.array(A, dtype=float)
        self.b_original = np.array(b, dtype=float)
        self.sense = sense
        self.constraints_type = constraints_type or ['<='] * len(b)
        self.M = 1e6  # Valor grande
        
        self.m, self.n = self.A_original.shape
    
    def solve(self):
        """Método Big M"""
        print("\n=== MÉTODO BIG M ===")
        print(f"Usando M = {self.M}")
        
        # Converter para maximização se necessário
        if self.sense == 'min':
            c = -self.c_original
        else:
            c = self.c_original.copy()
        
        A = self.A_original.copy()
        b = self.b_original.copy()
        
        # Tornar todos os b não-negativos
        for i in range(self.m):
            if b[i] < 0:
                A[i] *= -1
                b[i] *= -1
                # Inverter tipo da restrição
                if self.constraints_type[i] == '<=':
                    self.constraints_type[i] = '>='
                elif self.constraints_type[i] == '>=':
                    self.constraints_type[i] = '<='
        
        # Construir tableau com variáveis de folga e artificiais
        tableau_cols = []
        c_extended = list(c)
        base = []
        artificial_vars = []
        var_types = []  # Tipo de cada variável: 'original', 'slack', 'artificial'
        
        # Variáveis originais
        for j in range(self.n):
            col = np.zeros(self.m)
            for i in range(self.m):
                col[i] = A[i, j]
            tableau_cols.append(col)
            var_types.append('original')
        
        # Processar cada restrição
        for i, constraint in enumerate(self.constraints_type):
            if constraint == '<=':
                # Adicionar variável de folga
                col = np.zeros(self.m)
                col[i] = 1
                tableau_cols.append(col)
                c_extended.append(0)
                base.append(len(tableau_cols) - 1)
                var_types.append('slack')
                
            elif constraint == '>=':
                # Adicionar variável de folga negativa
                col = np.zeros(self.m)
                col[i] = -1
                tableau_cols.append(col)
                c_extended.append(0)
                var_types.append('slack')
                
                # Adicionar variável artificial
                col = np.zeros(self.m)
                col[i] = 1
                tableau_cols.append(col)
                c_extended.append(-self.M)
                base.append(len(tableau_cols) - 1)
                artificial_vars.append(len(tableau_cols) - 1)
                var_types.append('artificial')
                
            else:  # '='
                # Adicionar variável artificial
                col = np.zeros(self.m)
                col[i] = 1
                tableau_cols.append(col)
                c_extended.append(-self.M)
                base.append(len(tableau_cols) - 1)
                artificial_vars.append(len(tableau_cols) - 1)
                var_types.append('artificial')
        
        # Construir tableau
        tableau = np.column_stack(tableau_cols)
        c_extended = np.array(c_extended)
        
        print(f"Variáveis artificiais: {[f'x_{v+1}' for v in artificial_vars]}")
        
        iteration = 0
        print(f"Tableau inicial:")
        self._print_tableau(tableau, c_extended, b, base)
        
        while True:
            iteration += 1
            print(f"\n--- Iteração {iteration} ---")
            
            # Calcular custos reduzidos
            reduced_costs = []
            for j in range(len(c_extended)):
                if j not in base:
                    rc = c_extended[j]
                    for i, var in enumerate(base):
                        rc -= c_extended[var] * tableau[i, j]
                    reduced_costs.append((j, rc))
            
            # Teste de otimalidade
            max_rc = max(reduced_costs, key=lambda x: x[1])
            if max_rc[1] <= 1e-8:
                print("Solução ótima encontrada!")
                break
            
            # Variável entrante
            entering = max_rc[0]
            print(f"Variável entrante: x_{entering + 1}")
            
            # Teste de ilimitação
            if all(tableau[i, entering] <= 1e-8 for i in range(self.m)):
                raise ValueError("Problema ilimitado")
            
            # Variável sainte (teste da razão)
            ratios = []
            for i in range(self.m):
                if tableau[i, entering] > 1e-8:
                    ratios.append((i, b[i] / tableau[i, entering]))
                else:
                    ratios.append((i, float('inf')))
            
            leaving_idx = min(ratios, key=lambda x: x[1])[0]
            leaving = base[leaving_idx]
            print(f"Variável sainte: x_{leaving + 1}")
            
            # Pivotamento
            pivot = tableau[leaving_idx, entering]
            tableau[leaving_idx, :] /= pivot
            b[leaving_idx] /= pivot
            
            for i in range(self.m):
                if i != leaving_idx and abs(tableau[i, entering]) > 1e-8:
                    factor = tableau[i, entering]
                    tableau[i, :] -= factor * tableau[leaving_idx, :]
                    b[i] -= factor * b[leaving_idx]
            
            # Atualizar base
            base[leaving_idx] = entering
            
            self._print_tableau(tableau, c_extended, b, base)
        
        # Verificar se há variáveis artificiais na base
        artificial_in_base = [var for var in base if var in artificial_vars]
        if artificial_in_base:
            # Verificar se são zero
            for i, var in enumerate(base):
                if var in artificial_vars and abs(b[i]) > 1e-6:
                    raise ValueError("Problema infactível - variável artificial não-zero na solução ótima")
        
        # Extrair solução
        solution = np.zeros(len(c_extended))
        for i, var in enumerate(base):
            solution[var] = b[i]
        
        obj_value = sum(c_extended[var] * solution[var] for var in base)
        
        # Remover contribuição das variáveis artificiais (que devem ser zero)
        for var in artificial_vars:
            obj_value += self.M * solution[var]
        
        if self.sense == 'min':
            obj_value = -obj_value
        
        return solution[:self.n], obj_value
    
    def _print_tableau(self, tableau, c, b, base):
        """Imprime o tableau do simplex"""
        print("\nTableau:")
        print("Base\t", end="")
        for j in range(tableau.shape[1]):
            print(f"x_{j+1}\t", end="")
        print("RHS")
        
        for i in range(len(base)):
            print(f"x_{base[i]+1}\t", end="")
            for j in range(tableau.shape[1]):
                print(f"{tableau[i,j]:.3f}\t", end="")
            print(f"{b[i]:.3f}")
        
        print("z\t", end="")
        for j in range(len(c)):
            if j not in base:
                rc = c[j] - sum(c[base[i]] * tableau[i,j] for i in range(len(base)))
                print(f"{rc:.3f}\t", end="")
            else:
                print("0.000\t", end="")
        
        obj_value = sum(c[base[i]] * b[i] for i in range(len(base)))
        print(f"{obj_value:.3f}")

# ============================================================================
# MÉTODO BIG M - FIM
# ============================================================================

# ============================================================================
# SIMPLEX MINIMIZAÇÃO - INÍCIO
# ============================================================================

class SimplexMinimization:
    def __init__(self, c, A, b, constraints_type=None):
        self.c_original = np.array(c, dtype=float)
        self.A_original = np.array(A, dtype=float)
        self.b_original = np.array(b, dtype=float)
        self.constraints_type = constraints_type or ['<='] * len(b)
        self.m, self.n = self.A_original.shape
    
    def solve(self):
        """Simplex para minimização"""
        print("\n=== SIMPLEX PARA MINIMIZAÇÃO ===")
        print("Convertendo problema de minimização para maximização...")
        
        # Verificar se todas as restrições são <=
        if not all(ct == '<=' for ct in self.constraints_type):
            raise ValueError("Simplex para minimização requer todas as restrições do tipo <=")
        
        # Verificar se todos os b são não-negativos
        if not all(bi >= 0 for bi in self.b_original):
            raise ValueError("Simplex para minimização requer todos os termos b ≥ 0")
        
        # Converter min para max (multiplicar função objetivo por -1)
        c_max = -self.c_original
        
        # Usar simplex padrão para resolver o problema de maximização
        simplex_solver = SimplexStandard(c_max, self.A_original, self.b_original, 'max', self.constraints_type)
        solution, obj_value_max = simplex_solver.solve()
        
        # Converter resultado de volta para minimização
        obj_value_min = -obj_value_max
        
        print(f"\nConversão concluída:")
        print(f"Valor da maximização: {obj_value_max:.6f}")
        print(f"Valor da minimização: {obj_value_min:.6f}")
        
        return solution, obj_value_min

# ============================================================================
# SIMPLEX MINIMIZAÇÃO - FIM
# ============================================================================

# ============================================================================
# FUNÇÕES AUXILIARES - INÍCIO
# ============================================================================

def menu_principal():
    """Menu principal para seleção de método"""
    print("\n" + "="*50)
    print("RESOLVEDOR DE PROGRAMAÇÃO LINEAR")
    print("="*50)
    print("1. Método Gráfico (2 variáveis)")
    print("2. Método Simplex Padrão")
    print("3. Método Big M")
    print("4. Simplex para Minimização")
    print("0. Sair")
    print("="*50)
    
    return input("Escolha uma opção: ")

def entrada_dados():
    """Coleta dados do usuário"""
    print("\n=== ENTRADA DE DADOS ===")
    
    n_var = int(input("Número de variáveis: "))
    n_rest = int(input("Número de restrições: "))
    
    # Função objetivo
    sense = input("Tipo de otimização (max/min): ").lower()
    print(f"\nFunção objetivo ({sense}imizar):")
    c = []
    for i in range(n_var):
        coef = float(input(f"Coeficiente de x_{i+1}: "))
        c.append(coef)
    
    # Restrições
    print("\nRestrições:")
    A = []
    b = []
    constraints_type = []
    
    for i in range(n_rest):
        print(f"\nRestrição {i+1}:")
        linha = []
        for j in range(n_var):
            coef = float(input(f"Coeficiente de x_{j+1}: "))
            linha.append(coef)
        A.append(linha)
        
        constraint_type = input("Tipo de restrição (<=, >=, =): ")
        constraints_type.append(constraint_type)
        
        rhs = float(input("Termo independente: "))
        b.append(rhs)
    
    return c, A, b, sense, constraints_type

# ============================================================================
# FUNÇÕES AUXILIARES - FIM
# ============================================================================

# ============================================================================
# PROGRAMA PRINCIPAL - INÍCIO
# ============================================================================

if __name__ == "__main__":
    while True:
        opcao = menu_principal()
        
        if opcao == '0':
            print("Saindo...")
            break
        
        try:
            c, A, b, sense, constraints_type = entrada_dados()
            
            if opcao == '1':
                # Método Gráfico
                solver = GraphicalMethod(c, A, b, sense, constraints_type)
                solution, obj_value = solver.solve()
                
            elif opcao == '2':
                # Simplex Padrão
                solver = SimplexStandard(c, A, b, sense, constraints_type)
                solution, obj_value = solver.solve()
                
            elif opcao == '3':
                # Big M
                solver = SimplexBigM(c, A, b, sense, constraints_type)
                solution, obj_value = solver.solve()
                
            elif opcao == '4':
                # Simplex Minimização
                if sense != 'min':
                    print("Erro: Esta opção é apenas para problemas de minimização!")
                    continue
                solver = SimplexMinimization(c, A, b, constraints_type)
                solution, obj_value = solver.solve()
                
            else:
                print("Opção inválida!")
                continue
            
            print(f"\n=== SOLUÇÃO FINAL ===")
            for i, val in enumerate(solution):
                print(f"x_{i+1} = {val:.6f}")
            print(f"Valor ótimo: {obj_value:.6f}")
            
        except Exception as e:
            print(f"Erro: {str(e)}")
        
        input("\nPressione Enter para continuar...")