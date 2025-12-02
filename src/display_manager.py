# src/display_manager.py
"""
Gerenciador de Display com Escala Virtual
Garante que o jogo rode em qualquer resolução (PC/Mobile) mantendo a proporção.
"""

import pygame

# Resolução de Design (A resolução em que você desenhou o jogo)
# 1280x720 (HD) é um ótimo padrão para PC e Mobile
VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720

class DisplayManager:
    def __init__(self):
        self.screen_real = None      # A janela real do sistema
        self.surface_virtual = None  # Onde o jogo desenha
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.current_w = VIRTUAL_WIDTH
        self.current_h = VIRTUAL_HEIGHT

    def init_screen(self, width=1280, height=720, fullscreen=False):
        """Inicializa a tela real e a superfície virtual."""
        flags = pygame.RESIZABLE
        if fullscreen:
            flags |= pygame.FULLSCREEN
            # Pega resolução nativa do monitor se for fullscreen
            try:
                display_info = pygame.display.Info()
                width, height = display_info.current_w, display_info.current_h
            except:
                pass # Mantém width/height passados se der erro

        self.screen_real = pygame.display.set_mode((width, height), flags)
        self.surface_virtual = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        
        self._calculate_scale(width, height)
        return self.surface_virtual  # Retorna a superfície virtual para o jogo desenhar nela

    def resize(self, w, h):
        """Chamado quando a janela é redimensionada."""
        self.screen_real = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self._calculate_scale(w, h)

    def toggle_fullscreen(self):
        """Alterna tela cheia mantendo proporção."""
        is_full = self.screen_real.get_flags() & pygame.FULLSCREEN
        if is_full:
            # Volta para janela padrão
            self.init_screen(1280, 720, fullscreen=False)
        else:
            # Vai para fullscreen
            self.init_screen(fullscreen=True)

    def _calculate_scale(self, real_w, real_h):
        """Calcula o fator de escala para manter Aspect Ratio (Letterbox)."""
        self.current_w = real_w
        self.current_h = real_h

        scale_w = real_w / VIRTUAL_WIDTH
        scale_h = real_h / VIRTUAL_HEIGHT
        
        # Escolhe o menor fator para caber tudo na tela sem cortar
        self.scale_factor = min(scale_w, scale_h)
        
        # Calcula offsets para centralizar (barras pretas)
        new_w = int(VIRTUAL_WIDTH * self.scale_factor)
        new_h = int(VIRTUAL_HEIGHT * self.scale_factor)
        
        self.offset_x = (real_w - new_w) // 2
        self.offset_y = (real_h - new_h) // 2

    def update(self):
        """Desenha a superfície virtual na tela real escalada."""
        # Limpa as bordas (letterbox) com preto
        self.screen_real.fill((0, 0, 0))
        
        # Escala a superfície virtual
        scaled_w = int(VIRTUAL_WIDTH * self.scale_factor)
        scaled_h = int(VIRTUAL_HEIGHT * self.scale_factor)
        
        # Só faz smoothscale se o tamanho mudou significativamente para economizar performance
        # Mas aqui faremos sempre para garantir qualidade visual
        scaled_surf = pygame.transform.smoothscale(
            self.surface_virtual, 
            (scaled_w, scaled_h)
        )
        
        # Desenha centralizado
        self.screen_real.blit(scaled_surf, (self.offset_x, self.offset_y))
        pygame.display.flip()

    def get_mouse_pos(self):
        """Converte clique da tela real para coordenadas virtuais do jogo."""
        mx, my = pygame.mouse.get_pos()
        
        # Remove offset
        mx -= self.offset_x
        my -= self.offset_y
        
        # Remove escala
        if self.scale_factor != 0:
            mx /= self.scale_factor
            my /= self.scale_factor
        
        return int(mx), int(my)

# Instância Global
display_manager = DisplayManager()
