async def divine_intent(spec):
    """Derive agent intent from specification."""
    return {
        'name': spec.name,
        'purpose': spec.purpose,
    }
