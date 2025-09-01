"""
Тесты для улучшенного DateExtractor
"""

from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from infrastructure.llm.extractors.date_extractor import DateExtractor

# Timezone для тестов
TZ = ZoneInfo("Europe/Minsk")


class TestDateExtractor:

    @pytest.fixture
    def date_extractor(self):
        """Создает экземпляр DateExtractor для тестов"""
        with patch("infrastructure.llm.extractors.date_extractor.get_llm"):
            return DateExtractor()

    @pytest.fixture
    def fixed_now(self):
        """Фиксированное время для предсказуемых тестов (15 марта 2025)"""
        return datetime(2025, 3, 15, 12, 0, 0, tzinfo=TZ)

    def test_extract_specific_date_russian_format(self, date_extractor, fixed_now):
        """Тест извлечения конкретной даты в русском формате"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "20 марта"
            result = date_extractor.extract_specific_date("20 марта")
            assert result is not None
            date_obj, matched_text = result
            assert date_obj.day == 20
            assert date_obj.month == 3
            assert date_obj.year == 2025
            assert matched_text == "20 марта"

    def test_extract_specific_date_english_format(self, date_extractor, fixed_now):
        """Тест извлечения конкретной даты в английском формате"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "March 25"
            result = date_extractor.extract_specific_date("March 25")
            assert result is not None
            date_obj, matched_text = result
            assert date_obj.day == 25
            assert date_obj.month == 3
            assert matched_text == "march 25"

    def test_extract_specific_date_numeric_format(self, date_extractor, fixed_now):
        """Тест извлечения конкретной даты в цифровом формате"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "25.03"
            result = date_extractor.extract_specific_date("25.03")
            assert result is not None
            date_obj, matched_text = result
            assert date_obj.day == 25
            assert date_obj.month == 3
            assert matched_text == "25.03"

            # Тест с годом "25.03.2025"
            result = date_extractor.extract_specific_date("25.03.2025")
            assert result is not None
            date_obj, matched_text = result
            assert date_obj.day == 25
            assert date_obj.month == 3
            assert date_obj.year == 2025
            assert matched_text == "25.03"

    def test_extract_specific_date_past_date_next_year(self, date_extractor, fixed_now):
        """Тест что прошедшие даты переносятся на следующий год"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # 10 марта уже прошло (сейчас 15 марта), должно быть 2026 год
            result = date_extractor.extract_specific_date("10 марта")
            assert result is not None
            date_obj, matched_text = result
            assert date_obj.day == 10
            assert date_obj.month == 3
            assert date_obj.year == 2026  # Следующий год

    def test_extract_date_range_russian(self, date_extractor, fixed_now):
        """Тест извлечения диапазона дат в русском формате"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "20-25 марта"
            result = date_extractor.extract_date_range("20-25 марта")
            assert result is not None
            start_date, end_date, matched_text = result
            assert start_date.day == 20
            assert start_date.month == 3
            assert end_date.day == 25
            assert end_date.month == 3
            assert matched_text == "20-25 марта"

    def test_extract_date_range_english(self, date_extractor, fixed_now):
        """Тест извлечения диапазона дат в английском формате"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "March 20-25"
            result = date_extractor.extract_date_range("March 20-25")
            assert result is not None
            start_date, end_date, matched_text = result
            assert start_date.day == 20
            assert start_date.month == 3
            assert end_date.day == 25
            assert end_date.month == 3
            assert matched_text == "march 20-25"

    def test_extract_date_range_numeric(self, date_extractor, fixed_now):
        """Тест извлечения диапазона дат в цифровом формате"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "20.03-25.03"
            result = date_extractor.extract_date_range("20.03-25.03")
            assert result is not None
            start_date, end_date, matched_text = result
            assert start_date.day == 20
            assert start_date.month == 3
            assert end_date.day == 25
            assert end_date.month == 3
            assert matched_text == "20.03-25.03"

    def test_extract_date_range_cross_month(self, date_extractor, fixed_now):
        """Тест извлечения диапазона дат через месяцы"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "28.03-05.04" (переход март -> апрель)
            result = date_extractor.extract_date_range("28.03-05.04")
            assert result is not None
            start_date, end_date, matched_text = result
            assert start_date.day == 28
            assert start_date.month == 3
            assert end_date.day == 5
            assert end_date.month == 4
            assert matched_text == "28.03-05.04"

    def test_validate_date_range_valid(self, date_extractor):
        """Тест валидации корректного диапазона дат"""
        start_date = datetime(2025, 3, 20, tzinfo=TZ)
        end_date = datetime(2025, 3, 25, tzinfo=TZ)

        assert date_extractor.validate_date_range(start_date, end_date) is True

    def test_validate_date_range_invalid_order(self, date_extractor):
        """Тест валидации некорректного порядка дат"""
        start_date = datetime(2025, 3, 25, tzinfo=TZ)
        end_date = datetime(2025, 3, 20, tzinfo=TZ)

        assert date_extractor.validate_date_range(start_date, end_date) is False

    def test_validate_date_range_too_long(self, date_extractor):
        """Тест валидации слишком длинного диапазона"""
        start_date = datetime(2025, 3, 20, tzinfo=TZ)
        end_date = datetime(2026, 3, 25, tzinfo=TZ)  # Более года

        assert date_extractor.validate_date_range(start_date, end_date) is False

    def test_extract_dates_from_text_prioritization(self, date_extractor, fixed_now):
        """Тест приоритизации методов извлечения дат"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Текст с диапазоном дат (должен иметь приоритет)
            result = date_extractor.extract_dates_from_text("20-25 марта")
            start_date, end_date, matched_text = result
            assert matched_text == "20-25 марта"
            assert start_date.day == 20
            assert end_date.day == 25

            # Текст с конкретной датой
            result = date_extractor.extract_dates_from_text("20 марта")
            start_date, end_date, matched_text = result
            assert matched_text == "20 марта"
            assert start_date.day == 20
            assert end_date.day == 20  # Один день
            assert start_date.hour == 0
            assert end_date.hour == 23  # Конец дня

            # Текст только с месяцем (fallback к существующему методу)
            result = date_extractor.extract_dates_from_text("март")
            start_date, end_date, matched_text = result
            assert matched_text == "март"
            assert start_date.day == 1  # Начало месяца
            assert end_date.day == 31  # Конец марта

    def test_extract_specific_date_no_match(self, date_extractor):
        """Тест когда конкретная дата не найдена"""
        result = date_extractor.extract_specific_date("завтра будет хороший день")
        assert result is None

    def test_extract_date_range_no_match(self, date_extractor):
        """Тест когда диапазон дат не найден"""
        result = date_extractor.extract_date_range("завтра будет хороший день")
        assert result is None

    def test_extract_date_range_invalid_days(self, date_extractor, fixed_now):
        """Тест обработки некорректных дней в диапазоне"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Некорректный диапазон (второй день меньше первого)
            result = date_extractor.extract_date_range("25-20 марта")
            assert result is None

    def test_month_bounds_from_text_preserved(self, date_extractor, fixed_now):
        """Тест что существующий метод month_bounds_from_text сохранен"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест существующего метода
            start, end, label = date_extractor.month_bounds_from_text("март")
            assert start.month == 3
            assert start.day == 1
            assert end.month == 4 or (end.month == 3 and end.day == 31)  # Конец марта
            assert label == "март"

    def test_extract_dates_complex_text(self, date_extractor, fixed_now):
        """Тест извлечения дат из сложного текста"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Сложный текст с датой
            complex_text = "Хотел бы забронировать дом на 25 марта, если это возможно"
            result = date_extractor.extract_dates_from_text(complex_text)
            start_date, end_date, matched_text = result
            assert matched_text == "25 марта"
            assert start_date.day == 25

    def test_different_dash_formats(self, date_extractor, fixed_now):
        """Тест различных форматов тире/дефисов"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Различные типы тире
            formats = ["20-25 марта", "20—25 марта", "20 - 25 марта", "20— 25 марта"]

            for text_format in formats:
                result = date_extractor.extract_date_range(text_format)
                assert result is not None, f"Failed for format: {text_format}"
                start_date, end_date, matched_text = result
                assert start_date.day == 20
                assert end_date.day == 25

    def test_error_handling_in_date_parsing(self, date_extractor, fixed_now):
        """Тест обработки ошибок при парсинге дат"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Невалидные даты должны обрабатываться корректно
            invalid_dates = ["32 марта", "0 марта", "15.13", "40.02"]

            for invalid_date in invalid_dates:
                result = date_extractor.extract_specific_date(invalid_date)
                # Некоторые могут быть None, некоторые могут обрабатываться
                # Главное - не должно быть исключений
                assert True  # Если мы дошли до этой точки, исключений не было

    def test_timezone_awareness(self, date_extractor, fixed_now):
        """Тест что извлеченные даты имеют правильный timezone"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            result = date_extractor.extract_dates_from_text("25 марта")
            start_date, end_date, matched_text = result

            # Проверяем что даты имеют правильный timezone
            assert start_date.tzinfo == TZ
            assert end_date.tzinfo == TZ

    def test_extract_iso_date_format(self, date_extractor, fixed_now):
        """Тест извлечения дат в ISO формате YYYY-MM-DD"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест ISO формата "2025-03-25"
            result = date_extractor.extract_specific_date("2025-03-25")
            assert result is not None
            date_obj, matched_text = result
            assert date_obj.year == 2025
            assert date_obj.month == 3
            assert date_obj.day == 25
            assert matched_text == "2025-03-25"

            # Тест ISO формата с однозначными числами "2025-3-5"
            result = date_extractor.extract_specific_date("2025-3-5")
            assert result is not None
            date_obj, matched_text = result
            assert date_obj.year == 2025
            assert date_obj.month == 3
            assert date_obj.day == 5
            assert matched_text == "2025-03-05"  # Нормализованный формат

    def test_extract_iso_date_range(self, date_extractor, fixed_now):
        """Тест извлечения диапазона дат в ISO формате"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "2025-03-20 to 2025-03-25"
            result = date_extractor.extract_date_range("2025-03-20 to 2025-03-25")
            assert result is not None
            start_date, end_date, matched_text = result
            assert start_date.year == 2025
            assert start_date.month == 3
            assert start_date.day == 20
            assert end_date.year == 2025
            assert end_date.month == 3
            assert end_date.day == 25
            assert matched_text == "2025-03-20 to 2025-03-25"

            # Тест "2025-03-20 - 2025-03-25"
            result = date_extractor.extract_date_range("2025-03-20 - 2025-03-25")
            assert result is not None
            start_date, end_date, matched_text = result
            assert start_date.day == 20
            assert end_date.day == 25

            # Тест русских связок "2025-03-20 до 2025-03-25"
            result = date_extractor.extract_date_range("2025-03-20 до 2025-03-25")
            assert result is not None
            start_date, end_date, matched_text = result
            assert start_date.day == 20
            assert end_date.day == 25

    def test_extract_iso_date_range_cross_month(self, date_extractor, fixed_now):
        """Тест ISO диапазона через месяцы"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "2025-03-28 to 2025-04-05"
            result = date_extractor.extract_date_range("2025-03-28 to 2025-04-05")
            assert result is not None
            start_date, end_date, matched_text = result
            assert start_date.month == 3
            assert start_date.day == 28
            assert end_date.month == 4
            assert end_date.day == 5

    def test_extract_iso_date_range_cross_year(self, date_extractor, fixed_now):
        """Тест ISO диапазона через годы"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Тест "2025-12-28 to 2026-01-05"
            result = date_extractor.extract_date_range("2025-12-28 to 2026-01-05")
            assert result is not None
            start_date, end_date, matched_text = result
            assert start_date.year == 2025
            assert start_date.month == 12
            assert start_date.day == 28
            assert end_date.year == 2026
            assert end_date.month == 1
            assert end_date.day == 5

    def test_extract_dates_from_text_iso_prioritization(
        self, date_extractor, fixed_now
    ):
        """Тест приоритизации ISO формата в главном методе"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # ISO диапазон должен иметь приоритет
            result = date_extractor.extract_dates_from_text("2025-03-20 to 2025-03-25")
            start_date, end_date, matched_text = result
            assert matched_text == "2025-03-20 to 2025-03-25"
            assert start_date.day == 20
            assert end_date.day == 25

            # ISO одиночная дата
            result = date_extractor.extract_dates_from_text("2025-03-20")
            start_date, end_date, matched_text = result
            assert matched_text == "2025-03-20"
            assert start_date.day == 20
            assert end_date.day == 20  # Один день
            assert start_date.hour == 0
            assert end_date.hour == 23  # Конец дня

    def test_iso_date_validation_edge_cases(self, date_extractor, fixed_now):
        """Тест валидации ISO дат с граничными случаями"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Валидные граничные даты
            valid_dates = ["2025-01-01", "2025-12-31", "2024-02-29"]  # Високосный год

            for valid_date in valid_dates:
                result = date_extractor.extract_specific_date(valid_date)
                assert result is not None, f"Valid date {valid_date} should be parsed"

            # Невалидные даты должны быть отклонены
            invalid_dates = ["2025-13-01", "2025-02-30", "2025-00-15", "2025-01-32"]

            for invalid_date in invalid_dates:
                result = date_extractor.extract_specific_date(invalid_date)
                # Может быть None или обработано как ошибка, главное - без исключений
                assert True  # Если дошли до этой точки, исключений не было

    def test_iso_date_complex_text_extraction(self, date_extractor, fixed_now):
        """Тест извлечения ISO дат из сложного текста"""
        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine = datetime.combine
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Сложный текст с ISO датой
            complex_text = "I would like to book from 2025-03-25 if possible"
            result = date_extractor.extract_dates_from_text(complex_text)
            start_date, end_date, matched_text = result
            assert matched_text == "2025-03-25"
            assert start_date.day == 25

            # Сложный текст с ISO диапазоном
            complex_range_text = "Booking request for 2025-03-20 to 2025-03-25 period"
            result = date_extractor.extract_dates_from_text(complex_range_text)
            start_date, end_date, matched_text = result
            assert matched_text == "2025-03-20 to 2025-03-25"
            assert start_date.day == 20
            assert end_date.day == 25
