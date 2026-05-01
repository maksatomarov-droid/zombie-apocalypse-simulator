import numpy as np

def run_sir_model(population, infected_start, beta, gamma, days, quarantine_effect):
    """
    SIR-модель распространения эпидемии.
    Используется учёными для моделирования COVID-19, гриппа и других болезней.
    Мы применяем её к зомби-апокалипсису 🧟

    S — Susceptible   (люди, которые могут заразиться)
    I — Infected      (заражённые / зомби)
    R — Recovered     (выжившие с иммунитетом)

    beta  — скорость заражения
    gamma — скорость «выздоровления» (уничтожения зомби)
    quarantine_effect — насколько карантин снижает заражение (0–0.9)
    """
    effective_beta = beta * (1 - quarantine_effect)

    S = [population - infected_start]
    I = [infected_start]
    R = [0]

    for _ in range(days - 1):
        s, i, r = S[-1], I[-1], R[-1]
        n = s + i + r

        new_infected  = effective_beta * s * i / n
        new_recovered = gamma * i

        S.append(max(0, s - new_infected))
        I.append(max(0, i + new_infected - new_recovered))
        R.append(r + new_recovered)

    return np.array(S), np.array(I), np.array(R)


def get_summary_stats(S, I, R, population):
    peak_zombies  = int(max(I))
    peak_day      = int(np.argmax(I))
    survivors     = int(S[-1])
    survival_rate = round(survivors / population * 100, 1)
    total_zombified = population - survivors

    return {
        "peak_zombies":    peak_zombies,
        "peak_day":        peak_day,
        "survivors":       survivors,
        "survival_rate":   survival_rate,
        "total_zombified": total_zombified,
    }
