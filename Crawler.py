import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time


specialite = input("💉 Entrez la spécialité ou type de médecin recherché (ex: généraliste, dentiste, ophtalmo) : ") or ""
rue = input("entrez la rue et l'adresse (ex: 12 avenue Victor Hugo) : ") or ""
cp = input("entrez le code postal (ex: 75001) : ") or ""
ville = input("entrez la ville (ex: Paris) : ") or ""
adresse_complete = rue + " " + cp + " " + ville
preference = input("Souhaitez-vous uniquement les consultations en visio, en présentiel, ou les deux ? (visio/presentiel/tout) : ").lower().strip() or "tout"
assurance_pref = input("Souhaitez-vous un médecin conventionné d’un type précis ? (ex: secteur 1, secteur 2, non, tous) : ").lower().strip() or "tous"

#specialite = "medecin"
#adresse_complete = "75000"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.doctolib.fr")
driver.set_window_size(1256, 1256)

# Refuser les cookies
time.sleep(2)
driver.find_element(By.ID, "didomi-notice-disagree-button").click()

#recherche spécialité
time.sleep(4)
if specialite != "":
    specialite_input = driver.find_element(By.CSS_SELECTOR, "input.searchbar-input.searchbar-query-input")
    specialite_input.clear()
    specialite_input.send_keys(specialite)
    time.sleep(2)
    specialite_input.send_keys(Keys.ENTER)

# recherche postion
time.sleep(1)
place_input = driver.find_element(By.CSS_SELECTOR, "input.searchbar-input.searchbar-place-input")
place_input.clear()
place_input.send_keys(adresse_complete)

time.sleep(2)
suggestions = driver.find_elements(By.CSS_SELECTOR, "ul[role='listbox'] li button.searchbar-result")
if len(suggestions) >= 2:
    suggestions[1].click()
else:
    place_input.send_keys(Keys.ENTER)

#temps de pause
time.sleep(1)

# click bouton recherche
search_btn = driver.find_element(By.CSS_SELECTOR, "button.searchbar-submit-button")
search_btn.click()
if specialite == "":
    print("part a")
    time.sleep(50)
    search_btn = driver.find_element(By.CSS_SELECTOR, "button.searchbar-submit-button")
    search_btn.click()
    print("part c")


time.sleep(5)
medecins = []
base_url = driver.current_url.split("&page=")[0]
page = 1
max_pages = 4
print('its fetching time')
# cauchemardesque
while page <= max_pages:
    current_url = base_url + f"&page={page}"
    driver.get(current_url)
    time.sleep(2)
    cards = driver.find_elements(By.CSS_SELECTOR, "div.dl-card[data-design-system-component='Card']")
    print("selector card found")

    for card in cards:
        try:
            # Récup nom
            nom_elem = card.find_element(By.CSS_SELECTOR, "h2")
            nom = nom_elem.text.strip()

            # Récup spécialité
            spe = None
            for div in card.find_elements(By.CSS_SELECTOR, "div.flex"):
                if div.get_attribute("class").strip() == "flex":
                    spe = div.text.strip()
                    break
            #recup adress
            adresse = "Adresse non trouvée"
            try:
                bloc_adresse = card.find_element(By.CSS_SELECTOR, "div.flex.gap-8 div.flex.flex-wrap.gap-x-4")
                lignes = bloc_adresse.find_elements(By.TAG_NAME, "p")
                adresse = ", ".join(p.text.strip() for p in lignes if p.text.strip())
            except:
                pass

            # Récup conventionnement
            convention = "Conventionnement non trouvé"
            blocs = card.find_elements(By.CSS_SELECTOR, "div.flex.gap-8")
            for bloc in blocs:
                try:
                    icone = bloc.find_element(By.CSS_SELECTOR, "svg")
                    aria_label = icone.get_attribute("aria-label").lower().strip()

                    if aria_label == "assurance":
                        paragraphe = bloc.find_element(By.TAG_NAME, "p")
                        convention = paragraphe.text.strip()
                        break
                except:
                    continue

            # partie visio
            visio = "Visio non disponible"
            try:
                video_icon = card.find_element(By.CSS_SELECTOR, "svg[aria-label='Consultation vidéo disponible']")
                visio = "Visio disponible"
            except:
                visio = "Visio non disponible"

            # filtre assurance
            if assurance_pref != "tous" and assurance_pref not in convention.lower():
                continue
            # filtre visio
            if (preference == "visio" and visio != "Visio disponible") or \
                    (preference == "presentiel" and visio == "Visio disponible"):
                continue

            if nom and spe:
                medecins.append([nom, spe, adresse, convention,visio])
            else:
                print("info incomplète pour une card")

        except Exception as e:
            continue
    page += 1


print("fetching complete")
time.sleep(5)
driver.quit()

# save
with open("medecins.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Nom du médecin", "Spécialité", "Adresse", "Conventionnement", "Visio"])
    for ligne in medecins:
        writer.writerow(ligne)


print("CSV généré avec", len(medecins), "médecins.")

driver.quit()
