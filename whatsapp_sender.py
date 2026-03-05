import requests
import json
from urllib.parse import quote

class WhatsAppSender:
    def __init__(self, api_token=None, phone_number_id=None):
        self.api_token = api_token
        self.phone_number_id = phone_number_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def create_order_message(self, pedido_data):
        """Crear mensaje formateado para WhatsApp"""
        message = f"""🛍️ *NUEVO PEDIDO RECIBIDO* 🛍️

📋 *Detalles del Cliente:*
• Nombre: {pedido_data.get('nombre', 'N/A')}
• Teléfono: {pedido_data.get('telefono', 'N/A')}

📦 *Detalles del Pedido:*
• Producto: {pedido_data.get('producto', 'N/A')}
• Talla: {pedido_data.get('talla', 'N/A')}
• Método de Pago: {pedido_data.get('metodo_pago', 'N/A')}

📍 *Ubicación:*
{pedido_data.get('ubicacion', 'No especificada')}

---
*Pedido recibido via formulario web*"""
        
        return message
    
    def send_whatsapp_message(self, recipient_phone, message_text):
        """Enviar mensaje por WhatsApp usando Meta Business API"""
        try:
            if not self.api_token or not self.phone_number_id:
                return {
                    "success": False,
                    "message": "API token o Phone Number ID no configurados"
                }
            
            # Formatear número de teléfono (quitar +, espacios, guiones)
            formatted_phone = recipient_phone.replace('+', '').replace(' ', '').replace('-', '')
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "text",
                "text": {
                    "body": message_text
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Mensaje enviado exitosamente",
                    "response": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"Error enviando mensaje: {response.status_code}",
                    "error": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error en envío de WhatsApp: {e}"
            }
    
    def send_order_notification(self, pedido_data, admin_phone=None):
        """Enviar notificación del pedido"""
        message = self.create_order_message(pedido_data)
        
        results = {}
        
        # Enviar al cliente (confirmación)
        if pedido_data.get('telefono'):
            client_message = f"""✅ *Pedido Recibido!*

Hola {pedido_data.get('nombre', '')}, hemos recibido tu pedido correctamente.

📦 *Tu pedido:*
• Producto: {pedido_data.get('producto', 'N/A')}
• Talla: {pedido_data.get('talla', 'N/A')}

Nos contactaremos contigo pronto para confirmar los detalles.

Gracias por tu compra! 🛍️"""
            
            results['client'] = self.send_whatsapp_message(
                pedido_data['telefono'], 
                client_message
            )
        
        # Enviar al administrador (notificación)
        if admin_phone:
            results['admin'] = self.send_whatsapp_message(admin_phone, message)
        
        return results

# Alternativa simple usando WhatsApp Web (API gratuita)
class SimpleWhatsAppSender:
    def __init__(self, api_url=None, api_key=None):
        self.api_url = api_url or "https://api.callmebot.com/whatsapp.php"
        self.api_key = api_key
    
    def send_message(self, phone, message):
        """Enviar mensaje usando API gratuita de CallMeBot"""
        try:
            # Formatear número
            formatted_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            # Codificar mensaje
            encoded_message = quote(message)
            
            # Construir URL
            url = f"{self.api_url}?phone={formatted_phone}&text={encoded_message}&apikey={self.api_key}"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "message": "Mensaje enviado"}
            else:
                return {"success": False, "message": f"Error: {response.text}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}
