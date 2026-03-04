import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://lojasebocultural.com.br/categoria-produto/livros/jogos/"
# Escolha um nome de tópico único e difícil de adivinhar
NTFY_TOPIC = "jogo_no_sebo_cultural_jp" 
ARQUIVO_MEMORIA = "jogos_vistos.json"

def buscar_jogos():
    # Usamos um User-Agent para simular um navegador real e evitar bloqueios
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    resposta = requests.get(URL, headers=headers)
    resposta.raise_for_status()
    
    soup = BeautifulSoup(resposta.text, 'html.parser')
    
    # O WooCommerce geralmente usa essa classe para os títulos dos produtos
    titulos = soup.find_all('h2', class_='woocommerce-loop-product__title')
    return [titulo.get_text(strip=True) for titulo in titulos]

def main():
    jogos_atuais = buscar_jogos()
    
    # Carrega a memória de jogos já vistos
    if os.path.exists(ARQUIVO_MEMORIA):
        with open(ARQUIVO_MEMORIA, 'r', encoding='utf-8') as f:
            jogos_vistos = json.load(f)
    else:
        jogos_vistos = []

    # Encontra apenas os jogos que não estão na memória
    novos_jogos = [jogo for jogo in jogos_atuais if jogo not in jogos_vistos]

    if novos_jogos:
        for jogo in novos_jogos:
            # Envia a notificação Push para o celular
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                data=f"Novo item adicionado: {jogo}".encode('utf-8'),
                headers={"Title": "Sebo Cultural - Novo Jogo!"})
        
        # Atualiza a memória adicionando os novos jogos encontrados
        jogos_vistos.extend(novos_jogos)
        with open(ARQUIVO_MEMORIA, 'w', encoding='utf-8') as f:
            json.dump(jogos_vistos, f, ensure_ascii=False, indent=4)
            
        print(f"{len(novos_jogos)} novos jogos encontrados e notificados.")
    else:
        print("Nenhum jogo novo encontrado nesta rodada.")

if __name__ == "__main__":
    main()