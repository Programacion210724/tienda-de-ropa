from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from google_sheets import GoogleSheetsManager
from whatsapp_sender import SimpleWhatsAppSender
app = FastAPI(title="Backend Tienda de Ropa")

# Configuración de servicios
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "1_QkV3pHKqSDfQzCozzFK-JvqMytv6ygiy3yGaFWXSvo")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "TU_API_KEY")
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "TU_NUMERO_ADMIN")

# Inicializar servicios
credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
sheets_manager = GoogleSheetsManager(
    credentials_file=credentials_path,
    spreadsheet_id=GOOGLE_SPREADSHEET_ID
) if os.path.exists(credentials_path) else None

whatsapp_sender = SimpleWhatsAppSender(api_key=WHATSAPP_API_KEY)
# CORS permite que tu HTML (abierto en el navegador) pueda llamar a tu API en localhost
# Para aprender es común usarlo así. En producción se limita a dominios específicos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # En producción: poner tu dominio, no "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Pedido(BaseModel):
    # Field(...): significa "obligatorio"
    nombre: str = Field(..., min_length=1, description="Nombre del cliente")
    telefono: str = Field(..., min_length=1, description="Teléfono/WhatsApp del cliente")
    # Los demás pueden ser opcionales si quieres (aquí los dejo opcionales)
    producto: str | None = None
    talla: str | None = None
    metodo_pago: str | None = None
    # El link de Google Maps se recibe como texto (string)
    ubicacion: str | None = None

@app.get("/")
def health_check():
    # Ruta simple para probar que el servidor responde
    return {"ok": True, "message": "Servidor activo"}

@app.post("/pedido")
def crear_pedido(pedido: Pedido):
    # Convertir pedido a diccionario
    pedido_data = pedido.dict()
    
    # Debug: imprimir valores
    print(f"DEBUG: sheets_manager existe: {sheets_manager is not None}")
    print(f"DEBUG: GOOGLE_SPREADSHEET_ID: {GOOGLE_SPREADSHEET_ID}")
    print(f"DEBUG: ¿Coincide el ID?: {GOOGLE_SPREADSHEET_ID == '1_QkV3pHKqSDfQzCozzFK-JvqMytv6ygiy3yGaFWXSvo'}")
    
    # Resultado de Google Sheets
    sheets_result = None
    
    # Guardar en Google Sheets si está configurado
    if sheets_manager and GOOGLE_SPREADSHEET_ID == "1_QkV3pHKqSDfQzCozzFK-JvqMytv6ygiy3yGaFWXSvo":
        try:
            print("DEBUG: Intentando guardar en Google Sheets...")
            # Usar la hoja "pedidos"
            sheets_result = sheets_manager.append_order(pedido_data, sheet_name='pedidos')
            print(f"DEBUG: Resultado Google Sheets: {sheets_result}")
        except Exception as e:
            print(f"DEBUG: Error en Google Sheets: {e}")
            sheets_result = {"success": False, "message": f"Error Google Sheets: {e}"}
    else:
        print("DEBUG: No se cumple la condición para Google Sheets")
    
    # Construir respuesta
    response = {
        "ok": True,
        "message": "Pedido recibido correctamente",
        "data": pedido_data,
        "google_sheets": sheets_result
    }
    
    return response