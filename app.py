// SCRIPT MINIMALISTA - Solo limpieza, sin obtener datos
// La app Streamlit lee directamente de la API

function crearTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }
  
  // Ejecutar solo los DOMINGOS a las 5 AM para limpieza
  ScriptApp.newTrigger("limpiarDatosDominical")
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.SUNDAY)
    .atHour(5)
    .create();
  
  Logger.log("✅ Trigger creado: Limpieza los domingos a las 5 AM");
}

function limpiarDatosDominical() {
  // Solo ejecuta si es domingo a las 5 AM
  var ahora = new Date();
  var dia = ahora.getDay();
  var hora = ahora.getHours();
  
  if (dia === 0 && hora === 5) {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var hojas = [
      "Grupo A Lunes", "Grupo A Martes", "Grupo A Miércoles",
      "Grupo B Jueves", "Grupo B Viernes",
      "Grupo C Jueves", "Grupo C Viernes",
      "Final Sábado"
    ];
    
    hojas.forEach(function(nombre) {
      var h = ss.getSheetByName(nombre);
      if (h) {
        h.getRange("A7:E67").clearContent();
        Logger.log("🗑️ Limpiada: " + nombre);
      }
    });
    
    Logger.log("✅ Limpieza dominical completada");
  }
}
