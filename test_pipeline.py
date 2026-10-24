import logging
from main import run_pipeline
import os

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def test():
    logger.info("=== ЗАПУСК ТЕСТОВОГО ПРОГОНА ===")
    output_dir = "output/test_run"
    
    queries = [
        "Здравствуйте, нужна пропарка 5 железнодорожных цистерн класса 3 в Норильске до конца месяца.",
        "Требуется разработка плана ликвидации разливов нефти для нашего склада ГСМ в Хабаровске.",
        "Помогите с подготовкой документации по промышленной безопасности для проверки Ростехнадзора в Якутске."
    ]
    
    success = 0
    for i, q in enumerate(queries, 1):
        logger.info(f"\n--- Тест {i} ---")
        try:
            result = run_pipeline(q, mock=True, output_dir=output_dir)
            if result["paths"]["response"] != "error":
                success += 1
        except Exception as e:
            logger.error(f"Тест {i} провален: {e}")
            
    logger.info(f"\n=== ИТОГ: Обработано заявок: {len(queries)}, успешно: {success} ===")

if __name__ == "__main__":
    test()
