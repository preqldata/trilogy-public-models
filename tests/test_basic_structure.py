





def test_import():
    from trilogy_public_models import models

    from trilogy_public_models.bigquery import stack_overflow

    assert models['stack_overflow'] == stack_overflow

