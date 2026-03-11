import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

class GoogleSheetsManager:
    def __init__(self, credentials_file='credentials.json', spreadsheet_id=None):
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autenticarse con Google Sheets API"""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=creds)
        except Exception as e:
            print(f"Error autenticando con Google Sheets: {e}")
            raise
    
    def create_order_row(self, pedido_data):
        """Crear una fila con los datos del pedido"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row = [
            timestamp,                    # Fecha y hora
            pedido_data.get('nombre', ''),
            pedido_data.get('telefono', ''),
            pedido_data.get('producto', ''),
            pedido_data.get('talla', ''),
            pedido_data.get('metodo_pago', ''),
            pedido_data.get('ubicacion', '')
        ]
        return row
    
    def append_order(self, pedido_data, sheet_name='Pedidos'):
        """Agregar un nuevo pedido a Google Sheets"""
        try:
            if not self.spreadsheet_id:
                raise ValueError("Spreadsheet ID no configurado")
            
            row_data = self.create_order_row(pedido_data)
            
            # Agregar la fila al sheet
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:G",
                valueInputOption="USER_ENTERED",
                body={"values": [row_data]}
            ).execute()
            
            return {
                "success": True,
                "message": "Pedido guardado en Google Sheets",
                "updated_cells": result.get('updates', {}).get('updatedCells', 0)
            }
            
        except HttpError as e:
            return {
                "success": False,
                "message": f"Error de Google Sheets API: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error guardando en Google Sheets: {e}"
            }
    
    def setup_sheet(self, sheet_name='Pedidos'):
        """Configurar el sheet con encabezados si no existe"""
        try:
            headers = [
                "Fecha y Hora",
                "Nombre",
                "Teléfono",
                "Producto",
                "Talla",
                "Método de Pago",
                "Ubicación"
            ]
            
            # Verificar si el sheet ya tiene datos
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1:G1"
            ).execute()
            
            # Si no hay datos, agregar encabezados
            if not result.get('values'):
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A:G",
                    valueInputOption="USER_ENTERED",
                    body={"values": [headers]}
                ).execute()
                
            return {"success": True, "message": "Sheet configurado correctamente"}
            
        except Exception as e:
            return {"success": False, "message": f"Error configurando sheet: {e}"}
