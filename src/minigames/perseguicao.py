# ===========================================================
#           MINIGAME PERSEGUIÇÃO (WEB OPTIMIZED)
# ===========================================================

import pygame
import random
import sys
import time
import os
import math
import asyncio

from src.utils import show_pause_screen, draw_text_wrapped, draw_score_display, load_font
from src.score_manager import ScoreManager
# Correção do Import
from src.audio_manager import audio_manager 
import src.difficulty_manager as dm

# ===========================================================
#            BANCO DE INCIDENTES (MANTIDO)
# ===========================================================
ALL_INCIDENTS = {
    "facil": [
        {"descricao": "Um e-mail suspeito foi aberto por um funcionário.", "opcoes": ["Acionar resposta a incidentes", "Ignorar o ocorrido"], "correta": "Acionar resposta a incidentes"},
        {"descricao": "Um servidor apresentou falhas repetidas.", "opcoes": ["Analisar causa raiz", "Reiniciar e ignorar"], "correta": "Analisar causa raiz"},
        {"descricao": "Senha compartilhada no chat da empresa.", "opcoes": ["Redefinir senha agora", "Deixar pra lá"], "correta": "Redefinir senha agora"},
        {"descricao": "Visitante estranho tirando fotos do servidor.", "opcoes": ["Chamar segurança", "Perguntar o nome"], "correta": "Chamar segurança"},
        {"descricao": "Antivírus detectou um arquivo malicioso.", "opcoes": ["Quarentena Imediata", "Abrir para ver"], "correta": "Quarentena Imediata"},
        {"descricao": "Notebook corporativo foi perdido.", "opcoes": ["Bloquear acesso remoto", "Esperar ele aparecer"], "correta": "Bloquear acesso remoto"}
    ],
    "normal": [
        {"descricao": "Tentativa de acesso não autorizado no financeiro.", "opcoes": ["Bloquear IP e notificar", "Monitorar em silêncio"], "correta": "Bloquear IP e notificar"},
        {"descricao": "Backup diário falhou por falta de espaço.", "opcoes": ["Liberar espaço e refazer", "Ignorar por hoje"], "correta": "Liberar espaço e refazer"},
        {"descricao": "Funcionário instalou software pirata.", "opcoes": ["Remover e advertir", "Deixar se funcionar"], "correta": "Remover e advertir"},
        {"descricao": "Firewall está bloqueando tráfego legítimo.", "opcoes": ["Ajustar regras", "Desativar firewall"], "correta": "Ajustar regras"},
        {"descricao": "Vazamento de dados de clientes detectado.", "opcoes": ["Acionar plano de crise", "Esconder o fato"], "correta": "Acionar plano de crise"},
        {"descricao": "Usuário com privilégio de admin sem necessidade.", "opcoes": ["Revogar privilégio", "Manter por facilidade"], "correta": "Revogar privilégio"}
    ],
    "dificil": [
        {"descricao": "Ransomware criptografou o servidor de arquivos.", "opcoes": ["Isolar rede e restaurar", "Pagar o resgate"], "correta": "Isolar rede e restaurar"},
        {"descricao": "Ataque DDoS massivo em andamento.", "opcoes": ["Ativar mitigação DDoS", "Desligar o servidor"], "correta": "Ativar mitigação DDoS"},
        {"descricao": "Zero-day exploit divulgado para seu sistema.", "opcoes": ["Aplicar patch/workaround", "Esperar o vendor"], "correta": "Aplicar patch/workaround"},
        {"descricao": "Insider copiando banco de dados para USB.", "opcoes": ["Bloquear porta e conta", "Pedir explicação"], "correta": "Bloquear porta e conta"},
        {"descricao": "Certificado SSL do site expirou.", "opcoes": ["Renovar imediatamente", "Esperar reclamação"], "correta": "Renovar imediatamente"},
        {"descricao": "Logs de auditoria foram apagados.", "opcoes": ["Investigar intrusão", "Restaurar logs"], "correta": "Investigar intrusão"}
    ]
}

