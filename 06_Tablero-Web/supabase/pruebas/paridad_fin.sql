-- Paridad de las fórmulas financieras con 04_Finanzas/modelo-financiero.xlsx
-- EMPIEZA!C8   = pagados*precio - premio - premio_vendedor - gastos_varios
-- EMPIEZA!C10  = max(0, ceil((piso+premio+premio_vendedor+varios)/precio) - pagados)
-- REGLA-PREMIO G al nivel N = prob*neto_vendido + (1-prob)*neto_consolacion
--
-- Con los supuestos actuales (SUPUESTOS!B5=6000, B9=2000000, B12=100000, B13=50000, B20=0.08,
-- B21=0.10, B14=0.10, B4=1000, B25=3000000, consolacion=210000, tizumba=0):
--   N=0   → esperado = -2.260.000  (todo costos y premio, nada de ingreso)
--   N=300 → esperado = ~-513.900   (REGLA-PREMIO fila A8/E8/F8/G8 recalculado)
--   N=750 → esperado = ~1.981.700  (fila A15)
--   N=860 → caso vendido >= piso 3M  (fila A17 columna H = SI)
--
-- Comprueba el resultado contra una recalc del xlsx:
--   "/c/Program Files/LibreOffice/program/soffice.exe" --headless --calc \
--     --convert-to xlsx --outdir /tmp 04_Finanzas/modelo-financiero.xlsx
--   openpyxl(data_only=True): REGLA-PREMIO!G8, G11, G15, EMPIEZA!C8/C10/C12 con C5 variable.

-- 1) EMPIEZA!C8/C10/C12 con el número actual de pagados
select 'estadisticas() REAL' as caso, (estadisticas()->'real') as valor;

-- 2) REGLA-PREMIO al nivel 0, 300, 500, 750, 860, 900 (comparar con xlsx recalculado)
select 'nivel 0'   as caso, rifa.proyeccion_regla_premio(0)   as valor
union all select 'nivel 300', rifa.proyeccion_regla_premio(300)
union all select 'nivel 500', rifa.proyeccion_regla_premio(500)
union all select 'nivel 750', rifa.proyeccion_regla_premio(750)
union all select 'nivel 860', rifa.proyeccion_regla_premio(860)
union all select 'nivel 900', rifa.proyeccion_regla_premio(900);

-- 3) RLS: Sofía (turno) no debe poder llamar estadísticas, stats_vendedores,
--    entregar_efectivo, consignar, pagos_efectivo_pendientes.
--    Ejecutar en el panel SQL con el token de Sofía (via supabase.auth) y confirmar
--    que todas devuelven 'solo admin'.
