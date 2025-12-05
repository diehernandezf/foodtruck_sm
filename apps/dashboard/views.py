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
        fecha_inicio_anterior = fecha_inicio - timedelta(days=1)
        fecha_fin_anterior = fecha_inicio
    elif periodo == 'semana':
        fecha_inicio = ahora - timedelta(days=ahora.weekday())
        fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_inicio_anterior = fecha_inicio - timedelta(days=7)
        fecha_fin_anterior = fecha_inicio
    else:  # mes
        fecha_inicio = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Calcular primer día del mes anterior
        if fecha_inicio.month == 1:
            fecha_inicio_anterior = fecha_inicio.replace(year=fecha_inicio.year - 1, month=12)
        else:
            fecha_inicio_anterior = fecha_inicio.replace(month=fecha_inicio.month - 1)
        fecha_fin_anterior = fecha_inicio
    
    # Filtrar pedidos del período actual
    pedidos = Pedido.objects.filter(
        estado__in=['pagado', 'completado'],
        fecha__gte=fecha_inicio
    )
    
    # Filtrar pedidos del período anterior
    pedidos_anteriores = Pedido.objects.filter(
        estado__in=['pagado', 'completado'],
        fecha__gte=fecha_inicio_anterior,
        fecha__lt=fecha_fin_anterior
    )
    
    # KPI 1: Ventas totales
    ventas_totales = pedidos.aggregate(total=Sum('total'))['total'] or 0
    
    # KPI 2: Cantidad de Pedidos
    cantidad_pedidos = pedidos.count()
    
    # KPI 3: Ventas por hora (últimas 24 horas)
    hace_24h = ahora - timedelta(hours=24)
    ventas_por_hora = Pedido.objects.filter(
        estado__in=['pagado', 'completado'],
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
        pedido__estado__in=['pagado', 'completado'],
        pedido__fecha__gte=fecha_inicio
    ).values('nombre_producto').annotate(
        cantidad=Sum('cantidad'),
        total=Sum('subtotal')
    ).order_by('-cantidad')[:5]
    
    # KPI 5: Productos menos vendidos (Top 5)
    productos_bottom = DetallePedido.objects.filter(
        pedido__estado__in=['pagado', 'completado'],
        pedido__fecha__gte=fecha_inicio
    ).values('nombre_producto').annotate(
        cantidad=Sum('cantidad'),
        total=Sum('subtotal')
    ).order_by('cantidad')[:5]
    
    # KPI 6: Comparación de períodos
    ventas_periodo_actual = ventas_totales
    ventas_periodo_anterior = pedidos_anteriores.aggregate(total=Sum('total'))['total'] or 0
    
    # KPI 7: Tasa de crecimiento
    if ventas_periodo_anterior > 0:
        tasa_crecimiento = ((ventas_periodo_actual - ventas_periodo_anterior) / ventas_periodo_anterior) * 100
    else:
        tasa_crecimiento = 0 if ventas_periodo_actual == 0 else 100
    
    # KPI 8: Tasa de Repetición de Clientes
    # Clientes únicos en el período actual
    clientes_periodo = pedidos.filter(
        usuario__isnull=False
    ).values('usuario').distinct().count()
    
    # Clientes que compraron más de una vez en el período actual
    clientes_repetidos = pedidos.filter(
        usuario__isnull=False
    ).values('usuario').annotate(
        compras=Count('id')
    ).filter(compras__gt=1).count()
    
    if clientes_periodo > 0:
        tasa_repeticion = (clientes_repetidos / clientes_periodo) * 100
    else:
        tasa_repeticion = 0
    
    # Determinar label de comparación
    if periodo == 'dia':
        label_comparacion = 'Día'
    elif periodo == 'semana':
        label_comparacion = 'Semana'
    else:
        label_comparacion = 'Mes'
    
    # Preparar datos para contexto
    context = {
        'periodo': periodo,
        'ventas_totales': float(ventas_totales),
        'cantidad_pedidos': cantidad_pedidos,
        'horas_labels': json.dumps(horas_labels),
        'horas_datos': json.dumps(horas_datos),
        'productos_top': list(productos_top),
        'productos_bottom': list(productos_bottom),
        'comparacion_periodo_actual': float(ventas_periodo_actual),
        'comparacion_periodo_anterior': float(ventas_periodo_anterior),
        'label_comparacion': label_comparacion,
        'tasa_crecimiento': round(tasa_crecimiento, 2),
        'tasa_repeticion': round(tasa_repeticion, 2),
        'clientes_periodo': clientes_periodo,
    }
    
    return render(request, 'dashboard.html', context)