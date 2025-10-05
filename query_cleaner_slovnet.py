#created: 2025/10/05 23:48:52
#last-modified: 2025/10/06 00:08:20
#by kaldor31


import re
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, Doc

# Инициализация компонентов Natasha
# Эти объекты грузятся один раз при запуске, чтобы не тратить время на каждом запросе.
segmenter = Segmenter()
emb = NewsEmbedding()
morph_vocab = MorphVocab()
morph_tagger = NewsMorphTagger(emb)

# Часто встречающиеся вводные / нерелевантные слова (в леммах)
FILLER_LEMMAS = {
    "слушать", "подсказывать", "сказывать", "рассказывать",
    "интересно", "ну", "вот", "ладно", "короче", "значить",
    "мочь", "можешь", "если", "а", "пожалуйста", "объяснить",
    "расскажи", "объясни", "сказать", "подскажи", "скажи"
}


def clean_query(text: str) -> str:
    """
    Умно очищает запрос от обращений и вводных слов,
    используя морфологический анализ Natasha + Slovnet.
    """
    if not text:
        return ""

    text = text.strip()

    # Создаём документ
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)

    tokens = []
    skip = True

    for token in doc.tokens:
        lemma = (token.lemma or token.text).lower()
        # Морфологическая нормализация
        token.lemmatize(morph_vocab)

        # Если слово находится в списке вводных — пропускаем
        if skip and lemma in FILLER_LEMMAS:
            continue
        # После того как встретили смысловое слово, прекращаем пропуск
        skip = False
        tokens.append(token.text)

    cleaned = " ".join(tokens).strip()

    # Финальная косметическая чистка
    cleaned = re.sub(r"^[,.\s]+", "", cleaned)
    cleaned = re.sub(r"[?!.]+$", "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    # Если очистка удалила всё, возвращаем исходный текст
    return cleaned or text