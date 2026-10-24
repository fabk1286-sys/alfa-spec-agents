import argparse
import sys
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

from agents.classifier import classify_request
from agents.responder import generate_response
from agents.documenter import generate_document
from agents.publisher import save_results

def safe_call(func, *args, fallback=None, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Ошибка в агенте {func.__module__}: {e}")
        return fallback

def run_pipeline(text: str, mock: bool = True, output_dir: str = "output") -> dict:
    logger.info("=== ЗАПУСК ПАЙПЛАЙНА ===")
    
    classification = safe_call(
        classify_request, text, mock=mock, 
        fallback={"service_type": "other", "urgency": "low", "region": "не указан", "raw_text": text}
    )
    
    response = safe_call(
        generate_response, classification, mock=mock, 
        fallback="Извините, произошла ошибка при генерации ответа. Менеджер свяжется с вами."
    )
    
    document = safe_call(
        generate_document, classification, mock=mock, 
        fallback="# Коммерческое предложение\nОшибка генерации."
    )
    
    paths = safe_call(
        save_results, response, document, classification, output_dir=output_dir, 
        fallback={"response": "error", "document": "error"}
    )
    
    logger.info(f"=== ПАЙПЛАЙН ЗАВЕРШЕН. Результаты в {output_dir} ===")
    return {
        "classification": classification,
        "response": response,
        "document": document,
        "paths": paths
    }

def main():
    parser = argparse.ArgumentParser(description="Мультиагентная система обработки заявок")
    parser.add_argument("query", nargs="?", help="Текст заявки")
    parser.add_argument("--file", help="Путь к файлу с заявкой")
    parser.add_argument("--real", action="store_true", help="Использовать реальный Claude API")
    parser.add_argument("--demo", action="store_true", help="Прогнать 3 тестовые заявки")
    
    args = parser.parse_args()
    
    if args.demo:
        if args.real:
            logger.warning("Режим --demo всегда работает в mock. Флаг --real игнорируется.")
        mock_mode = True
        
        examples_file = "examples/sample_requests.md"
        if not os.path.exists(examples_file):
            logger.error(f"Файл с примерами не найден: {examples_file}")
            sys.exit(1)
            
        with open(examples_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        lines = [line.strip() for line in content.split('\n') if line.strip() and line.strip()[0].isdigit()]
        queries = [line.split('.', 1)[1].strip() for line in lines if '.' in line]
        
        logger.info(f"Найдено {len(queries)} заявок в {examples_file}")
        for i, q in enumerate(queries, 1):
            logger.info(f"\n--- ЗАЯВКА {i} ---\n{q}")
            run_pipeline(q, mock=mock_mode)
        return

    text = None
    if args.file:
        if args.query:
            logger.warning("Игнорирую текстовый аргумент, использую файл.")
        if not os.path.exists(args.file):
            logger.error(f"Файл не найден: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    elif args.query:
        text = args.query
    else:
        logger.error("Укажите текст заявки или используйте --file / --demo.")
        sys.exit(1)

    mock_mode = True
    if args.real:
        from dotenv import load_dotenv
        load_dotenv()
        if not os.getenv("ANTHROPIC_API_KEY"):
            logger.error("Для реального режима укажите ANTHROPIC_API_KEY в .env файле.")
            sys.exit(1)
        mock_mode = False

    run_pipeline(text, mock=mock_mode)

if __name__ == "__main__":
    main()
