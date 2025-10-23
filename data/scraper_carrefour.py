# -- coding: utf-8 --
"""
Scraper Carrefour via JSON-LD (ld+json)
Modo: GitHub Actions + commit no repo
Armazenamento: 1 Excel por mês (coluna por dia)
"""

import os
import json
import time
from datetime import datetime
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By


# =========================
# 1) Paths e nomes mensais
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

today = datetime.now()
STAMP_DAY = today.strftime("%Y%m%d")       # -> coluna diária (Preço_YYYYMMDD)
STAMP_MONTH = today.strftime("%Y-%m")      # -> arquivo do mês (precos_carrefour_YYYY-MM.xlsx)

ARQ_MENSAL = os.path.join(DATA_DIR, f"precos_carrefour_{STAMP_MONTH}.xlsx")
ARQ_ERROS  = os.path.join(DATA_DIR, f"erros_carrefour_{STAMP_MONTH}.xlsx")
COLUNA_DIA = f"Preço_{STAMP_DAY}"


# =========================================
# 2) Driver (headless — ideal para Actions)
# =========================================
def build_driver(headless: bool = True):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.page_load_strategy = "eager"  # não espera tudo para acelerar
    # desliga imagens para ganhar velocidade
    opts.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2
    })
    # Selenium Manager resolve o driver compatível automaticamente
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(2)
    return driver


# =====================================
# 3) Scraper: lê JSON-LD do tipo Product
# =====================================
def scrape_product_via_json(url: str, driver: webdriver.Chrome) -> dict:
    print(f"\n🔗 {url}")
    driver.get(url)
    time.sleep(2)  # pequeno respiro para scripts carregarem

    try:
        tags = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
        for tag in tags:
            raw = tag.get_attribute("innerHTML")
            if not raw:
                continue

            try:
                data = json.loads(raw)
            except Exception:
                # ignora blocos inválidos
                continue

            objs = data if isinstance(data, list) else [data]
            for obj in objs:
                if isinstance(obj, dict) and obj.get("@type") == "Product":
                    name = obj.get("name", "Não encontrado")

                    # offers pode ser dict ou lista
                    offers = obj.get("offers", {})
                    price = None
                    if isinstance(offers, dict):
                        price = offers.get("price")
                    elif isinstance(offers, list) and offers:
                        price = offers[0].get("price")

                    try:
                        price_float = float(str(price).replace(",", "."))
                    except Exception:
                        price_float = 0.0

                    print("✅", name, "| R$", price_float)
                    return {"Nome do Produto": name, "Preço": price_float, "URL": url}

    except Exception as e:
        print("❌ Erro no parsing JSON-LD:", e)

    print("⚠️ Nada encontrado nessa URL.")
    return {"Nome do Produto": "Não encontrado", "Preço": 0.0, "URL": url}


