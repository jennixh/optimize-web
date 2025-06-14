from django.db import models
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

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
