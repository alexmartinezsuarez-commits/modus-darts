function actualizarDatosCompletos() {
  var BASE = "https://api-igamedc.igamemedia.com/api/mss-web";
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // 1. Limpiar hoja de estadísticas generales (esta sí siempre)
  var hojaDuros = ss.getSheetByName("Estadísticas Profundas") || ss.insertSheet("Estadísticas Profundas");
  hojaDuros.clearContents();

  // ✅ VERIFICAR SI ES DOMINGO A LAS 5 AM O MÁS
  var ahora = new Date();
  var diaSemana = ahora.getDay(); // 0 = Domingo, 1 = Lunes... 6 = Sábado
  var horaActual = ahora.getHours();
  
  var esDomingo = (diaSemana === 0);
  var esDesde5AM = (horaActual >= 5);
  var debeHacerLimpiezaDominical = esDomingo && esDesde5AM;

  Logger.log("📅 Día: " + ["Domingo","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"][diaSemana]);
  Logger.log("⏰ Hora: " + horaActual + ":00");
  
  if (debeHacerLimpiezaDominical) {
    Logger.log("✅ LIMPIEZA DOMINICAL ACTIVADA (Domingo >= 5 AM)");
  } else if (esDomingo && !esDesde5AM) {
    Logger.log("⏳ Espera a las 5 AM para limpieza dominical (Aún en madrugada del sábado-domingo)");
  } else {
    Logger.log("📊 Modo normal: Solo actualizar si hay datos nuevos");
  }

  function buscarHoja(nombreBuscado) {
    var hojas = ss.getSheets();
    var normalizar = function(txt) {
      return txt.toLowerCase().replace(/\s+/g, " ").trim();
    };
    var objetivo = normalizar(nombreBuscado);
    for (var i = 0; i < hojas.length; i++) {
      if (normalizar(hojas[i].getName()) === objetivo) {
        return hojas[i];
      }
    }
    return null;
  }

  // ✅ SI ES DOMINGO A LAS 5 AM O DESPUÉS: Borrar TODAS las hojas de la semana
  if (debeHacerLimpiezaDominical) {
    var todasLasHojas = [
      "Grupo A Lunes", "Grupo A Martes", "Grupo A Miércoles",
      "Grupo B Jueves", "Grupo B Viernes",
      "Grupo C Jueves", "Grupo C Viernes",
      "Final Sábado"
    ];

    todasLasHojas.forEach(function(nombre) {
      var h = buscarHoja(nombre);
      if (h) {
        h.getRange("A7:E67").clearContent();
        Logger.log("🗑️ Limpiada: " + nombre);
      }
    });
    Logger.log("✅ LIMPIEZA DOMINICAL (5 AM) COMPLETADA - Todas las hojas vaciadas para la nueva semana");
  }

  try {
    var resBase = UrlFetchApp.fetch(BASE + "/results-fixtures");
    var jsonBase = JSON.parse(resBase.getContentText());
    var weekActiva = jsonBase.selected?.week || "";

    var grupos = jsonBase.selected?.groups || [{id: 1}, {id: 2}, {id: 3}, {id: 8}];
    var partidosBrutos = [];

    for (var g = 0; g < grupos.length; g++) {
      var urlGrupo = BASE + "/results-fixtures?group=" + grupos[g].id + (weekActiva ? "&week=" + weekActiva : "");
      var resG = UrlFetchApp.fetch(urlGrupo);
      var jsonG = JSON.parse(resG.getContentText());
      var p = jsonG.Fixtures || jsonG.fixtures || [];
      partidosBrutos = partidosBrutos.concat(p);
    }

    var partidosUnicos = {};
    partidosBrutos.forEach(function(p) {
      var id = p.gameId || p.Id || p.id;
      if (id) partidosUnicos[id] = p;
    });

    var partidos = Object.values(partidosUnicos);
    var resultados = [];

    for (var i = 0; i < partidos.length; i++) {
      var p = partidos[i];
      var id = p.gameId || p.Id || p.id;
      var fila = {
        gameId: id, Fecha: p.fixture || "", Jugador_Casa: p.playerHome || "", Jugador_Fuera: p.playerAway || "",
        Casa_180s: "", Casa_Average: "", Casa_CheckoutPct: "", Casa_LegsWon: "",
        Fuera_180s: "", Fuera_Average: "", Fuera_CheckoutPct: "", Fuera_LegsWon: ""
      };

      try {
        var res = UrlFetchApp.fetch(BASE + "/fixtures/" + id);
        var detalle = JSON.parse(res.getContentText());
        var stats = detalle.playersStatistics?.statistics;

        if (stats && stats.length >= 2 && stats[0].average !== null) {
          var s1 = stats[0];
          var s2 = stats[1];
          var partidoIniciado = (s1.average > 0 || s2.average > 0 || (p.status && p.status.toLowerCase() !== 'not started'));

          if (partidoIniciado) {
            fila.Casa_180s = s1.turns180 ?? "";
            fila.Casa_Average = s1.average ?? "";
            fila.Casa_CheckoutPct = s1.checkoutPercentage ?? "";
            fila.Casa_LegsWon = p.scorePlayerHome ?? "";
            fila.Fuera_180s = s2.turns180 ?? "";
            fila.Fuera_Average = s2.average ?? "";
            fila.Fuera_CheckoutPct = s2.checkoutPercentage ?? "";
            fila.Fuera_LegsWon = p.scorePlayerAway ?? "";
          }
        }
      } catch (e) {}
      resultados.push(fila);
      Utilities.sleep(300);
    }

    var gruposPorHoja = {};
    var dias = ["Domingo","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"];

    resultados.forEach(function(f){
      if (!f.Fecha) return;
      var fechaUTC = new Date(f.Fecha);
      var txt = Utilities.formatDate(fechaUTC,"Europe/Madrid","yyyy-MM-dd HH:mm:ss");
      var partes = txt.split(/[- :]/);
      var d = new Date(partes[0], partes[1]-1, partes[2], partes[3], partes[4]);
      var horaReal = d.getHours(); 

      if (horaReal < 6) d.setDate(d.getDate() - 1);

      var dia = d.getDay();
      var nombreDia = dias[dia];
      var hoja = "";

      if (dia >= 1 && dia <= 3) hoja = "Grupo A " + nombreDia;
      else if (dia === 4 || dia === 5) {
        if (horaReal >= 19 || horaReal < 6) hoja = "Grupo B " + nombreDia;
        else hoja = "Grupo C " + nombreDia;
      } 
      else if (dia === 6) hoja = "Final Sábado";

      if (hoja) {
        if (!gruposPorHoja[hoja]) gruposPorHoja[hoja] = [];
        gruposPorHoja[hoja].push(f);
      }
    });

    // ✅ Lógica de borrado:
    // - Si es domingo >= 5 AM: Ya borramos todo arriba, solo escribimos
    // - Si NO es domingo: Solo borrar las hojas que tienen datos nuevos
    for (var nombreHoja in gruposPorHoja) {
      var h = buscarHoja(nombreHoja);
      if (!h) continue;

      var data = gruposPorHoja[nombreHoja];
      
      // Solo borrar si NO es limpieza dominical Y hay datos nuevos
      if (!debeHacerLimpiezaDominical && data.length > 0) {
        h.getRange("A7:E67").clearContent();
        Logger.log("🗑️ Limpiada: " + nombreHoja + " (hay " + data.length + " partidos nuevos)");
      }

      var salida = [];
      data.forEach(function(p){
        var jugado = (p.Casa_Average !== "");
        var c1 = (jugado && p.Casa_CheckoutPct !== "") ? Number(p.Casa_CheckoutPct) / 100 : "";
        var c2 = (jugado && p.Fuera_CheckoutPct !== "") ? Number(p.Fuera_CheckoutPct) / 100 : "";

        salida.push([p.Jugador_Casa, (jugado ? p.Casa_LegsWon : ""), (jugado ? p.Casa_180s : ""), (jugado ? p.Casa_Average : ""), c1]);
        salida.push([p.Jugador_Fuera, (jugado ? p.Fuera_LegsWon : ""), (jugado ? p.Fuera_180s : ""), (jugado ? p.Fuera_Average : ""), c2]);
      });

      if (salida.length > 0) {
        h.getRange(7, 1, salida.length, 5).setValues(salida);
        Logger.log("✅ Actualizada hoja: " + nombreHoja);
      }
    }
    
    if (debeHacerLimpiezaDominical) {
      Logger.log("✅ FIN - Limpieza dominical (5 AM) completada + datos nuevos actualizados");
    } else if (esDomingo && !esDespe5AM) {
      Logger.log("⏳ FIN - Aún es madrugada. Limpieza pendiente a las 5 AM");
    } else {
      Logger.log("✅ FIN - Datos actualizados. Solo se borraron hojas con datos nuevos");
    }

  } catch(e) {
    Logger.log("❌ ERROR: " + e);
  }
}                  
