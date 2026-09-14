"""Source-only presentation. Never used for retrieval, ranking or prompt construction."""

VERSION = "source-value-1"
HORIZON = "Non établi pour ce cas. Évaluez l'intérêt après un premier résultat relu, puis plusieurs usages si nécessaire."
TRADEOFF = "Mettez en balance la préparation, la relecture et les corrections avec l'utilité du résultat. Un effort faible n'est pas une preuve de gain."
USEFUL_WHEN = "À essayer si cette tâche correspond à votre besoin, avec les éléments nécessaires et un outil autorisé. Comparez ensuite à votre pratique habituelle."
LIMIT = "Description et première action issues du catalogue, sans promesse de gain mesuré. Aucun délai de rentabilité établi."


def value_presentation(source: dict) -> dict:
    def field(name):
        value = source.get(name)
        return value if isinstance(value, str) and value.strip() else None

    return {
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
