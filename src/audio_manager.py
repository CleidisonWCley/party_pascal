#====================================================
#              SISTEMA DE AUDIO (WEB OPTIMIZED)
#====================================================

"""
AudioManager – Versão Web/Mobile 2025 (Ultra Baixa Latência)
-------------------------------------------------------
Melhorias Críticas:
- Buffer de áudio forçado para 512 (reduz delay no Chrome).
- Novo método 'preload_all_sfx()': Carrega tudo na RAM no início.
- Cache persistente para evitar releitura de disco (lento na web).
"""

import os
import json
import pygame
import sys
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "sounds", "musica")
SFX_DIR = os.path.join(ASSETS_DIR, "sounds", "efeitos")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")

class _AudioManager:
    def __init__(self, default_music_vol=0.5, default_sfx_vol=1.0):
        
        # ==========================================================
        # 1. Mixer Otimizado para WEB (Baixa Latência)
        # ==========================================================
        if not pygame.mixer.get_init():
            try:
                # Na Web, o buffer controla o atraso. 
                # 512 é o "ponto doce" entre rapidez e qualidade.
                # Se o áudio chiar (crackling), suba para 1024.
                buffer_size = 512 
                
                # Frequência 44100 é nativa da maioria dos browsers
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=buffer_size)
                pygame.mixer.init()
                
                # Garante canais suficientes para sons simultâneos
                pygame.mixer.set_num_channels(16)
            except Exception as e:
                print(f"Erro ao iniciar mixer: {e}")
        
        self.fade_speed = 600

        # ==========================================================
        # TABELA DE ARQUIVOS
        # ==========================================================
        self.music_table = {
            "loop_start": "loop_start.ogg",  
            "musica_final": "musica_final.ogg",
            "musica_show_do_bilhao": "musica_show_do_bilhao.ogg",
            "musica_batalha_naval": "musica_batalha_naval.ogg",
            "musica_maleta_certa": "musica_maleta_certa.ogg",
            "musica_rodada_bonus": "musica_rodada_bonus.ogg",
            "musica_perseguicao": "musica_perseguicao.ogg",
            "musica_stop": "musica_stop.ogg",
            "cutscene_intro": "musica_cutscene_intro.ogg",
            "cutscene_final": "musica_cutscene_final.ogg",
            "menu": "music_menu.ogg",
        }

        self.sfx_table = {
            "correto": "correto.wav",
            "errado": "errado.wav",
            "explosion": "explosion.wav",
            "roleta": "roleta.wav",
        }

        # Cache vital para performance Web
        self.sfx_cache = {}

        # Carrega configurações
        settings = self._load_settings()
        self.music_volume = settings.get("music_volume", default_music_vol)
        self.sfx_volume = settings.get("fx_volume", default_sfx_vol)

        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except:
            pass

        self.current_music_key = None

    # ==========================================================
    # NOVO: PRÉ-CARREGAMENTO (A Chave para 0 Lag)
    # ==========================================================
    def preload_all_sfx(self):
        """
        Carrega TODOS os efeitos sonoros para a RAM imediatamente.
        Chame isso na tela de carregamento ou logo após pygame.init().
        Isso elimina a travadinha na primeira vez que o som toca.
        """
        print("Iniciando preload de áudio...")
        count = 0
        for key in self.sfx_table:
            if self._load_sfx_to_cache(key):
                count += 1
        print(f"Áudio: {count} efeitos pré-carregados na RAM.")

    def _load_sfx_to_cache(self, key):
        """Carrega um único som para o cache se ainda não estiver lá."""
        if key in self.sfx_cache:
            return self.sfx_cache[key]

        path = self._sfx_path(key)
        if not path or not os.path.exists(path):
            return None

        try:
            # Carrega o som
            snd = pygame.mixer.Sound(path)
            snd.set_volume(self.sfx_volume)
            # Guarda na memória
            self.sfx_cache[key] = snd
            return snd
        except Exception as e:
            print(f"Erro ao carregar SFX {key}: {e}")
            return None

    # ==========================================================
    # INTERNOS
    # ==========================================================

    def _load_settings(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
        except:
            pass
        return {"music_volume": 0.5, "fx_volume": 1.0}

    def _music_path(self, key):
        filename = self.music_table.get(key)
        if not filename: return None
        
        path_music = os.path.join(MUSIC_DIR, filename)
        if os.path.exists(path_music): return path_music

        path_sfx = os.path.join(SFX_DIR, filename)
        if os.path.exists(path_sfx): return path_sfx
        
        return path_music

    def _sfx_path(self, key):
        f = self.sfx_table.get(key)
        if not f: return None
        return os.path.join(SFX_DIR, f)

    # ==========================================================
    # MÚSICA (STREAMING)
    # ==========================================================

    def play_music_if_exists(self, key, loops=-1):
        path = self._music_path(key)
        if not path or not os.path.exists(path):
            return False

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
            self.current_music_key = key
            return True
        except:
            return False

    def fade_to_music_if_exists(self, key, fade_ms=None):
        path = self._music_path(key)
        if not path or not os.path.exists(path):
            return False

        fade_ms = fade_ms or self.fade_speed

        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_ms)
        except:
            pass

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)
            self.current_music_key = key
            return True
        except:
            return False
    
    def fade_to_music(self, key, fade_ms=None):
        return self.fade_to_music_if_exists(key, fade_ms)

    # ==========================================================
    # SFX (INSTANTÂNEO VIA CACHE)
    # ==========================================================

    def play_sfx_if_exists(self, key):
        # Tenta pegar do cache primeiro (Rápido)
        snd = self.sfx_cache.get(key)
        
        # Se não estiver no cache, carrega agora (Lento, mas fallback)
        if not snd:
            snd = self._load_sfx_to_cache(key)
        
        if snd:
            try:
                snd.play()
                return True
            except:
                pass
        return False

    # ==========================================================
    # VOLUMES
    # ==========================================================

    def set_music_volume(self, v):
        v = max(0, min(1, float(v)))
        self.music_volume = v
        try:
            pygame.mixer.music.set_volume(v)
        except:
            pass
        self._save_settings()

    def set_sfx_volume(self, v):
        v = max(0, min(1, float(v)))
        self.sfx_volume = v
        # Atualiza volume de todos os sons já carregados na memória
        for snd in self.sfx_cache.values():
            try:
                snd.set_volume(v)
            except:
                pass
        self._save_settings()

    def _save_settings(self):
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump({"music_volume": self.music_volume,
                           "fx_volume": self.sfx_volume}, f, indent=2)
        except:
            pass

# Singleton
AudioManager = _AudioManager()
audio_manager = AudioManager