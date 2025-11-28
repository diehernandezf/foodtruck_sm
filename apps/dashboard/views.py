from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from apps.ordenes.models import Pedido, DetallePedido
from django.db.models.functions import TruncDate, TruncHour, TruncWeek, TruncMonth
import json


@login_required
def dashboard(request):
    # Obtener parámetros de filtro
    periodo = request.GET.get('periodo', 'mes')  # dia, semana, mes
    
    # Calcular fechas según el período
    ahora = timezone.now()
    
    if periodo == 'dia':
        fecha_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'semana':
        fecha_inicio = ahora - timedelta(days=ahora.weekday())
        fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
    else:  # mes
        fecha_inicio = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Filtrar pedidos pagados en el período
    pedidos = Pedido.objects.filter(
        estado='pagado',
        fecha__gte=fecha_inicio
    )
    
    # KPI 1: Ventas totales
    ventas_totales = pedidos.aggregate(total=Sum('total'))['total'] or 0
    
    # KPI 2: Cantidad de Pedidos
    cantidad_pedidos = pedidos.count()
    
    # KPI 3: Ventas por hora (últimas 24 horas)
    hace_24h = ahora - timedelta(hours=24)
    ventas_por_hora = pedidos.filter(
        fecha__gte=hace_24h
    ).annotate(
        hora=TruncHour('fecha')
    ).values('hora').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('hora')
    
    # Convertir a formato para gráfico
    horas_labels = [v['hora'].strftime('%H:%M') for v in ventas_por_hora]
    horas_datos = [float(v['total']) for v in ventas_por_hora]
    
    # KPI 4: Productos más vendidos (Top 5)
    productos_top = DetallePedido.objects.filter(
        pedido__estado='pagado',
        pedido__fecha__gte=fecha_inicio
    ).values('nombre_producto').annotate(
        cantidad=Sum('cantidad'),
        total=Sum('subtotal')
    ).order_by('-cantidad')[:5]
    
    # KPI 5: Productos menos vendidos (Top 5)
    productos_bottom = DetallePedido.objects.filter(
        pedido__estado='pagado',
        pedido__fecha__gte=fecha_inicio
    ).values('nombre_producto').annotate(
        cantidad=Sum('cantidad'),
        total=Sum('subtotal')
    ).order_by('cantidad')[:5]
    
    # KPI 6: Comparación semanal/mensual
    if periodo == 'mes':
        # Comparar este mes con mes anterior
        fecha_mes_anterior = fecha_inicio - timedelta(days=1)
        fecha_inicio_mes_anterior = fecha_mes_anterior.replace(day=1)
        
        ventas_mes_actual = pedidos.aggregate(total=Sum('total'))['total'] or 0
        ventas_mes_anterior = Pedido.objects.filter(
            estado='pagado',
            fecha__gte=fecha_inicio_mes_anterior,
            fecha__lt=fecha_inicio
        ).aggregate(total=Sum('total'))['total'] or 0
        
        comparacion_periodo_actual = ventas_mes_actual
        comparacion_periodo_anterior = ventas_mes_anterior
        label_comparacion = 'Mes'
    else:
        # Comparar esta semana con semana anterior
        fecha_semana_anterior = fecha_inicio - timedelta(days=7)
        
        ventas_semana_actual = pedidos.aggregate(total=Sum('total'))['total'] or 0
        ventas_semana_anterior = Pedido.objects.filter(
            estado='pagado',
            fecha__gte=fecha_semana_anterior,
            fecha__lt=fecha_inicio
        ).aggregate(total=Sum('total'))['total'] or 0
        
        comparacion_periodo_actual = ventas_semana_actual
        comparacion_periodo_anterior = ventas_semana_anterior
        label_comparacion = 'Semana'
    
    # KPI 7: Tasa de crecimiento
    if comparacion_periodo_anterior > 0:
        tasa_crecimiento = ((comparacion_periodo_actual - comparacion_periodo_anterior) / comparacion_periodo_anterior) * 100
    else:
        tasa_crecimiento = 0 if comparacion_periodo_actual == 0 else 100
    
    # KPI 8: Tasa de Repetición de Clientes
    # Clientes únicos en el período
    clientes_periodo = pedidos.values('usuario').distinct().count()
    
    # Clientes que compraron más de una vez
    clientes_repetidos = Pedido.objects.filter(
        usuario__isnull=False,
        estado='pagado',
        fecha__gte=fecha_inicio
    ).values('usuario').annotate(
        compras=Count('id')
    ).filter(compras__gt=1).count()
    
    if clientes_periodo > 0:
        tasa_repeticion = (clientes_repetidos / clientes_periodo) * 100
    else:
        tasa_repeticion = 0
    
    # Preparar datos para contexto
    context = {
        'periodo': periodo,
        'ventas_totales': float(ventas_totales),
        'cantidad_pedidos': cantidad_pedidos,
        'horas_labels': json.dumps(horas_labels),
        'horas_datos': json.dumps(horas_datos),
        'productos_top': list(productos_top),
        'productos_bottom': list(productos_bottom),
        'comparacion_periodo_actual': float(comparacion_periodo_actual),
        'comparacion_periodo_anterior': float(comparacion_periodo_anterior),
        'label_comparacion': label_comparacion,
        'tasa_crecimiento': round(tasa_crecimiento, 2),
        'tasa_repeticion': round(tasa_repeticion, 2),
        'clientes_periodo': clientes_periodo,
    }
    
    return render(request, 'dashboard.html', context)