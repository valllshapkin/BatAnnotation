
# Структура базы данных (Markdown)

Ниже представлено краткое описание схемы базы данных.

## 1. Справочники (Lookup Tables)
Таблицы, содержащие фиксированные списки значений. Легко расширяются без изменения кода. Английский язык и латынь используются как базовый стандарт.

| Таблица | PK (ID) | Ключевые поля | Описание |
| :--- | :--- | :--- | :--- |
| **`ref_species`** | `species_id` | `latin_name`, `genus`, `family` | Виды летучих мышей (строго латынь). |
| **`ref_detector_models`** | `detector_id` | `manufacturer`, `model`, `type` | Оборудование (Pettersson, AudioMoth и др.). |
| **`ref_habitat_types`** | `habitat_id` | `code`, `name` | Тип среды (forest, water, urban). |
| **`ref_context_types`** | `context_id` | `code`, `name` | Поведение (foraging, commuting, social). |
| **`ref_signal_shapes`** | `shape_id` | `code`, `name` | Формы сигналов (FM, CF, qCF). |

*Примечание: Все справочники имеют поле `is_active` (Boolean) для безопасного скрытия устаревших записей.*

## 2. Основные таблицы (Трёхуровневая иерархия)

Структура данных от физического аудиофайла до конкретного акустического импульса.

### Уровень 1: `recordings` (Файл / Сессия)
Описывает сам аудиофайл и физические условия записи.
*   **PK:** `recording_id`
*   **FK:** `detector_id` -> `ref_detector_models`, `habitat_id` -> `ref_habitat_types`
*   **Поля:** `filename`, `duration_s`, `sample_rate_hz`, координаты (`lat`/`lon`), `temperature_c`, `recorded_at`.

### Уровень 2: `call_sequences` (Контекст / Пролёт)
Описывает осмысленное событие (группу писков) внутри файла. Именно здесь определяется вид летучей мыши.
*   **PK:** `sequence_id`
*   **FK:** 
    *   `recording_id` -> `recordings` (Связь с файлом)
    *   `context_id` -> `ref_context_types` (Тип поведения)
    *   `species_id` -> `ref_species` (Видовая принадлежность)
*   **Поля:** Глобальные рамки (`t_start_ms`, `t_end_ms`, `f_min_khz`, `f_max_khz`), `notes` (заметки).

### Уровень 3: `bat_calls` (Отдельный импульс / Писк)
Описывает единичный акустический сигнал внутри секвенции.
*   **PK:** `call_id`
*   **FK:** 
    *   `sequence_id` -> `call_sequences` (Связь с родительским контекстом)
    *   `shape_id` -> `ref_signal_shapes` (Форма конкретного писка)
*   **Поля:** Рамки писка (`t_start_ms`, `t_end_ms`, `f_min_khz`, `f_max_khz`), пиковая частота (`fmaxe_khz`), время пиковой частоты (`t_fmaxe_ms`), кривые сигнала (`signal_curves` JSON), заметки (`notes`).
