#--------------------------------------------------------------------
# INICIALIZAÇÃO DO JOGO - ADAPTADO PARA WEB (PYGBAG) & ESCALA
#--------------------------------------------------------------------
import asyncio  # 1. IMPORT OBRIGATÓRIO PARA WEB
import pygame
import sys
import os

# Adiciona o diretório base ao path (Boa prática)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- IMPORTS DO SEU JOGO ---
from src.core import main_menu
from src.audio_manager import audio_manager
from src.display_manager import display_manager  # <--- O NOVO GERENTE

# 2. A FUNÇÃO PRINCIPAL (ASYNC)
async def main():
    # Inicializa Pygame
    pygame.init()
    
    # Inicializa o Audio Manager (Se tiver o método init)
    try:
        audio_manager.init_mixer()
    except:
        pass

    # ------------------------------------------------------------------
    # 3. INICIALIZAÇÃO DA TELA (MUDANÇA CRÍTICA)
    # ------------------------------------------------------------------
    # Em vez de vários ifs (web/mobile/pc), deixamos o display_manager
    # criar a janela ideal e nos dar uma "tela virtual" de 1280x720.
    # ------------------------------------------------------------------
    
    # Detecta se é web para ajuste fino se necessário, mas o manager cuida do grosso
    if sys.platform == "emscripten":
        print("🌐 Modo Web (Pygbag) Detectado")
    
    # Esta função cria a janela real e retorna a superfície virtual (1280x720)
    # O jogo vai desenhar tudo nessa 'virtual_screen'
    # Se for mobile/web, o fullscreen=True (ou auto-detecção no manager) cuida do resto
    is_fullscreen = sys.platform == "emscripten" or sys.platform.startswith("android")
    virtual_screen = display_manager.init_screen(1280, 720, fullscreen=is_fullscreen)
    
    pygame.display.set_caption("Party Pascal - Mobile/PC Edition")

    # ------------------------------------------------------------------
    # 4. CHAMADA DO MENU
    # Passamos a 'virtual_screen' para o menu desenhar nela.
    # ------------------------------------------------------------------
    
    # O loop do jogo precisa ser async para web.
    # Se main_menu for uma função async, usamos await.
    try:
        await main_menu(virtual_screen)
    except TypeError:
        # Se main_menu não for async, chamamos normal (mas o ideal é ser async)
        print("Aviso: main_menu não é assíncrono. Pode travar na Web se não tiver asyncio.sleep(0).")
        main_menu(virtual_screen)

if __name__ == "__main__":
    # 5. EXECUÇÃO COM ASYNCIO
    asyncio.run(main())
