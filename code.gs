/**
 * Google Apps Script - Backend para Tienda de Ropa
 * Este código reemplaza tus 3 archivos de Python
 * 
 * INSTRUCCIONES:
 * 1. Abre tu Google Sheets
 * 2. Extensiones > Apps Script
 * 3. Borra todo y pega este código
 * 4. Guarda y despliega como Web App
 * 5. Copia la URL y úsala en tu HTML
 */

// Configuración - cambia estos valores
const CONFIG = {
  // Email para notificaciones
  adminEmail: "kennedybizarroreyes@gmail.com"
};

/**
 * Esta función se ejecuta cuando alguien envía el formulario
 * Equivalente al @app.post("/pedido") de FastAPI
 * Acepta tanto POST como GET
 */
function doPost(e) {
  return handleRequest(e);
}

function doGet(e) {
  return handleRequest(e);
}

function handleRequest(e) {
  try {
    // Para depurar - ver qué datos llegan
    Logger.log("Evento completo: " + JSON.stringify(e));
    
    // Obtener los datos del formulario (funciona con POST y GET)
    let parametros = {};
    
    if (e.parameter && Object.keys(e.parameter).length > 0) {
      // GET request (parámetros en URL)
      parametros = e.parameter;
      Logger.log("Método GET - parámetros: " + JSON.stringify(parametros));
    } else if (e.postData && e.postData.contents) {
      // POST request
      const contents = e.postData.contents;
      Logger.log("Contenido POST: " + contents);
      parametros = {};
      contents.split('&').forEach(part => {
        const [key, value] = part.split('=');
        if (key) {
          parametros[decodeURIComponent(key)] = decodeURIComponent(value || '');
        }
      });
      Logger.log("Parámetros parseados: " + JSON.stringify(parametros));
    } else {
      throw new Error("No se recibieron datos. Parameter keys: " + (e.parameter ? Object.keys(e.parameter).length : "null") + ", postData: " + (e.postData ? "exists" : "null"));
    }
    
    // Si no hay parámetros, usar valores por defecto para prueba
    if (Object.keys(parametros).length === 0) {
      Logger.log("No hay parámetros, creando datos de prueba");
      parametros = {
        nombre: "Prueba",
        telefono: "999999999",
        producto: "Camisa",
        talla: "M",
        metodo_pago: "Yape",
        ubicacion: "-test"
      };
    }
    
    // Extraer los datos (igual que tu modelo Pedido en Python)
    const pedido = {
      nombre: parametros.nombre || "",
      telefono: "'" + (parametros.telefono || ""),
      producto: parametros.producto || "",
      talla: parametros.talla || "",
      metodo_pago: parametros.metodo_pago || "",
      ubicacion: parametros.ubicacion || "",
      fecha: new Date().toLocaleString("es-PE", { timeZone: "America/Lima" })
    };
    
    // Guardar en Google Sheets
    const resultadoSheets = guardarEnSheets(pedido);
    if (!resultadoSheets.success) {
      Logger.log("Error guardando en Sheets: " + resultadoSheets.message);
    }

    // Enviar notificación por email
    if (CONFIG.adminEmail) {
      const resultadoEmail = enviarNotificacionEmail(pedido);
      if (!resultadoEmail.success) {
        Logger.log("Error enviando email: " + resultadoEmail.message);
      }
    }
    
    // Devolver respuesta exitosa
    return ContentService
      .createTextOutput(JSON.stringify({
        success: true,
        message: "Pedido recibido correctamente",
        data: pedido
      }))
      .setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    Logger.log("Error general: " + error.message);
    // Devolver respuesta de error
    return ContentService
      .createTextOutput(JSON.stringify({
        success: false,
        message: "Error: " + error.message
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Guardar pedido en Google Sheets
 * Equivalente a GoogleSheetsManager.append_order()
 */
function guardarEnSheets(pedido) {
  try {
    // Obtener la hoja de cálculo activa (o puedes especificar ID)
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = spreadsheet.getSheetByName("Pedidos") || spreadsheet.getActiveSheet();
    
    // Crear la fila con los datos
    const fila = [
      pedido.fecha,
      pedido.nombre,
      pedido.telefono,
      pedido.producto,
      pedido.talla,
      pedido.metodo_pago,
      pedido.ubicacion
    ];
    
    // Agregar la fila a la hoja
    sheet.appendRow(fila);
    
    // Agregar encabezados si es la primera fila
    if (sheet.getLastRow() === 1) {
      sheet.getRange("A1:G1").setValues([[
        "Fecha", "Nombre", "Teléfono", "Producto", "Talla", "Método de Pago", "Ubicación"
      ]]);
    }
    
    return { success: true, message: "Guardado en Sheets" };
    
  } catch (error) {
    return { success: false, message: "Error en Sheets: " + error.message };
  }
}

/**
 * Enviar notificación por email
 */
function enviarNotificacionEmail(pedido) {
  try {
    const destinatario = CONFIG.adminEmail;
    const asunto = "Nuevo pedido - " + pedido.producto;
    const cuerpo = `Nuevo pedido recibido:

Cliente: ${pedido.nombre}
Teléfono: ${pedido.telefono}
Producto: ${pedido.producto}
Talla: ${pedido.talla}
Método de Pago: ${pedido.metodo_pago}
Ubicación: ${pedido.ubicacion || "No especificada"}

Fecha: ${pedido.fecha}`;

    GmailApp.sendEmail(destinatario, asunto, cuerpo);
    Logger.log("Email enviado exitosamente a " + destinatario);
    return { success: true };
  } catch (error) {
    Logger.log("Error email: " + error.message);
    return { success: false, message: error.message };
  }
}

/**
 * Función de prueba - Equivalente al health check
 */
function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({
      ok: true,
      message: "Servidor activo - Tienda de Ropa API"
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Función para probar el guardado
 */
/**
 * Mostrar notificación/alerta en Sheets cuando llega nuevo pedido
 * Esta función se ejecuta automáticamente cuando se编辑a la hoja
 */
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  const range = e.range;
  
  // Verificar si es la hoja de Pedidos y hay una nueva fila
  if (sheet.getName() === "Pedidos" && range.getRow() > 1) {
    const lastRow = sheet.getLastRow();
    
    // Si hay al menos un pedido nuevo
    if (lastRow > 1) {
      // Obtener los datos del último pedido
      const pedido = sheet.getRange(lastRow, 1, 1, 7).getValues()[0];
      
      // Mostrar notificación tipo toast
      sheet.showToast("🛍️ Nuevo pedido: " + pedido[3] + " - " + pedido[1], "NovaWear", 10);
      
      Logger.log("Alerta mostrada para pedido: " + pedido[3]);
    }
  }
}

/**
 * Configurar activador para mostrar alertas automáticas
 * Ejecuta esto una vez para activar las notificaciones en Sheets
 */
function crearActivador() {
  // Eliminar activadores anteriores si existen
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === "onEdit") {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Crear nuevo activador que detecta cambios en la hoja
  ScriptApp.newTrigger("onEdit")
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onEdit()
    .create();
  
  Logger.log("Activador creado exitosamente");
  return "Activador configurado. Ahora recibirás alertas en Sheets.";
}

function testGuardar() {
  const pedidoPrueba = {
    nombre: "Juan Pérez",
    telefono: "999999999",
    producto: "Camisa Formal",
    talla: "M",
    metodo_pago: "Yape",
    ubicacion: "https://maps.google.com/...",
    fecha: new Date().toLocaleString()
  };
  
  const resultado = guardarEnSheets(pedidoPrueba);
  Logger.log(JSON.stringify(resultado));
}
