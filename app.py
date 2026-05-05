1. LIVE

Esta pestaña debe mostrar automáticamente la jornada que se está jugando en ese momento según la hora actual.

🕒 HORARIOS DE LAS JORNADAS
🟦 Grupo A (mañana)
Lunes → 10:00 a 16:00
Martes → 10:00 a 16:00
Miércoles → 10:00 a 16:00
🟨 Grupo C (tarde)
Jueves → 13:00 a 19:00
Viernes → 13:00 a 19:00
🌙 Grupo B + Final (noche, cruza medianoche)
Jueves → 22:00 a 03:00 (día siguiente)
Viernes → 22:00 a 03:00 (día siguiente)
Sábado (Final) → 22:00 a 03:00 (día siguiente)
⚙️ LÓGICA A IMPLEMENTAR

👉 Condiciones claras:

Solo puede haber una jornada activa a la vez (no hay solapamientos)
Detectar jornada según:
Día de la semana
Hora actual
⚠️ CASO ESPECIAL (MUY IMPORTANTE)

Las jornadas nocturnas cruzan de día:

Ejemplo:

Viernes 01:30 → pertenece a Grupo B Jueves
Sábado 01:30 → pertenece a Grupo B Viernes
Domingo 01:30 → pertenece a Final Sábado

👉 Debes:

Asociar correctamente la jornada al día en que empieza
No al día actual
🟢 COMPORTAMIENTO DE LIVE
Si hay jornada activa → mostrarla directamente
Si no hay:
Mostrar: “No hay partidos en juego ahora”
Opcional: mostrar próxima jornada
💰 2. VALUE BETS
Misma prioridad que LIVE
Acceso directo desde navegación principal
Mantener mejoras visuales ya definidas
📊 3. RESULTADOS Y ESTADÍSTICAS
Contenedor de todas las jornadas:
Grupo A (Lunes, Martes, Miércoles)
Grupo B (Jueves, Viernes)
Grupo C (Jueves, Viernes)
Final Sábado
Resumen Semanal

👉 Mostrar como lista o tarjetas
👉 Al hacer clic → navegar a esa sección
