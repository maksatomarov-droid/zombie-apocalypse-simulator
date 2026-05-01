def get_survival_rules(stats, beta, gamma, quarantine_effect):
    """
    Правила выживания из Зомбиленда на основе результатов симуляции.
    По сути — model explainability: объясняем что значит результат модели.
    """
    rules = []
    sr   = stats["survival_rate"]
    peak = stats["peak_day"]

    if beta > 0.4:
        rules.append({"number": 1,  "emoji": "🏃", "title": "Кардио",
            "reason": f"Скорость заражения {beta:.2f} — вирус молниеносный. "
                      f"Пик настал на {peak}-й день. Только быстрые выживают."})

    if sr < 30:
        rules.append({"number": 2,  "emoji": "🔫", "title": "Двойной выстрел",
            "reason": f"Выжило {sr}% — почти никого. Никогда не экономь "
                      "на безопасности. Добивай угрозу до конца."})

    if quarantine_effect < 0.3:
        rules.append({"number": 3,  "emoji": "🚗", "title": "Пристёгивай ремень",
            "reason": "Карантин почти не применялся. Базовая защита — "
                      "не роскошь, а необходимость."})

    if stats["peak_zombies"] > 500_000:
        rules.append({"number": 4,  "emoji": "🦸", "title": "Не будь героем",
            "reason": f"На пике было {stats['peak_zombies']:,} зомби. "
                      "Один против такой орды — это не смелость, это глупость."})

    if gamma < 0.05:
        rules.append({"number": 7,  "emoji": "🎒", "title": "Путешествуй налегке",
            "reason": "Зомби уничтожаются очень медленно. "
                      "Мобильность — твоё главное оружие. Брось лишний груз."})

    if quarantine_effect > 0.5 and sr < 40:
        rules.append({"number": 22, "emoji": "🚪", "title": "Знай свой выход",
            "reason": "Даже жёсткий карантин не спас ситуацию. "
                      "Всегда имей запасной план эвакуации."})

    if sr > 60:
        rules.append({"number": 17, "emoji": "🎨", "title": "Важно иметь хобби",
            "reason": f"Выжило {sr}%! Угроза под контролем. "
                      "Когда опасность позади — найди смысл и радость."})

    if sr > 40 and beta < 0.4:
        rules.append({"number": 32, "emoji": "✨", "title": "Наслаждайся мелочами",
            "reason": "Вирус распространялся медленно и человечество выстояло. "
                      "Самое время найти свой Твинки 🧁"})

    if not rules:
        rules.append({"number": 1, "emoji": "🏃", "title": "Кардио",
            "reason": "Всегда будь готов. Ты прошёл симуляцию — "
                      "значит ты уже думаешь как выживший."})
    return rules
