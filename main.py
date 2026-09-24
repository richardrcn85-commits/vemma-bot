import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# Configuración de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Cargar claves desde el entorno de Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Inicializar cliente de Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Prompt Socrático Vemma
SYSTEM_PROMPT = """
Sos "Vemma", un tutor de física experto para aspirantes al examen de ingreso de la UNA (Universidad Nacional de Asunción) en Paraguay.

REGLAS PEDAGÓGICAS OBLIGATORIAS:
1. Usá el voseo paraguayo (ej. "fijate", "¿cuál creés que es?").
2. NUNCA resuelvas el ejercicio de entrada ni des el resultado directo. Sé estrictamente Socrático: guiá al alumno haciendo preguntas orientadoras.
3. El estándar de gravedad es g = 9.8 m/s^2. No usés cálculo diferencial ni fórmulas universitarias complejas.
4. Mantené un tono alentador, claro y breve (máximo 120 palabras por respuesta).
5. Guiá siempre siguiendo la estructura de 4 pasos: Datos, Planteo, Despeje, Resultado.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_bienvenida = (
        "¡Hola! Soy Vemma, tu tutor 24/7 de Física para el ingreso a la UNA. 🇵🇾\n\n"
        "Contame, ¿con qué ejercicio o concepto tenés dudas hoy?"
    )
    await update.message.reply_text(mensaje_bienvenida)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text
    
    prompt_completo = f"{SYSTEM_PROMPT}\n\nConsulta del alumno: {texto_usuario}"
    
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_completo
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error con Gemini: {e}")
        await update.message.reply_text("Ocurrió un pequeño inconveniente al procesar tu consulta. Probá de nuevo en unos segundos.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    print("Bot Vemma activo...")
    app.run_polling()