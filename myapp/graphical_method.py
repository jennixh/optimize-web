from django.db import models
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

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
        return fig
    
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