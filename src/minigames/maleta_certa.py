# ===========================================================
#           MINIGAME MALETA CERTA (WEB SAFE MODE)
# ===========================================================

import pygame
import random
import sys
import os
import math
import asyncio

# Imports seguros (com fallback se falhar)
try:
    from src.utils import show_pause_screen, draw_text_wrapped, draw_score_display, load_font
    from src.score_manager import ScoreManager
    from src.audio_manager import audio_manager 
    import src.difficulty_manager as dm
except ImportError as e:
    print(f"Erro crítico de importação: {e}")

# ===========================================================
#            BANCO DE DESAFIOS
# ===========================================================
ALL_CHALLENGES = {
    "facil": [
        {"problema": "A empresa sofre com decisões de TI desalinhadas aos objetivos de negócio.", "opcoes": ["Adotar COBIT 2019", "Trocar equipamentos", "Fazer backup"], "correta": "Adotar COBIT 2019"},
        {"problema": "Usuários continuam caindo em golpes de phishing.", "opcoes": ["Treinar Usuários", "Atualizar Servidor", "Comprar licenças"], "correta": "Treinar Usuários"},
        {"problema": "Há falhas frequentes na comunicação entre TI e negócios.", "opcoes": ["Criar Comitê de TI", "Aumentar orçamento", "Comprar ERP"], "correta": "Criar Comitê de TI"},
        {"problema": "Incidentes não são registrados formalmente.", "opcoes": ["Gestão de Incidentes", "Contratar analistas", "Aumentar data center"], "correta": "Gestão de Incidentes"},
        {"problema": "Auditorias mostram falhas recorrentes de compliance.", "opcoes": ["Reforçar Controles", "Reduzir políticas", "Migrar para nuvem"], "correta": "Reforçar Controles"},
        {"problema": "O time de TI está sobrecarregado com tarefas manuais.", "opcoes": ["Automatizar Processos", "Contratar estagiários", "Ignorar chamados"], "correta": "Automatizar Processos"}
    ],
    "normal": [
        {"problema": "A TI não consegue priorizar projetos estratégicos.", "opcoes": ["Gestão de Portfólio", "Cancelar projetos", "Focar no operacional"], "correta": "Gestão de Portfólio"},
        {"problema": "Riscos de segurança não são monitorados proativamente.", "opcoes": ["Gestão de Riscos", "Instalar antivírus grátis", "Esperar o ataque"], "correta": "Gestão de Riscos"},
        {"problema": "Não se sabe se o investimento em TI traz retorno.", "opcoes": ["Gestão de Valor", "Cortar custos", "Aumentar preços"], "correta": "Gestão de Valor"},
        {"problema": "Mudanças no sistema causam falhas constantes.", "opcoes": ["Gestão de Mudanças", "Proibir atualizações", "Testar em produção"], "correta": "Gestão de Mudanças"},
        {"problema": "Dados sensíveis estão sendo acessados indevidamente.", "opcoes": ["Gestão de Identidade", "Bloquear internet", "Confiar nos usuários"], "correta": "Gestão de Identidade"},
        {"problema": "A empresa não tem plano para desastres.", "opcoes": ["Plano de Continuidade", "Backup em fita", "Rezar"], "correta": "Plano de Continuidade"}
    ],
    "dificil": [
        {"problema": "Falta alinhamento entre Arquitetura de TI e Estratégia.", "opcoes": ["Arquitetura Corporativa", "Comprar servidores", "Trocar o CIO"], "correta": "Arquitetura Corporativa"},
        {"problema": "A TI não atende aos níveis de serviço acordados (SLA).", "opcoes": ["Gestão de Nível de Serviço", "Ignorar o contrato", "Culpar o usuário"], "correta": "Gestão de Nível de Serviço"},
        {"problema": "Custos de TI estão opacos e sem controle.", "opcoes": ["Gestão Financeira de TI", "Planilha Excel", "Pedir mais dinheiro"], "correta": "Gestão Financeira de TI"},
        {"problema": "Fornecedores não entregam o prometido.", "opcoes": ["Gestão de Fornecedores", "Trocar de fornecedor", "Aceitar o prejuízo"], "correta": "Gestão de Fornecedores"},
        {"problema": "A qualidade dos softwares entregues é baixa.", "opcoes": ["Gestão da Qualidade", "Testar menos", "Lançar rápido"], "correta": "Gestão da Qualidade"},
        {"problema": "Conhecimento crítico está retido em poucas pessoas.", "opcoes": ["Gestão do Conhecimento", "Aumentar salários", "Impedir demissões"], "correta": "Gestão do Conhecimento"}
    ]
}

