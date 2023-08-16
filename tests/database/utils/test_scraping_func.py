from app.utils.scraping_func import run_scrapping_trustpilot 
import os 
import pytest

# Définition du marqueur custom @integration
pytest.mark.integration = pytest.mark.marker

@pytest.mark.integration
def test_run_scrapping_trustpilot_integration(monkeypatch):
    tenant_id = 123
    website = "https://example.com"
    month = "2023-08"

    # Simuler l'environnement avec des variables vides
    monkeypatch.delenv("TENANT_WEBSITE", raising=False)
    monkeypatch.delenv("TENANT_ID", raising=False)
    monkeypatch.delenv("TENANT_MONTH", raising=False)

    # Appel à la fonction
    run_scrapping_trustpilot(tenant_id, website, month)

    # Vérification que les variables d'environnement ont été modifiées
    assert "TENANT_WEBSITE" in os.environ
    assert "TENANT_ID" in os.environ
    assert "TENANT_MONTH" in os.environ

    assert os.environ["TENANT_WEBSITE"] == website
    assert os.environ["TENANT_ID"] == str(tenant_id)
    assert os.environ["TENANT_MONTH"] == month
