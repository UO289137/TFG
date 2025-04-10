from flask import Flask, request, send_file, make_response, jsonify
from flask_cors import CORS
import os
import uuid

# Importa tus clases / servicios OOP (ajusta las rutas según tu proyecto)
from services.openai_service import OpenAIService
from services.translator_service import TranslatorService
from services.json_generation_service import JSONGenerationService
from services.data_generation_service import DataGenerationService

# (Opcional) si necesitas loggers
from utils.logger_config import setup_logger
logger = setup_logger("my_logger", "app.log")

app = Flask(__name__)
CORS(app)  # Permite peticiones desde tu frontend React

# Instancia de servicios OOP
openai_service = OpenAIService(logger=logger, model_name="gpt-4o-mini")
translator_service = TranslatorService(logger=logger)
json_gen_service = JSONGenerationService(openai_service, logger=logger)
data_gen_service = DataGenerationService(translator_service, openai_service, logger=logger)


@app.route("/generate", methods=["POST"])
def generate():
    """
    Endpoint que recibe:
      {
        "generator_type": "merlin" | "gold" | "premium" | "oracle",
        "theme": "texto de temática",
        "rows": 123
      }
    Genera un CSV en local y lo retorna para descargar.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        generator_type = data.get("generator_type")
        theme = data.get("theme", "")
        rows = data.get("rows", 100)

        if not generator_type or not theme:
            return jsonify({"error": "Missing 'generator_type' or 'theme'"}), 400

        # 1) Generar nombre de archivo temporal (en local)
        filename = f"{generator_type}_{uuid.uuid4().hex}.csv"
        filepath = os.path.join("tmp", filename)

        # Crea el directorio /tmp si no existe
        os.makedirs("tmp", exist_ok=True)

        # 2) Dependiendo de generator_type, llama al método apropiado.
        if generator_type.lower() == "merlin":
            data_gen_service.generate_data_merlin(
                theme=theme,
                json_generation_service=json_gen_service,
                rows=rows,
                vary_names=True,
                vary_countries=True,
                output_file=filepath
            )
        elif generator_type.lower() == "gold":
            data_gen_service.generate_data_gold(
                theme=theme,
                rows=rows,
                output_file=filepath
            )
        elif generator_type.lower() == "ydata":
            data_gen_service.generate_data_ydata(
                rows=rows,
                output_file=filepath
            )
        else:
            return jsonify({"error": f"Unknown generator_type: {generator_type}"}), 400

        # Verificar que el CSV se haya creado
        if not os.path.exists(filepath):
            return jsonify({"error": "CSV not created"}), 500

        # 3) Devolver el CSV al cliente
        #    O puedes devolver un JSON con un link local si prefieres.
        #    Aquí, lo devolvemos directamente como archivo adjunto.
        return send_file(
            filepath,
            mimetype="text/csv",
            as_attachment=True,
            download_name="synthetic_data.csv"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
