"""
sound_manager.py — Audio system for the Fire Brigade Pathfinding Visualizer.

Uses pygame.mixer for multi-channel sound playback.  All audio access is
centralised here so the rest of the codebase only calls high-level methods
like `play_button_click()` or `start_siren()`.

Supported sounds:
    One-shot:  button click, cell click, error beep, fire extinguisher
    Looping:   fire crackling (ambient), fire-brigade siren

If pygame is unavailable or the mixer fails to initialise, the manager
degrades gracefully — every public method becomes a silent no-op.
"""

import os

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    AUDIO_AVAILABLE = True
except (ImportError, Exception):
    AUDIO_AVAILABLE = False

from gui.constants import SOUND_DIR


class SoundManager:
    """Centralised audio controller with a mute toggle.

    Attributes:
        muted: Whether all audio output is currently suppressed.
    """

    def __init__(self):
        self.muted           = False
        self._sounds         = {}       # key → pygame.mixer.Sound
        self._fire_channel   = None     # Dedicated channel for fire-crackling loop
        self._siren_channel  = None     # Dedicated channel for siren loop

        if not AUDIO_AVAILABLE:
            return

        # ── Load all sound effects ──
        self._load("button_click", "UI_button_click.mp3",    volume=0.15)
        self._load("cell_click",   "UI_cell_click.mp3",      volume=0.12)
        self._load("error",        "UI_error.mp3",           volume=0.30)
        self._load("fire_crackle", "fire_crackling2.mp3",    volume=0.30)
        self._load("siren",        "FireBrigadierSiren.mp3", volume=0.12)
        self._load("extinguisher", "fire_extinguisher.mp3",  volume=0.35)

        # ── Reserve two high-numbered channels for looping sounds ──
        pygame.mixer.set_num_channels(8)
        self._fire_channel  = pygame.mixer.Channel(6)
        self._siren_channel = pygame.mixer.Channel(7)

    # ═══════════════════════════════════════════════════════════
    #  INTERNAL
    # ═══════════════════════════════════════════════════════════

    def _load(self, key, filename, volume=0.3):
        """Load a sound file from SOUND_DIR and register it under *key*.

        Silently skips if the file is missing or loading fails.
        """
        path = os.path.join(SOUND_DIR, filename)
        if os.path.exists(path):
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(volume)
                self._sounds[key] = snd
            except Exception:
                pass   # Non-critical — audio simply won't play for this key

    def _play(self, key):
        """Play a one-shot sound by key (respects mute state)."""
        if not AUDIO_AVAILABLE or self.muted:
            return
        snd = self._sounds.get(key)
        if snd:
            snd.play()

    # ═══════════════════════════════════════════════════════════
    #  ONE-SHOT SOUNDS
    # ═══════════════════════════════════════════════════════════

    def play_button_click(self):
        """Play the UI button click feedback sound."""
        self._play("button_click")

    def play_cell_click(self):
        """Play the cell placement feedback sound."""
        self._play("cell_click")

    def play_error(self):
        """Play the error/warning beep."""
        self._play("error")

    def play_extinguisher(self):
        """Play the fire-extinguisher spray sound."""
        self._play("extinguisher")

    # ═══════════════════════════════════════════════════════════
    #  LOOPING SOUNDS
    # ═══════════════════════════════════════════════════════════

    def start_fire_crackling(self):
        """Start the fire-crackling ambient loop (idempotent)."""
        if not AUDIO_AVAILABLE or self.muted:
            return
        snd = self._sounds.get("fire_crackle")
        if snd and self._fire_channel and not self._fire_channel.get_busy():
            self._fire_channel.play(snd, loops=-1)

    def stop_fire_crackling(self):
        """Stop the fire-crackling loop."""
        if AUDIO_AVAILABLE and self._fire_channel:
            self._fire_channel.stop()

    def start_siren(self):
        """Start the fire-brigade siren loop."""
        if not AUDIO_AVAILABLE or self.muted:
            return
        snd = self._sounds.get("siren")
        if snd and self._siren_channel:
            self._siren_channel.play(snd, loops=-1)

    def stop_siren(self):
        """Stop the siren loop."""
        if AUDIO_AVAILABLE and self._siren_channel:
            self._siren_channel.stop()

    # ═══════════════════════════════════════════════════════════
    #  MUTE TOGGLE
    # ═══════════════════════════════════════════════════════════

    def toggle_mute(self):
        """Toggle mute on/off.  Stops all loops when muting.

        Returns:
            The new muted state (True = muted).
        """
        self.muted = not self.muted
        if self.muted:
            self.stop_fire_crackling()
            self.stop_siren()
        return self.muted