# =========================
# 4) URLs (sua lista aqui)
# =========================
URLS = [
    'https://mercado.carrefour.com.br/arroz-branco-longofino-tipo-1-tio-joao-2kg-115657/p',
    'https://mercado.carrefour.com.br/feijao-carioca-tipo-1-kicaldo-1kg-466506/p',
    'https://mercado.carrefour.com.br/macarrao-de-semola-com-ovos-espaguete-8-adria-500g-4180372/p',
    'https://mercado.carrefour.com.br/farofa-de-mandioca-tradicional-yoki-400g-6582613/p',
    'https://mercado.carrefour.com.br/massa-para-pastel-discao-massa-leve-500g-841757/p',
    'https://mercado.carrefour.com.br/macarrao-instantaneo-nissin-sabor-galinha-caipira-85g-4814177/p',
    'https://mercado.carrefour.com.br/batata-monalisa-carrefour-aprox-600g-46922/p',
    'https://mercado.carrefour.com.br/pimentao-block-vermelho-trebeshi-150-g-5738458/p',
    'https://mercado.carrefour.com.br/tomate-carmem-carrefour-aprox-500g-262676/p',
    'https://mercado.carrefour.com.br/cebola-carrefour-aprox-500g-20621/p',
    'https://mercado.carrefour.com.br/cenoura-unico-1kg-5154669/p',
    'https://mercado.carrefour.com.br/acucar-refinado-uniao-1kg-197564/p',
    'https://mercado.carrefour.com.br/chocolate-ao-leite-com-amendoim-shot-165g-5790859/p',
    'https://mercado.carrefour.com.br/sorvete-napolitano-nestle-1-5-litros-8616043/p',
    'https://mercado.carrefour.com.br/achocolatado-em-po-nescau-550g-6409717/p',
    'https://mercado.carrefour.com.br/alface-lisa-carrefour-7745044/p',
    'https://mercado.carrefour.com.br/couve-flor-cledson-300-g-9560297/p',
    'https://mercado.carrefour.com.br/banana-nanica-fresca-organica-600g-210978/p',
    'https://mercado.carrefour.com.br/banana-prata-fischer-turma-da-monica-750g-9773711/p',
    'https://mercado.carrefour.com.br/limao-siciliano-carrefour-aprox-500g-63592/p',
    'https://mercado.carrefour.com.br/maca-gala-carrefour-aprox-600-g-10120/p',
    'https://mercado.carrefour.com.br/mamao-formosa-sabor-qualidade-aprox-16-kg-20524/p',
    'https://mercado.carrefour.com.br/manga-palmer-carrefour-aprox-600g-88919/p',
    'https://mercado.carrefour.com.br/melancia-premium-carrefour-aprox---8kg-194743/p',
    'https://mercado.carrefour.com.br/pera-willians-aprox-500g-39675/p',
    'https://mercado.carrefour.com.br/uva-escura-sem-semente-carrefour-500g-5141982/p',
    'https://mercado.carrefour.com.br/laranja-pera-carrefour-mercado-5-kg-6282032/p',
    'https://mercado.carrefour.com.br/bisteca-suina-congelada-sadia-1-kg-209864/p',
    'https://mercado.carrefour.com.br/contra-file-swift-mais-aprox-1-5kg-295906/p',
    'https://mercado.carrefour.com.br/coxao-mole-fracionado-a-vacuo-aprox--1-3-kg-18295/p',
    'https://mercado.carrefour.com.br/alcatra-bovina-carrefour-aproximadamente-400-g-21962/p',
    'https://mercado.carrefour.com.br/patinho-fracionado-a-vacuo-500g-18325/p',
    'https://mercado.carrefour.com.br/lagarto-swift-mais-aprox-15kg-295914/p',
    'https://mercado.carrefour.com.br/paleta-bovina-a-vacuo-500gnao-reativarcodigo-de-compra-20745/p',
    'https://mercado.carrefour.com.br/acem-em-pedacos-carrefour-aproximadamente-500-g-158828/p',
    'https://mercado.carrefour.com.br/costela-minga-bovina-cong-aprox-2kg-224006/p',
    'https://mercado.carrefour.com.br/camarao-descascado-cozido-36-40-celm-400-g-5939747/p',
    'https://mercado.carrefour.com.br/posta-cacao-congelado-buona-pesca-500-g-6311059/p',
    'https://mercado.carrefour.com.br/file-de-merluza-congelado-planalto-500-g-6323774/p',
    'https://mercado.carrefour.com.br/file-de-pescada-sem-espinha-swift-500-g-5457297/p',
    'https://mercado.carrefour.com.br/file-de-tilapia-fresco-carrefour-500-g-98930/p',
    'https://mercado.carrefour.com.br/presunto-cozido-sem-capa-fatiado-aurora-aproximadamente-200-g-49450/p',
    'https://mercado.carrefour.com.br/salsicha-hot-dog-resfriada-aurora-aproximadamente-500-g-49352/p',
    'https://mercado.carrefour.com.br/linguica-toscana-swift-700-g-5600812/p',
    'https://mercado.carrefour.com.br/mortadela-defumada-sadia-280g-5447045/p',
    'https://mercado.carrefour.com.br/queijo-minas-frescal-aurora-450-g-6264693/p',
    'https://mercado.carrefour.com.br/queijo-coalho-bom-leite-500-g-4305054/p',
    'https://mercado.carrefour.com.br/leite-uht-integral-piratininga-1-l-665017/p',
    'https://mercado.carrefour.com.br/iogurte-natural-tradicional-batavo-170g-5150439/p',
    'https://mercado.carrefour.com.br/manteiga-com-sal-aviacao-200-g-10010/p',
    'https://mercado.carrefour.com.br/creme-de-leite-ultrapasteurizado-itambe-200-g-5988921/p',
    'https://mercado.carrefour.com.br/requeijao-cremoso-aviacao-tradicional-220-g-10000/p',
    'https://mercado.carrefour.com.br/acucar-cristal-carrefour-1kg-5147300/p',
    'https://mercado.carrefour.com.br/mel-com-cacau-e-avela-400-g-4510146/p',
    'https://mercado.carrefour.com.br/geleia-de-goiaba-selecoes-c-pedacos-260-g-1280815/p',
    'https://mercado.carrefour.com.br/suco-de-uva-integral-maric-1-l-3538256/p',
    'https://mercado.carrefour.com.br/vinho-tinto-fino-seco-cabernet-sauvignon-pergola-750ml-1521709/p',
    'https://mercado.carrefour.com.br/whisky-red-label-johnnie-walker-1-litro-2719/p',
    'https://mercado.carrefour.com.br/refrigerante-coca-cola-sabor-cola-1-5-l-11087/p',
    'https://mercado.carrefour.com.br/cafe-torrado-e-moido-extraforte-melitta-500g-271203/p',
    'https://mercado.carrefour.com.br/farinha-de-trigo-dona-benta-tradicional-1kg-196416/p',
    'https://mercado.carrefour.com.br/azeite-extravirgem-portugues-oliveira-da-serra-500-ml-4526108/p',
    'https://mercado.carrefour.com.br/oleo-de-soja-soya-900ml-482616/p',
    'https://mercado.carrefour.com.br/margarina-qualy-com-sal-250g-4815618/p',
    'https://mercado.carrefour.com.br/arroz-branco-longofino-tipo-1-tio-joao-1kg-115658/p',
    'https://mercado.carrefour.com.br/feijao-preto-tipo-1-kicaldo-1kg-466510/p',
]


