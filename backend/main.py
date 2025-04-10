import os
from utils.logger_config import setup_logger
from services.openai_service import OpenAIService
from services.translator_service import TranslatorService
from services.json_generation_service import JSONGenerationService
from services.data_generation_service import DataGenerationService


def main():
    # 1. Setup logger
    logger = setup_logger("my_logger", "app.log")
    logger.info("Application started.")

    # 2. Initialize services
    openai_service = OpenAIService(logger, model_name="gpt-4o-mini")
    translator_service = TranslatorService(logger)
    json_gen_service = JSONGenerationService(openai_service, logger)
    data_gen_service = DataGenerationService(translator_service, openai_service, logger)

    # 3. Make sure the output directory exists
    os.makedirs("generations", exist_ok=True)

    # 4. Example calls
    logger.info("Generating data with MERLIN approach (patients).")
    data_gen_service.generate_data_merlin(
        theme="Hospital patients with id, name, age, disease",
        json_generation_service=json_gen_service,
        rows=1000,
        vary_names=True,
        vary_countries=True,
        output_file="generations/merlin_data.csv"
    )

    logger.info("Generating data with GOLD approach (basketball players).")
    data_gen_service.generate_data_gold(
        theme="NBA basketball players with name, height, weight, team, and this season's scoring stats",
        rows=8,
        output_file="generations/gold_data.csv"
    )

    # 5. (If needed) Data generation using YDATA approach (not implemented)
    # data_gen_service.generate_data_ydata(theme="Some theme", rows=20)

    logger.info("Application finished.")


if __name__ == "__main__":
    main()
