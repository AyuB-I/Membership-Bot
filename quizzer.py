from typing import List


class Quiz:
    type: str = "quiz"

    def __init__(self, poll_id, question, options, correct_option_id, owner_id, poll_type, is_anonymous,
                 allows_multiple_answers, video_link, total_vote_counter):
        # Используем подсказки типов, чтобы было проще ориентироваться.
        self.poll_id: str = poll_id  # ID викторины. Изменится после отправки от имени бота
        self.question: str = question  # Текст вопроса
        self.options: List[str] = [*options]  # "Распакованное" содержимое массива m_options в массив options
        self.correct_option_id: int = correct_option_id  # ID правильного ответа
        self.owner: int = owner_id  # Владелец опроса
        self.poll_type: str = poll_type  # Тип опроса
        self.is_anonymous: bool = is_anonymous  # anonymous or no
        self.allows_multiple_answers: bool = allows_multiple_answers  # multiple answers
        self.winners: List[int] = []  # Список победителей
        self.chat_id: int = 0  # Чат, в котором опубликована викторина
        self.message_id: int = 0  # Сообщение с викториной (для закрытия)
        self.video_link: str = video_link
