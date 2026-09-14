"""Source and separate editorial presentation; never used for selection or prompts."""

from app.value_editorial import editorial_for

VERSION = "source-value-1"
EDITORIAL_VERSION = "editorial-value-2"
HORIZON = "Non établi pour ce cas. Évaluez l'intérêt après un premier résultat relu, puis plusieurs usages si nécessaire."
TRADEOFF = "Mettez en balance la préparation, la relecture et les corrections avec l'utilité du résultat. Un effort faible n'est pas une preuve de gain."
USEFUL_WHEN = "À essayer si cette tâche correspond à votre besoin, avec les éléments nécessaires et un outil autorisé. Comparez ensuite à votre pratique habituelle."
LIMIT = "Description et première action issues du catalogue, sans promesse de gain mesuré. Aucun délai de rentabilité établi."


def value_presentation(source: dict, case_id: str | None = None) -> dict:
    def field(name):
        value = source.get(name)
        return value if isinstance(value, str) and value.strip() else None

    result = {
        "version": VERSION,
        "status": "source_only",
        "description": field("description_cas_utilisation"),
        "first_action": field("premiere_action_48h"),
        "effort": field("effort"),
        "horizon": HORIZON,
        "tradeoff": TRADEOFF,
        "useful_when": USEFUL_WHEN,
        "limit": LIMIT,
    }
    editorial = editorial_for(case_id, source) if case_id else None
    if editorial:
        result.update(version=EDITORIAL_VERSION, status="editorial_hypothesis", editorial=editorial)
        for name in ("horizon", "useful_when", "tradeoff"):
            result[name] = editorial["claims"][name]["text"] or editorial["claims"][name]["unknown_reason"]
        result["limit"] = (
            "Hypothèses rédigées à partir des descriptions, actions et précautions publiées, "
            "à vérifier dans votre contexte. Gain mesuré et durée avant valeur non établis ; "
            "aucun délai de rentabilité annoncé."
        )
        result["measured_gain"] = None
        result["elapsed_horizon"] = None
    return result
