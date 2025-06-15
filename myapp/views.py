# myapp/views.py

import io
import base64
import json
import sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .graphical_method import GraphicalMethod
from django.shortcuts import render
from .big_m import SimplexBigM 

def index(request):
    return render(request, 'main.html')

@csrf_exempt  
def solve_linear_program(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        c = data['c']
        A = data['A']
        b = data['b']
        sense = data.get('sense', 'max')
        constraints_type = data.get('constraints_type', None)

        try:
            gm = GraphicalMethod(c, A, b, sense=sense, constraints_type=constraints_type)
            point, value = gm.solve()

        # Gerar gráfico e salvar em memória
            fig = gm._plot_solution(gm._find_vertices(), tuple(point))  # <- aqui está a correção
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

            return JsonResponse({
                'solution_point': point.tolist(),
                'optimal_value': value,
                'plot_image': img_base64
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'message': 'Only POST allowed'}, status=405)

@csrf_exempt
def solve_bigm(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            c = data['c']
            A = data['A']
            b = data['b']
            sense = data.get('sense', 'max')
            constraints_type = data.get('constraints_type', None)

            # Redirecionar stdout para capturar os prints
            log_buffer = io.StringIO()
            sys_stdout = sys.stdout
            sys.stdout = log_buffer

            # Resolver o problema
            solver = SimplexBigM(c, A, b, sense=sense, constraints_type=constraints_type)
            solution, optimal_value = solver.solve()

            # Restaurar o stdout
            sys.stdout = sys_stdout

            # Pegar conteúdo do log
            log_text = log_buffer.getvalue()

            return JsonResponse({
                'solution': solution.tolist(),
                'optimal_value': optimal_value,
                'log': log_text  # <-- envia o log para o frontend
            })

        except Exception as e:
            sys.stdout = sys_stdout  # garantir que restaura mesmo com erro
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'message': 'Only POST allowed'}, status=405)