# ===========================================================
#              SISTEMA DE PARTÍCULAS (SAFE)
# ===========================================================
class MalaParticle:
    __slots__ = ('screen_w', 'screen_h', 'image', 'x', 'y', 'speed', 'alpha')

    def __init__(self, screen_w, screen_h, icon_surf):
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        size = random.randint(20, 36)
        
        # SEGURANÇA: Se a imagem não veio (None), cria um quadrado amarelo
        if icon_surf is None:
            self.image = pygame.Surface((size, size))
            self.image.fill((220, 200, 50)) 
        else:
            try:
                # Usa SCALE simples, smoothscale pode travar web
                self.image = pygame.transform.scale(icon_surf, (size, size))
            except:
                self.image = pygame.Surface((size, size))
                self.image.fill((220, 200, 50))

        self.image.set_alpha(random.randint(80, 150))
        self.reset(first_run=True)

    def reset(self, first_run=False):
        self.x = random.randint(0, self.screen_w)
        if first_run:
            self.y = random.randint(0, self.screen_h)
        else:
            self.y = random.randint(-200, -50)
        self.speed = random.uniform(0.7, 1.7)

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > self.screen_h + 10:
            self.reset()

    def draw(self, screen):
        screen.blit(self.image, (int(self.x), int(self.y)))


# ===========================================================
#   CLASSE DE BOTÃO OTIMIZADA
# ===========================================================
class MaletaButton:
    def __init__(self, base_rect, text, font):
        self.base_rect = base_rect
        self.text = text
        self.font = font
        self.current_rect = base_rect.copy()
        
        # Gera superfícies
        self.surf_normal = self._create_surface((20, 30, 60, 160), (0, 180, 255), (80, 120, 200), False)
        self.surf_hover = self._create_surface((40, 60, 120, 210), (150, 220, 255), (150, 220, 255), True)

    def _create_surface(self, body_color, border_color, handle_color, is_hover):
        w, h = self.base_rect.width, self.base_rect.height
        surf = pygame.Surface((w, h + 40), pygame.SRCALPHA)
        body_y = 30
        
        # Alça
        handle_w = int(w * 0.3)
        handle_h = 25
        handle_x = (w - handle_w) // 2
        handle_rect = pygame.Rect(handle_x, body_y - 15, handle_w, handle_h)
        
        pygame.draw.rect(surf, (*body_color[:3], 100), handle_rect, border_radius=10)
        pygame.draw.rect(surf, handle_color, handle_rect, 3, border_radius=10)

        # Corpo
        body_rect = pygame.Rect(0, body_y, w, h)
        pygame.draw.rect(surf, body_color, body_rect, border_radius=15)
        pygame.draw.rect(surf, border_color, body_rect, 2 if not is_hover else 3, border_radius=15)

        # Texto
        text_rect = body_rect.inflate(-20, -20)
        try:
            draw_text_wrapped(surf, self.text, self.font, (255, 255, 255), text_rect)
        except:
            # Fallback se draw_text_wrapped falhar
            pass
        
        return surf

    def draw(self, screen, anim_offset, is_hovered):
        lift = -6 if is_hovered else 0
        current_y = self.base_rect.y + anim_offset + lift
        self.current_rect.y = current_y
        
        shadow_rect = pygame.Rect(self.base_rect.x + 5, current_y + 8, self.base_rect.width, self.base_rect.height)
        pygame.draw.rect(screen, (0, 0, 0, 100 if is_hovered else 80), shadow_rect, border_radius=15)
        
        img = self.surf_hover if is_hovered else self.surf_normal
        screen.blit(img, (self.base_rect.x, current_y - 30))

    def check_hover(self, pos):
        return self.current_rect.collidepoint(pos)


