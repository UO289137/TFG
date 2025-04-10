# app.py (tu Flask principal)
from flask import Flask, request, send_file, make_response, jsonify
from flask_cors import CORS
import os
import uuid

# Import your service classes
from services.openai_service import OpenAIService
from services.translator_service import TranslatorService
from services.json_generation_service import JSONGenerationService
from services.data_generation_service import DataGenerationService

# Logger if you need it
from utils.logger_config import setup_logger
logger = setup_logger("my_logger", "app.log")

app = Flask(__name__)
CORS(app)

openai_service = OpenAIService(logger=logger, model_name="gpt-4o-mini")
translator_service = TranslatorService(logger=logger)
json_gen_service = JSONGenerationService(openai_service, logger=logger)
data_gen_service = DataGenerationService(translator_service, openai_service, logger=logger)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        if 'generator_type' in request.form and request.form['generator_type'].lower() == 'ctgan':
            generator_type = request.form['generator_type']
            rows = int(request.form.get('rows', 100))

            uploaded_file = request.files.get('file')
            if not uploaded_file:
                return jsonify({"error": "No file was uploaded"}), 400

            # Crear la carpeta tmp si no existe
            os.makedirs("tmp", exist_ok=True)

            # Nombre para el CSV subido
            input_filename = f"{generator_type}_{uuid.uuid4().hex}_input.csv"
            input_filepath = os.path.join("tmp", input_filename)
            uploaded_file.save(input_filepath)

            # Nombre para el CSV final
            output_filename = f"{generator_type}_{uuid.uuid4().hex}_augmented.csv"
            output_filepath = os.path.join("tmp", output_filename)

            # Llamamos a nuestra nueva función
            data_gen_service.generate_data_ctgan(
                input_file=input_filepath,
                rows=rows,
                output_file=output_filepath
            )

            # Verificar que se haya creado el CSV
            if not os.path.exists(output_filepath):
                return jsonify({"error": "CSV not created"}), 500

            # Responder con el CSV
            return send_file(
                output_filepath,
                mimetype="text/csv",
                as_attachment=True,
                download_name="synthetic_data.csv"
            )

        # De lo contrario, tratamos JSON (merlin, gold, etc.)
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        generator_type = data.get("generator_type")
        theme = data.get("theme", "")
        rows = data.get("rows", 100)

        if not generator_type or not theme:
            return jsonify({"error": "Missing 'generator_type' or 'theme'"}), 400

        os.makedirs("tmp", exist_ok=True)
        filename = f"{generator_type}_{uuid.uuid4().hex}.csv"
        filepath = os.path.join("tmp", filename)

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
        else:
            return jsonify({"error": f"Unknown generator_type: {generator_type}"}), 400

        if not os.path.exists(filepath):
            return jsonify({"error": "CSV not created"}), 500

        return send_file(
            filepath,
            mimetype="text/csv",
            as_attachment=True,
            download_name="synthetic_data.csv"
        )

    except Exception as e:
        logger.exception("Error in /generate endpoint")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
