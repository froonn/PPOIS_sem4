import random
from models.model import DatabaseModel
from utils.constants import ACADEMIC_RANKS, ACADEMIC_DEGREES, FACULTIES, DEFAULT_DB_NAME

# Пример генератора случайных имен и кафедр
FIRST_NAMES = ['Иван', 'Петр', 'Алексей', 'Николай', 'Сергей', 'Екатерина', 'Анна', 'Мария', 'Наталья', 'Ольга']
LAST_NAMES = ['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Смирнов', 'Васильева', 'Козлова', 'Новикова', 'Соловьев', 'Жуков']
DEPARTMENTS = ['Кафедра математики', 'Кафедра физики', 'Кафедра информатики', 'Кафедра электроники', 'Кафедра языков']

def random_full_name():
    return f"{random.choice(LAST_NAMES)} {random.choice(FIRST_NAMES)}"

def random_record():
    return {
        'faculty': random.choice(FACULTIES),
        'department': random.choice(DEPARTMENTS),
        'full_name': random_full_name(),
        'academic_rank': random.choice(ACADEMIC_RANKS),
        'academic_degree': random.choice(ACADEMIC_DEGREES),
        'experience': random.randint(0, 40)
    }

if __name__ == "__main__":
    db = DatabaseModel(DEFAULT_DB_NAME)
    records = [random_record() for _ in range(50)]
    if db.add_records_batch(records):
        print("50 случайных записей успешно добавлены в базу данных!")
    else:
        print("Ошибка при записи в базу данных.")
    db.close()