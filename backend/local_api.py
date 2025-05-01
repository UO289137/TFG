# local_api.py

import os
import uuid
import logging

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

from services.openai_service import OpenAIService
from services.translator_service import TranslatorService
from services.json_generation_service import JSONGenerationService
from services.data_generation_service import DataGenerationService
from utils.logger_config import LoggerUtils

class WebAPI:
    """
    Sub­sistema Web API que expone el endpoint /generate y orquesta
    los servicios de generación de datos.
    """

    def __init__(self,
                 logger_name: str = "my_logger",
                 log_file: str = "app.log"):
        # Logger
        self.logger: logging.Logger = LoggerUtils.setup_logger(logger_name, log_file)

        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)

        # Servicios
        self.openai_service      = OpenAIService(self.logger, model_name="gpt-4o-mini")
        self.translator_service  = TranslatorService(self.logger)
        self.json_gen_service    = JSONGenerationService(self.openai_service, self.logger)
        self.data_gen_service    = DataGenerationService(self.translator_service,
                                                         self.openai_service,
                                                         self.logger)

        # Registrar rutas
        self._register_routes()

    def _register_routes(self):
        @self.app.route("/generate", methods=["POST"])
        def generate():
            try:
                # --- CTGAN / Gaussian uploads (form-data) ---
                if 'generator_type' in request.form:
                    gtype = request.form['generator_type'].lower()
                    rows  = int(request.form.get('rows', 100))
                    file_ = request.files.get('file')
                    if not file_:
                        return jsonify({"error": "No file was uploaded"}), 400

                    os.makedirs("tmp", exist_ok=True)
                    in_name  = f"{gtype}_{uuid.uuid4().hex}_input.csv"
                    in_path  = os.path.join("tmp", in_name)
                    file_.save(in_path)

                    out_name = f"{gtype}_{uuid.uuid4().hex}_augmented.csv"
                    out_path = os.path.join("tmp", out_name)

                    if gtype == 'ctgan':
                        self.data_gen_service.generate_data_ctgan(in_path, rows, out_path)
                    elif gtype == 'gaussian':
                        self.data_gen_service.generate_data_gaussian(in_path, rows, out_path)
                    else:
                        return jsonify({"error": f"Unknown generator_type: {gtype}"}), 400

                    if not os.path.exists(out_path):
                        return jsonify({"error": "CSV not created"}), 500

                    return send_file(out_path,
                                     mimetype="text/csv",
                                     as_attachment=True,
                                     download_name="synthetic_data.csv")

                # --- JSON-based generators (Merlin/Gold/Real) ---
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No JSON payload provided"}), 400

                gtype = data.get("generator_type", "").lower()
                theme = data.get("theme", "")
                rows  = data.get("rows", 100)
                if not gtype or not theme:
                    return jsonify({"error": "Missing 'generator_type' or 'theme'"}), 400

                os.makedirs("tmp", exist_ok=True)
                filename = f"{gtype}_{uuid.uuid4().hex}.csv"
                filepath = os.path.join("tmp", filename)

                if gtype == "merlin":
                    self.data_gen_service.generate_data_merlin(
                        theme=theme,
                        json_generation_service=self.json_gen_service,
                        rows=rows,
                        vary_names=True,
                        vary_countries=True,
                        output_file=filepath
                    )
                elif gtype == "gold":
                    self.data_gen_service.generate_data_gold(theme=theme,
                                                            rows=rows,
                                                            output_file=filepath)
                elif gtype == "real":
                    self.data_gen_service.generate_data_real(theme=theme,
                                                            rows=rows,
                                                            output_file=filepath)
                else:
                    return jsonify({"error": f"Unknown generator_type: {gtype}"}), 400

                if not os.path.exists(filepath):
                    return jsonify({"error": "CSV not created"}), 500

                return send_file(filepath,
                                 mimetype="text/csv",
                                 as_attachment=True,
                                 download_name="synthetic_data.csv")

            except Exception as e:
                self.logger.exception("Error in /generate endpoint")
                return jsonify({"error": str(e)}), 500

    def run(self, host="0.0.0.0", port=5000, debug=True):
        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    api = WebAPI()
    api.run()