# ===========================================================
#             FUNÇÃO PRINCIPAL
# ===========================================================
async def run_maleta_certa(screen):
    pygame.display.set_caption("Qual é a Maleta Certa?")
    clock = pygame.time.Clock()

    layout = {}
    
    # Caminhos diretos (Web Friendly)
    # Tentamos carregar de 'assets/...' direto, que é como o pygbag monta
    bg_path = "assets/background/background_maleta_certa.png"
    icon_path = "assets/icons/mala.png"

    # --- CARREGAMENTO SEGURO ---
    bg_original = None
    try:
        bg_original = pygame.image.load(bg_path).convert()
    except Exception:
        # Tenta caminho absoluto como fallback (para rodar local no python normal)
        try:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            bg_original = pygame.image.load(os.path.join(base, bg_path)).convert()
        except:
            pass

    mala_icon_original = None
    try:
        mala_icon_original = pygame.image.load(icon_path).convert_alpha()
    except Exception:
        try:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            mala_icon_original = pygame.image.load(os.path.join(base, icon_path)).convert_alpha()
        except:
            pass

    # === RESIZE & CACHE ===
    def resize_assets(surface):
        w, h = surface.get_size()
        
        # Background Safe
        if bg_original:
            try:
                layout['background'] = pygame.transform.scale(bg_original, (w, h))
            except:
                layout['background'] = pygame.Surface((w, h)); layout['background'].fill((40, 0, 0))
        else:
            layout['background'] = pygame.Surface((w, h))
            layout['background'].fill((40, 0, 0))

        # Mala Safe
        if mala_icon_original:
            try:
                # Usa SCALE ao invés de smoothscale para evitar crash na web
                layout['mala_icon'] = mala_icon_original
                layout['mala_big'] = pygame.transform.scale(mala_icon_original, (int(h*0.09), int(h*0.09)))
            except:
                layout['mala_icon'] = None
                layout['mala_big'] = None
        else:
            # Fallback quadrado amarelo
            s = int(h*0.09)
            fallback = pygame.Surface((s, s))
            fallback.fill((255, 200, 0))
            layout['mala_icon'] = fallback
            layout['mala_big'] = fallback

        # Fontes Safe
        def safe_font(size):
            try:
                return load_font(size)
            except:
                return pygame.font.SysFont(None, size)

        layout['font_title'] = safe_font(min(int(h * 0.085), 70))
        layout['font_text'] = safe_font(min(int(h * 0.065), 44))
        layout['font_small'] = safe_font(min(int(h * 0.048), 34))
        
        # Titulo Cache
        try:
            t_txt = "Qual é a Maleta Certa?"
            layout['title_surf'] = layout['font_title'].render(t_txt, True, (255, 215, 0))
            layout['title_shadow'] = layout['font_title'].render(t_txt, True, (0, 0, 0))
            layout['title_rect'] = layout['title_surf'].get_rect(center=(w // 2, int(h * 0.10)))
        except:
            pass

    resize_assets(screen)

    # Partículas
    particles = []
    if layout.get('mala_icon'):
        particles = [MalaParticle(screen.get_width(), screen.get_height(), layout['mala_icon']) for _ in range(12)]

    diff_rules = dm.get_rules()
    q_type = dm.get_question_set_type()
    desafios = ALL_CHALLENGES.get(q_type, ALL_CHALLENGES["normal"])
    # Cópia segura para não alterar o original
    desafios = [d.copy() for d in desafios]
    random.shuffle(desafios)
    
    pontos_acerto = 10 + diff_rules["bonus_acerto"]
    pontos_erro = -diff_rules["perda_pontos"]

    indice = 0
    efeitos = []
    anim_timer = 0
    
    current_buttons = []
    current_question_surf = None
    current_question_rect = None
    
    def setup_ui(idx):
        nonlocal current_buttons, current_question_surf, current_question_rect
        w, h = screen.get_size()
        desafio = desafios[idx]
        
        # Embaralha
        opcoes = desafio["opcoes"][:]
        random.shuffle(opcoes)
        
        # Container
        c_h = int(h * 0.22)
        c_w = w - 160
        c_rect = pygame.Rect(80, int(h * 0.22), c_w, c_h)
        current_question_rect = c_rect
        
        s = pygame.Surface((c_w, c_h + 30), pygame.SRCALPHA)
        body_rect = pygame.Rect(0, 15, c_w, c_h)
        pygame.draw.rect(s, (20, 30, 60, 180), body_rect, border_radius=15)
        pygame.draw.rect(s, (80, 220, 255), body_rect, 2, border_radius=15)
        
        try:
            badge_surf = layout['font_small'].render("PROBLEMA", True, (20, 30, 60))
            badge_bg = badge_surf.get_rect().inflate(30, 12)
            badge_bg.topleft = (20, 0)
            pygame.draw.rect(s, (80, 220, 255), badge_bg, border_radius=8)
            s.blit(badge_surf, badge_surf.get_rect(center=badge_bg.center))
            
            text_area = body_rect.inflate(-40, -10)
            text_area.top += 25
            text_area.height -= 25
            draw_text_wrapped(s, desafio["problema"], layout['font_text'], (255, 255, 255), text_area)
        except:
            pass # Evita crash no render de texto
        
        current_question_surf = s
        
        # Botões
        largura = int(w * 0.27)
        altura = int(h * 0.17)
        esp = int(w * 0.05)
        total = largura * 3 + esp * 2
        start_x = (w - total) // 2
        base_y = int(h * 0.58)
        
        current_buttons = []
        for i, txt in enumerate(opcoes):
            r = pygame.Rect(start_x + i * (largura + esp), base_y, largura, altura)
            btn = MaletaButton(r, txt, layout['font_small'])
            current_buttons.append(btn)

    if indice < len(desafios):
        setup_ui(indice)

    # Loop principal
    while True:
        dt = clock.tick(60) / 16.0
        anim_timer += 1
        mouse_pos = pygame.mouse.get_pos()
        
        if indice >= len(desafios):
            audio_manager.play_sfx_if_exists("roleta")
            await show_pause_screen(screen, clock, "Desafio Completo!", f"Pontuação: {ScoreManager.get_score()}", theme="Maleta Certa")
            return ScoreManager.get_score()

        screen.blit(layout['background'], (0, 0))
        
        for p in particles:
            p.update(dt)
            p.draw(screen)

        # Título
        try:
            if layout.get('title_surf'):
                float_y = int(math.sin(anim_timer * 0.04) * 4)
                t_rect = layout['title_rect'].move(0, float_y)
                screen.blit(layout['title_shadow'], t_rect.move(4, 4))
                screen.blit(layout['title_surf'], t_rect)

            if layout.get('mala_big'):
                icon_float = int(math.sin(anim_timer * 0.06) * 3)
                screen.blit(layout['mala_big'], (t_rect.left - layout['mala_big'].get_width() - 15, t_rect.y + icon_float))
                screen.blit(layout['mala_big'], (t_rect.right + 15, t_rect.y + icon_float))
        except:
            pass

        # Pergunta
        if current_question_surf:
            float_box = int(math.sin(anim_timer * 0.03 + 1) * 3)
            screen.blit(current_question_surf, (current_question_rect.x, current_question_rect.y + float_box - 15))

        # Botões
        for i, btn in enumerate(current_buttons):
            hover = btn.check_hover(mouse_pos)
            anim_mala = int(math.sin(anim_timer * 0.05 + i * 0.8) * 5)
            btn.draw(screen, anim_mala, hover)

        # Efeitos
        for e in efeitos[:]:
            e["tempo"] += 1
            alpha = int(255 * (1 - e["tempo"] / e["max_tempo"]))
            c = (0, 255, 0, alpha) if e["tipo"] == "acerto" else (255, 50, 50, alpha)
            
            glow = pygame.Surface((e["rect"].width, e["rect"].height), pygame.SRCALPHA)
            glow.fill(c)
            screen.blit(glow, (e["rect"].x, e["rect"].y)) 
            if e["tempo"] >= e["max_tempo"]:
                efeitos.remove(e)

        draw_score_display(screen, ScoreManager.get_score(), layout['font_small'], "topright")
        pygame.display.flip()
        
        # PONTO VITAL PARA NÃO TRAVAR O NAVEGADOR
        await asyncio.sleep(0)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    screen = pygame.display.get_surface()
                    resize_assets(screen)
                    if indice < len(desafios): setup_ui(indice)
                elif event.key == pygame.K_ESCAPE:
                    return ScoreManager.get_score()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in current_buttons:
                    if btn.check_hover(event.pos):
                        pygame.display.flip()
                        await asyncio.sleep(0.05)

                        is_correct = (btn.text == desafios[indice]["correta"])
                        
                        if is_correct:
                            ScoreManager.add_points(pontos_acerto)
                            audio_manager.play_sfx_if_exists("correto")
                            tipo = "acerto"
                        else:
                            ScoreManager.add_points(pontos_erro)
                            audio_manager.play_sfx_if_exists("errado")
                            tipo = "erro"
                        
                        efeitos.append({"tipo": tipo, "rect": btn.current_rect, "tempo": 0, "max_tempo": 16})
                        
                        indice += 1
                        if indice < len(desafios):
                            setup_ui(indice)
                        break
    
    return ScoreManager.get_score()