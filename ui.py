import pygame

AZZURRO = (135, 206, 235)
BIANCO = (255, 255, 255)
GIALLO_PULSANTE = (220, 200, 0)
ROSSO_PULSANTE = (213, 50, 80)
ORO_RECORD = (255, 215, 0)
VERDE_MELA = (0, 255, 100)
GIALLO_PASSI = (255, 215, 0)

def disegna_menu_iniziale(dis, larghezza, altezza):
    dis.fill((20, 20, 20))
    font_titolo = pygame.font.SysFont("arial", 40, bold=True)
    titolo = font_titolo.render("Scegli la modalità:", True, BIANCO)
    dis.blit(titolo, (larghezza//2 - titolo.get_width()//2, altezza//3))
    
    btn_classico = pygame.Rect(larghezza//2 - 230, altezza//2, 200, 60)
    btn_addestramento = pygame.Rect(larghezza//2 + 30, altezza//2, 200, 60)
    
    pygame.draw.rect(dis, GIALLO_PULSANTE, btn_classico, border_radius=10)
    pygame.draw.rect(dis, ROSSO_PULSANTE, btn_addestramento, border_radius=10)
    
    font_btn = pygame.font.SysFont("arial", 22, bold=True)
    t_classico = font_btn.render("Classico", True, (0, 0, 0))
    t_addestro = font_btn.render("Addestramento", True, BIANCO)
    
    dis.blit(t_classico, (btn_classico.centerx - t_classico.get_width()//2, btn_classico.centery - t_classico.get_height()//2))
    dis.blit(t_addestro, (btn_addestramento.centerx - t_addestro.get_width()//2, btn_addestramento.centery - t_addestro.get_height()//2))
    
    return btn_classico, btn_addestramento

def disegna_game_over_classico(dis, larghezza, altezza):
    sfondo = pygame.Surface((larghezza, altezza), pygame.SRCALPHA)
    sfondo.fill((0, 0, 0, 200))
    dis.blit(sfondo, (0, 0))
    
    font_titolo = pygame.font.SysFont("arial", 50, bold=True)
    titolo = font_titolo.render("GAME OVER", True, (213, 50, 80))
    dis.blit(titolo, (larghezza//2 - titolo.get_width()//2, altezza//4))
    
    btn_w, btn_h = 220, 50
    spazio = 20
    start_y = altezza // 2 - 30
    
    btn_riprova = pygame.Rect(larghezza//2 - btn_w//2, start_y, btn_w, btn_h)
    btn_menu = pygame.Rect(larghezza//2 - btn_w//2, start_y + btn_h + spazio, btn_w, btn_h)
    btn_esci = pygame.Rect(larghezza//2 - btn_w//2, start_y + (btn_h + spazio)*2, btn_w, btn_h)
    
    pygame.draw.rect(dis, GIALLO_PULSANTE, btn_riprova, border_radius=8)
    pygame.draw.rect(dis, GIALLO_PULSANTE, btn_menu, border_radius=8)
    pygame.draw.rect(dis, GIALLO_PULSANTE, btn_esci, border_radius=8)
    
    font_btn = pygame.font.SysFont("arial", 22, bold=True)
    t_rip = font_btn.render("Riprova", True, (0, 0, 0))
    t_men = font_btn.render("Menù Iniziale", True, (0, 0, 0))
    t_esc = font_btn.render("Esci", True, (0, 0, 0))
    
    dis.blit(t_rip, (btn_riprova.centerx - t_rip.get_width()//2, btn_riprova.centery - t_rip.get_height()//2))
    dis.blit(t_men, (btn_menu.centerx - t_men.get_width()//2, btn_menu.centery - t_men.get_height()//2))
    dis.blit(t_esc, (btn_esci.centerx - t_esc.get_width()//2, btn_esci.centery - t_esc.get_height()//2))
    
    return btn_riprova, btn_menu, btn_esci

def disegna_pannello_ui_addestramento(dis, premio_reale, mele_attuali, max_mele, larghezza, altezza_pannello, slider_val):
    pygame.draw.rect(dis, AZZURRO, [0, 0, larghezza, altezza_pannello])
    
    font_titoli = pygame.font.SysFont("arial", 20, bold=True)
    
    # --- RIGA 1: Mele attuali ---
    txt_mele = font_titoli.render(f"Mele attuali: {mele_attuali}", True, (0, 0, 0))
    dis.blit(txt_mele, (20, 12))
    
    # --- RIGA 2: Premio RL dell'episodio corrente + pulsante Info Premi ---
    txt_premio_rl = font_titoli.render(f"Premio RL (Episodio Corrente): {premio_reale:.3f}", True, (0, 0, 0))
    dis.blit(txt_premio_rl, (20, 46))
    
    btn_info_x = 20 + txt_premio_rl.get_width() + 15
    btn_info = pygame.Rect(btn_info_x, 43, 110, 28)
    pygame.draw.rect(dis, GIALLO_PULSANTE, btn_info, border_radius=6)
    pygame.draw.rect(dis, (0, 0, 0), btn_info, 1, border_radius=6)
    
    font_btn = pygame.font.SysFont("arial", 14, bold=True)
    t_info = font_btn.render("Info Premi", True, (0, 0, 0))
    dis.blit(t_info, (btn_info.centerx - t_info.get_width()//2, btn_info.centery - t_info.get_height()//2))

    # --- RIGA 3: SLIDER VELOCITÀ (riga propria, per non sovrapporsi al pulsante Info Premi) ---
    slider_w = 200
    slider_h = 8
    slider_x = max(90, larghezza - slider_w - 90)
    slider_y = altezza_pannello - 30
    
    font_small = pygame.font.SysFont("arial", 12, bold=True)
    txt_lento = font_small.render("Lento", True, (0, 0, 0))
    dis.blit(txt_lento, (slider_x - txt_lento.get_width() - 15, slider_y - 4))
    dis.blit(font_small.render("0", True, (0,0,0)), (slider_x + slider_w//2 - 4, slider_y - 20))
    dis.blit(font_small.render("MAX", True, (0,0,0)), (slider_x + slider_w + 10, slider_y - 4))
    
    pygame.draw.rect(dis, (100, 100, 100), [slider_x, slider_y, slider_w, slider_h], border_radius=4)
    pygame.draw.line(dis, (0, 0, 0), (slider_x + slider_w//2, slider_y - 3), (slider_x + slider_w//2, slider_y + slider_h + 3), 2)
    
    knob_x = slider_x + int((slider_val + 1.0) / 2.0 * slider_w)
    knob_rect = pygame.Rect(knob_x - 8, slider_y - 8, 16, 24)
    pygame.draw.rect(dis, BIANCO, knob_rect, border_radius=5)
    pygame.draw.rect(dis, (0,0,0), knob_rect, 1, border_radius=5)
    
    return pygame.Rect(slider_x, slider_y, slider_w, slider_h), pygame.Rect(slider_x - 15, slider_y - 15, slider_w + 30, slider_h + 30), btn_info

def _disegna_grafico_grande(dis, dati, titolo, label_y, label_x, x, y, w, h, colore_linea, record_assoluto):
    sfondo = pygame.Surface((w, h))
    sfondo.fill((30, 30, 30))
    dis.blit(sfondo, (x, y))

    font_titolo = pygame.font.SysFont("arial", 20, bold=True)
    font_assi = pygame.font.SysFont("arial", 15, bold=True)
    font_valori = pygame.font.SysFont("arial", 11)
    
    pygame.draw.rect(dis, (100, 100, 100), (x, y, w, h), 2)
    
    # --- Titolo del grafico: ben visibile ---
    testo_titolo = font_titolo.render(titolo, True, BIANCO)
    dis.blit(testo_titolo, (x + w//2 - testo_titolo.get_width()//2, y + 8))

    if len(dati) < 2: return

    # Scaliamo il grafico sui dati effettivamente visibili (non sul record assoluto),
    # così l'andamento recente si vede sempre bene "zoomato" e non appiattito
    val_max = max(dati)
    val_min = min(dati)
    if val_max == val_min:
        val_max += 1
    
    pad_left = 55
    pad_bottom = 35
    pad_top = 45
    pad_right = 15
    
    pygame.draw.line(dis, (150, 150, 150), (x + pad_left, y + h - pad_bottom), (x + w - pad_right, y + h - pad_bottom), 2)
    pygame.draw.line(dis, (150, 150, 150), (x + pad_left, y + pad_top), (x + pad_left, y + h - pad_bottom), 2)
    
    # --- Etichette assi: ben visibili, in evidenza ---
    txt_y = font_assi.render(label_y, True, BIANCO)
    dis.blit(txt_y, (x + 8, y + pad_top - 20))
    
    txt_x = font_assi.render(label_x, True, BIANCO)
    dis.blit(txt_x, (x + w - txt_x.get_width() - 10, y + h - 18))
    
    # --- Valori numerici min/max: piccoli e discreti, non in risalto ---
    dis.blit(font_valori.render(str(int(val_max)), True, (150, 150, 150)), (x + 8, y + pad_top))
    dis.blit(font_valori.render(str(int(val_min)), True, (150, 150, 150)), (x + 8, y + h - pad_bottom - 14))

    punti = []
    for i, val in enumerate(dati):
        px = x + pad_left + (i / (len(dati) - 1)) * (w - pad_left - pad_right)
        div = (val_max - val_min) if (val_max - val_min) != 0 else 1
        py = y + h - pad_bottom - ((val - val_min) / div) * (h - pad_top - pad_bottom)
        punti.append((px, py))

    pygame.draw.lines(dis, colore_linea, False, punti, 3)

def disegna_grafici_dashboard(dis, storico_mele, storico_passi, larghezza, y_grafici, altezza_grafici, record_mele, record_passi):
    pygame.draw.rect(dis, (15, 15, 15), [0, y_grafici, larghezza, altezza_grafici])

    spazio = 20
    w = (larghezza - (spazio * 3)) // 2
    h = altezza_grafici - 20
    y = y_grafici + 10

    _disegna_grafico_grande(dis, storico_mele, "Andamento Mele Mangiate", "Mele", "Tentativi", spazio, y, w, h, VERDE_MELA, record_mele)
    _disegna_grafico_grande(dis, storico_passi, "Andamento Sopravvivenza", "Passi", "Tentativi", spazio*2 + w, y, w, h, GIALLO_PASSI, record_passi)

def disegna_popup_info(dis, larghezza, altezza):
    sfondo = pygame.Surface((larghezza, altezza), pygame.SRCALPHA)
    sfondo.fill((0, 0, 0, 180))
    dis.blit(sfondo, (0, 0))
    
    popup_w, popup_h = 400, 260
    popup_rect = pygame.Rect(larghezza//2 - popup_w//2, altezza//2 - popup_h//2, popup_w, popup_h)
    pygame.draw.rect(dis, (40, 40, 40), popup_rect, border_radius=10)
    pygame.draw.rect(dis, GIALLO_PULSANTE, popup_rect, 2, border_radius=10)
    
    font_titolo = pygame.font.SysFont("arial", 20, bold=True)
    font_testo = pygame.font.SysFont("arial", 16)
    
    titolo = font_titolo.render("Info Premi Reali RL (PPO)", True, GIALLO_PULSANTE)
    dis.blit(titolo, (popup_rect.centerx - titolo.get_width()//2, popup_rect.y + 15))
    
    testi = [
        "+ Mela mangiata: +10.0",
        "+ Avvicinamento mela: +0.015",
        "- Allontanamento mela: -0.015",
        "- Malus temporale (step): -0.005",
        "X Scontro con se stesso: -2.0",
        "X Scontro col muro: -1.5",
        "X Morte per inedia: -1.0"
    ]
    
    for i, t in enumerate(testi):
        lbl = font_testo.render(t, True, BIANCO)
        dis.blit(lbl, (popup_rect.x + 30, popup_rect.y + 55 + i*22))
        
    btn_chiudi = pygame.Rect(popup_rect.centerx - 50, popup_rect.bottom - 40, 100, 30)
    pygame.draw.rect(dis, ROSSO_PULSANTE, btn_chiudi, border_radius=5)
    
    lbl_chiudi = font_testo.render("Chiudi", True, BIANCO)
    dis.blit(lbl_chiudi, (btn_chiudi.centerx - lbl_chiudi.get_width()//2, btn_chiudi.centery - lbl_chiudi.get_height()//2))
    
    return btn_chiudi