# =========================
# 5) Execução principal
# =========================
def main():
    driver = build_driver(headless=True)

    try:
        registros = []
        for url in URLS:
            registros.append(scrape_product_via_json(url, driver))
            time.sleep(1)
    finally:
        driver.quit()

    df_total = pd.DataFrame(registros)
    df_ok  = df_total[df_total["Preço"] > 0][["Nome do Produto", "Preço"]].copy()
    df_err = df_total[df_total["Preço"] <= 0].copy()

    # ---- Excel mensal: aba "Precos" com coluna diária ----
    if not df_ok.empty:
        if os.path.exists(ARQ_MENSAL):
            base = pd.read_excel(ARQ_MENSAL, sheet_name="Precos")
            if "Nome do Produto" not in base.columns:
                base["Nome do Produto"] = df_ok["Nome do Produto"]
            base = base.merge(df_ok, on="Nome do Produto", how="outer")
            if "Preço" in base.columns:
                base[COLUNA_DIA] = base.pop("Preço")
        else:
            base = df_ok.rename(columns={"Preço": COLUNA_DIA})

        with pd.ExcelWriter(ARQ_MENSAL, engine="openpyxl", mode="w") as w:
            base.to_excel(w, index=False, sheet_name="Precos")
        print(f"📁 Atualizado: {ARQ_MENSAL} (coluna {COLUNA_DIA})")
    else:
        print("⚠️ Nenhum preço válido hoje.")

    # ---- Log de erros do mês (opcional) ----
    if not df_err.empty:
        df_err["Data"] = today.strftime("%Y-%m-%d")
        if os.path.exists(ARQ_ERROS):
            be = pd.read_excel(ARQ_ERROS)
            be = pd.concat([be, df_err], ignore_index=True)
        else:
            be = df_err
        be.to_excel(ARQ_ERROS, index=False)
        print(f"⚠️ Erros/zeros salvos: {ARQ_ERROS}")
    else:
        print("✅ Sem erros hoje.")


if __name__ == "__main__":
    main()