# ===========================================================
#            CLASSE: Estrada (Otimizada)
# ===========================================================
class RoadLine:
    __slots__ = ('w', 'h', 'x', 'y', 'length', 'speed', 'width', 'color')
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.x = random.randint(0, screen_w)
        self.y = random.randint(-screen_h, 0)
        self.length = random.randint(20, 60)
        self.speed = random.uniform(10, 25)
        self.width = random.randint(2, 4)
        self.color = (40, 40, 60)

    def update(self):
        self.y += self.speed
        if self.y > self.h:
            self.y = -self.length
            self.x = random.randint(0, self.w)

    def draw(self, surface, offset_x, offset_y):
        # Desenha direto na tela com offset
        start = (self.x + offset_x, self.y + offset_y)
        end = (self.x + offset_x, self.y + self.length + offset_y)
        pygame.draw.line(surface, self.color, start, end, self.width)


# ===========================================================
#             FUNÇÃO PRINCIPAL (ASYNC)
# ===========================================================
async def run_perseguicao(screen):
    pygame.display.set_caption("🚨 Perseguição — Decisões Rápidas 🚨")
    clock = pygame.time.Clock()

    layout = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_dir = os.path.join(base_dir, "assets")
    
    bg_path = os.path.join(assets_dir, "background", "background_perseguicao.png")
    police_path = os.path.join(assets_dir, "icons", "police_car.png")
    hacker_path = os.path.join(assets_dir, "icons", "hacker.png")
    lock_path = os.path.join(assets_dir, "icons", "cadeado.png") 
    
    # Loads
    bg_original = pygame.image.load(bg_path).convert() if os.path.exists(bg_path) else None
    img_hacker = pygame.image.load(hacker_path).convert_alpha() if os.path.exists(hacker_path) else None
    img_lock = pygame.image.load(lock_path).convert_alpha() if os.path.exists(lock_path) else None

    # === CACHE DE ASSETS ===
    sirene_top = None
    sirene_bottom = None

    def resize_assets(surface):
        nonlocal sirene_top, sirene_bottom
        w, h = surface.get_size()
        
        if bg_original:
            layout['background'] = pygame.transform.scale(bg_original, (w, h))
        else:
            layout['background'] = pygame.Surface((w, h))
            layout['background'].fill((10, 10, 15)) 

        # Fontes
        layout['font_title'] = load_font(max(48, int(h * 0.07)))
        layout['font_text'] = load_font(max(40, int(h * 0.06)))
        layout['font_small'] = load_font(max(28, int(h * 0.045)))
        layout['font_timer'] = load_font(max(24, int(h * 0.035)))

        icon_size = int(h * 0.06)
        if img_hacker:
            layout['icon_hacker'] = pygame.transform.smoothscale(img_hacker, (int(icon_size*1.2), int(icon_size*1.2)))
        else:
            s = pygame.Surface((icon_size, icon_size)); s.fill((255, 50, 50))
            layout['icon_hacker'] = s

        if img_lock:
            ts = int(h * 0.085) 
            layout['icon_title'] = pygame.transform.smoothscale(img_lock, (ts, ts))
        else:
            layout['icon_title'] = None
            
        # Título Cache
        title_text = "ALERTA DE SEGURANÇA"
        layout['title_surf'] = layout['font_title'].render(title_text, True, (255, 215, 0))
        layout['title_shadow'] = layout['font_title'].render(title_text, True, (0, 0, 0))
        
        # Vignette Cache (Cria uma vez, muda alpha no loop)
        sirene_top = pygame.Surface((w, 30))
        sirene_bottom = pygame.Surface((w, 30))

    resize_assets(screen)

    road_lines = [RoadLine(screen.get_width(), screen.get_height()) for _ in range(25)]
    shake_amount = 0

    # Lógica
    diff_rules = dm.get_rules()
    q_type = dm.get_question_set_type()
    tempo_base = diff_rules.get("perseguicao_tempo", 5)
    
    incidentes = ALL_INCIDENTS.get(q_type, ALL_INCIDENTS["normal"])
    random.shuffle(incidentes)
    
    pontos_acerto = 10 + diff_rules["bonus_acerto"]
    pontos_erro = -diff_rules["perda_pontos"]

    indice = 0
    feedback = None
    start_time = time.time()
    frame = 0
    pontos_desta_fase = 0
    
    transitioning = False
    transition_start_time = 0
    
    # === ESTADO CACHEADO DA UI ===
    current_incident_surf = None
    current_buttons = [] # Lista de (rect, texto_original, surface_texto)
    
    def cache_incident_ui(idx):
        nonlocal current_incident_surf, current_buttons
        if idx >= len(incidentes): return
        
        inc = incidentes[idx]
        w, h = screen.get_size()
        
        # 1. Container de Texto (Surface Fixa)
        container_w = w - 200
        text_margin = 30
        
        # Calcula altura necessária (simples estimativa ou wrap real)
        # Para otimizar, fixamos uma altura segura ou usamos o draw_text_wrapped em uma surface temp
        temp_h = int(h * 0.3)
        s = pygame.Surface((container_w, temp_h), pygame.SRCALPHA)
        
        # Fundo do container
        pygame.draw.rect(s, (0, 20, 10, 200), s.get_rect(), border_radius=8)
        pygame.draw.rect(s, (0, 255, 0), s.get_rect(), 2, border_radius=8)
        
        # Texto Aviso
        warn = layout['font_small'].render("> INCIDENTE DETECTADO <", True, (255, 0, 0))
        s.blit(warn, warn.get_rect(midtop=(container_w//2, 10)))
        
        # Texto Descrição
        text_rect = pygame.Rect(text_margin, 60, container_w - text_margin*2, temp_h - 70)
        draw_text_wrapped(s, inc["descricao"], layout['font_text'], (200, 255, 200), text_rect)
        
        current_incident_surf = s
        
        # 2. Prepara Botões (Embaralha e cacheia texto)
        if 'shuffled_opcoes' not in inc:
            opts = inc["opcoes"][:]
            random.shuffle(opts)
            # Tenta garantir que a correta não fique sempre no mesmo lugar (simples)
            inc['shuffled_opcoes'] = opts
            
        current_buttons = []
        largura_botao = int(w * 0.40)
        altura_botao = int(h * 0.16)
        espaco = 60
        total_largura = (2 * largura_botao) + espaco
        start_x = (w - total_largura) // 2
        y_base = int(h * 0.22) + int(math.sin(0) * 5) + temp_h + int(h * 0.05) # Aproximado
        
        for i, txt in enumerate(inc['shuffled_opcoes']):
            # Cache do texto do botão
            txt_surf = layout['font_small'].render(txt, True, (255, 255, 255))
            # Ajusta tamanho se muito grande
            if txt_surf.get_width() > largura_botao - 20:
                sc = (largura_botao - 20) / txt_surf.get_width()
                txt_surf = pygame.transform.smoothscale(txt_surf, (int(txt_surf.get_width()*sc), int(txt_surf.get_height()*sc)))
            
            # Rect base (será atualizado na animação)
            r = pygame.Rect(start_x + i * (largura_botao + espaco), y_base, largura_botao, altura_botao)
            current_buttons.append({"rect": r, "text": txt, "surf": txt_surf})

    # Cache inicial
    if indice < len(incidentes):
        cache_incident_ui(0)

    # Loop Principal
    while True:
        # WEB PERFORMANCE: Fixar DT para física não explodir
        dt = clock.tick(60) / 1000.0
        frame += 1
        w, h = screen.get_size()

        # Check Fim
        if indice >= len(incidentes) and not transitioning:
            audio_manager.play_sfx_if_exists("roleta")
            await show_pause_screen(screen, clock, "Relatório", f"Pontuação: {ScoreManager.get_score()}", theme="Perseguição")
            return ScoreManager.get_score()

        # Transição
        if transitioning:
            if time.time() - transition_start_time > 0.6: # 0.6s transição
                transitioning = False
                feedback = None
                indice += 1
                if indice < len(incidentes):
                    cache_incident_ui(indice)
                start_time = time.time()
        
        # Shake
        if shake_amount > 0:
            shake_amount -= 0.5
            if shake_amount < 0: shake_amount = 0
        shake_x = random.randint(-int(shake_amount), int(shake_amount))
        shake_y = random.randint(-int(shake_amount), int(shake_amount))
        
        # 1. Background
        screen.blit(layout['background'], (0, 0))
        
        # 2. Road Lines (Direto na tela)
        for line in road_lines:
            line.update()
            line.draw(screen, shake_x, shake_y)

        # 3. Sirene (Vignette) - Ajuste de cor sem criar surface
        is_red = (frame // 30) % 2 == 0
        color = (255, 0, 0) if is_red else (0, 0, 255)
        alpha = int(abs(math.sin(frame * 0.15)) * 120)
        
        if sirene_top:
            sirene_top.fill(color); sirene_top.set_alpha(alpha)
            sirene_bottom.fill(color); sirene_bottom.set_alpha(alpha)
            screen.blit(sirene_top, (0,0))
            screen.blit(sirene_bottom, (0, h-30))

        # 4. Título & Ícones (Com shake)
        float_y = int(math.sin(frame * 0.05) * 5)
        cx, cy = w // 2, int(h * 0.10) + float_y
        
        # Sombra e Texto
        t_surf = layout['title_surf']
        t_rect = t_surf.get_rect(center=(cx, cy))
        screen.blit(layout['title_shadow'], (t_rect.x + 3 + shake_x, t_rect.y + 3 + shake_y))
        screen.blit(t_surf, (t_rect.x + shake_x, t_rect.y + shake_y))

        # Ícones Cadeado
        if layout['icon_title']:
            ico = layout['icon_title']
            # Brilho simples (blend add do proprio icone)
            screen.blit(ico, (t_rect.left - ico.get_width() - 20 + shake_x, t_rect.centery - ico.get_height()//2 + shake_y))
            screen.blit(ico, (t_rect.right + 20 + shake_x, t_rect.centery - ico.get_height()//2 + shake_y))

        # 5. UI do Incidente (Cacheada)
        if current_incident_surf:
            cont_x = 100 + shake_x
            cont_y = int(h * 0.22) + float_y + shake_y
            screen.blit(current_incident_surf, (cont_x, cont_y))
            
            # Botões
            mouse_pos = pygame.mouse.get_pos()
            adj_mouse = (mouse_pos[0] - shake_x, mouse_pos[1] - shake_y)
            
            # Base Y dos botões (recalculada para alinhar com container flutuante)
            # Assumimos que o cache criou botões baseados em um Y fixo, 
            # aqui ajustamos apenas o offset de animação de entrada
            
            # Altura do container
            cont_h = current_incident_surf.get_height()
            btn_base_y = cont_y + cont_h + int(h * 0.05)

            for i, btn_data in enumerate(current_buttons):
                # Animação de entrada
                offset_anim = max(0, (20 - (time.time() - start_time)*40)) * (-1 if i==0 else 1)
                
                # Rect real na tela
                rect = btn_data["rect"].copy()
                rect.x += offset_anim + shake_x
                rect.y = btn_base_y + shake_y # Override Y to follow float
                
                hover = rect.collidepoint(mouse_pos)
                
                # Cores
                bg_col = (20, 40, 90, 230)
                bord_col = (0, 150, 255)
                
                if transitioning:
                    inc = incidentes[indice]
                    if btn_data["text"] == inc["correta"]:
                        bg_col = (0, 180, 0, 230)
                        bord_col = (255, 255, 255)
                    elif feedback and not feedback[1] and hover: # Errado selecionado
                         bg_col = (180, 0, 0, 230)
                elif hover:
                    bg_col = (40, 80, 160, 240)
                    bord_col = (255, 255, 255)

                # Desenha Botão
                pygame.draw.rect(screen, bg_col, rect, border_radius=10)
                pygame.draw.rect(screen, bord_col, rect, 2, border_radius=10)
                
                # Texto do Botão (Cacheado)
                txt = btn_data["surf"]
                screen.blit(txt, txt.get_rect(center=rect.center))

        # 6. Timer Bar
        if not transitioning:
            t_rest = max(0, tempo_base - (time.time() - start_time))
        else:
            t_rest = 0 # Congela ou zera visualmente
            
        ratio = t_rest / tempo_base
        bar_w = int((w * 0.8) * ratio)
        bar_x = w * 0.1
        bar_y = h - 80 + shake_y
        
        col = (0, 255, 0)
        if ratio < 0.5: col = (255, 255, 0)
        if ratio < 0.2: col = (255, 0, 0)
        
        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, w*0.8, 16), border_radius=8)
        if bar_w > 0:
            pygame.draw.rect(screen, col, (bar_x, bar_y, bar_w, 16), border_radius=8)
            
        # Icone Hacker na barra
        h_icon = layout['icon_hacker']
        screen.blit(h_icon, (bar_x + bar_w - h_icon.get_width()//2 + shake_x, bar_y + 8 - h_icon.get_height()//2 + shake_y))
        
        # Timer Text
        t_str = layout['font_timer'].render(f"{t_rest:.1f}s", True, (255, 255, 255))
        screen.blit(t_str, (w//2 - t_str.get_width()//2 + shake_x, bar_y - 30 + shake_y))

        # Score
        draw_score_display(screen, ScoreManager.get_score(), layout['font_small'], "topright")

        # Feedback Overlay
        if feedback and transitioning:
            msg, acerto = feedback
            c = (0, 100, 0, 200) if acerto else (140, 0, 0, 200)
            ov = pygame.Surface((w, 80), pygame.SRCALPHA)
            ov.fill(c)
            ft = layout['font_title'].render(msg, True, (255, 255, 255))
            ov.blit(ft, ft.get_rect(center=(w//2, 40)))
            screen.blit(ov, (0, h//2 - 40))

        # === LÓGICA DE TEMPO ===
        if t_rest <= 0 and not transitioning:
            transitioning = True
            transition_start_time = time.time()
            ScoreManager.add_points(pontos_erro)
            feedback = ("TEMPO ESGOTADO", False)
            audio_manager.play_sfx_if_exists("errado")
            shake_amount = 20

        pygame.display.flip()
        await asyncio.sleep(0) # Vital

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    screen = pygame.display.get_surface()
                    resize_assets(screen)
                    cache_incident_ui(indice)
                elif event.key == pygame.K_ESCAPE:
                    return ScoreManager.get_score()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not transitioning:
                # Recalcula rects atuais
                if current_incident_surf:
                    # Precisamos reconstruir os rects baseados na posição atual (com float/shake) para o collide
                    # Mas para simplificar o clique, usamos a posição base Y calculada
                    # Recalculo rápido:
                    cont_h = current_incident_surf.get_height()
                    cont_y = int(h * 0.22) + float_y # base y do container
                    btn_y_base = cont_y + cont_h + int(h * 0.05)
                    
                    for i, btn_data in enumerate(current_buttons):
                        offset_anim = max(0, (20 - (time.time() - start_time)*40)) * (-1 if i==0 else 1)
                        # Rect temporário para teste de colisão
                        r_test = btn_data["rect"].copy()
                        r_test.x += offset_anim + shake_x
                        r_test.y = btn_y_base + shake_y
                        
                        if r_test.collidepoint(mouse_pos):
                            transitioning = True
                            transition_start_time = time.time()
                            
                            inc = incidentes[indice]
                            if btn_data["text"] == inc["correta"]:
                                ScoreManager.add_points(pontos_acerto)
                                feedback = ("AMEAÇA BLOQUEADA", True)
                                audio_manager.play_sfx_if_exists("correto")
                                shake_amount = 0
                            else:
                                ScoreManager.add_points(pontos_erro)
                                feedback = ("ERRO CRÍTICO", False)
                                audio_manager.play_sfx_if_exists("errado")
                                shake_amount = 20
                            break

    return ScoreManager.get_score()