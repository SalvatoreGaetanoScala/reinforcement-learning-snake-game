# 🐍 Snake RL — Reinforcement Learning con PPO

Un progetto che addestra un agente a giocare a Snake usando **Reinforcement Learning** (algoritmo **PPO** di Stable-Baselines3), con un'interfaccia grafica in **Pygame** per giocare sia in modalità classica (manuale) sia in modalità addestramento (osservando l'agente allenarsi in tempo reale), affiancata da un pannello **Tkinter** con i parametri live del training.

## 🎮 Caratteristiche

- **Modalità Classico**: gioca a Snake manualmente con i tasti `W`, `A`, `S`, `D`.
- **Modalità Addestramento**: osserva l'agente RL giocare in autonomia, con:
  - pannello statistiche in tempo reale (mele mangiate, premio dell'episodio corrente);
  - grafici a schermo dell'andamento storico (mele mangiate e passi di sopravvivenza);
  - slider per regolare la velocità di simulazione;
  - finestra separata (Tkinter) con gli iperparametri dell'algoritmo PPO;
  - popup informativo con il dettaglio del sistema di reward.
- **Salvataggio persistente** delle statistiche di addestramento (`stats.json`) e del modello (`snake_model.zip`), così l'addestramento può essere interrotto e ripreso in qualsiasi momento.

## 🧠 Come funziona l'agente

L'ambiente (`SnakeEnv`) è costruito sopra l'interfaccia `gymnasium.Env` e osserva lo stato del gioco tramite un vettore di **28 valori**:
- per **8 direzioni** attorno alla testa dello snake: distanza dal muro, distanza dalla mela e distanza dal proprio corpo (24 valori);
- **4 valori** aggiuntivi per la codifica one-hot della direzione corrente (su/giù/sinistra/destra).

Le azioni possibili sono 4 (Su, Giù, Sinistra, Destra) e il sistema di reward è così definito:

| Evento | Reward |
|---|---|
| 🍎 Mela mangiata | `+10.0` |
| ↗️ Avvicinamento alla mela | `+0.015` |
| ↘️ Allontanamento dalla mela | `-0.015` |
| ⏱️ Malus temporale (per ogni step) | `-0.005` |
| 💥 Scontro con se stesso | `-2.0` |
| 🧱 Scontro con il muro | `-1.5` |
| 😵 Morte per inedia (troppi passi senza mangiare) | `-1.0` |

L'agente è addestrato con **PPO (Proximal Policy Optimization)**, un algoritmo Actor-Critic della famiglia dei Policy Gradient, usando la libreria **Stable-Baselines3**.

### Iperparametri principali

| Parametro | Valore |
|---|---|
| Algoritmo | PPO (Stable-Baselines3) |
| Learning Rate | `3e-4`, con decadimento lineare |
| Gamma (discount factor) | `0.999` |
| Entropy coefficient | `0.01` |
| Architettura rete | Policy `[256, 256]`, Value `[256, 256]` |
| N-Steps | `2048` |
| Batch size | `64` |
| Epoche per update | `10` |

## 📁 Struttura del progetto

```
.
├── main.py            # Loop principale: menu, modalità classico/addestramento, rendering Pygame
├── snake_env.py        # Ambiente Gymnasium custom del gioco Snake
├── train.py             # Script per addestrare/continuare l'addestramento del modello PPO
├── ui.py                  # Funzioni di disegno per menu, pannelli, grafici e popup
├── snake_model.zip     # Modello PPO addestrato (pesi della rete neurale)
└── stats.json           # Storico persistente delle statistiche di addestramento
```

## ⚙️ Requisiti

- Python 3.9+
- [pygame](https://www.pygame.org/)
- [gymnasium](https://gymnasium.farama.org/)
- [stable-baselines3](https://stable-baselines3.readthedocs.io/)
- numpy

Installazione rapida:

```bash
pip install pygame gymnasium stable-baselines3 numpy
```

## 🚀 Come avviare il progetto

### Giocare / osservare l'agente

```bash
python main.py
```

Dal menu iniziale puoi scegliere tra modalità **Classico** (gioco manuale) e **Addestramento** (osservazione dell'agente).

### Addestrare (o continuare ad addestrare) il modello

```bash
python train.py
```

Se esiste già un file `snake_model.zip`, il training riprenderà da lì continuando ad accumulare i progressi. Altrimenti verrà creato un nuovo modello da zero. È possibile interrompere l'addestramento in qualsiasi momento con `CTRL+C`: il modello verrà comunque salvato prima della chiusura.

## 📊 Statistiche

Il file `stats.json` mantiene traccia di:
- numero totale di iterazioni (partite giocate);
- numero totale di passi eseguiti nell'ambiente;
- storico delle ultime 100 partite (mele mangiate e passi sopravvissuti);
- record assoluti di mele mangiate e passi sopravvissuti.

## 📄 Documentazione

Il progetto include una relazione tecnica (`reinforcement_learning_con_snake.pdf`) che approfondisce:
- i concetti teorici di base del Reinforcement Learning e del Processo di Decisione di Markov (MDP);
- il funzionamento dell'algoritmo PPO e la sua funzione obiettivo;
- l'analisi dettagliata dell'implementazione del progetto.

## 📝 Licenza

Aggiungi qui la licenza che preferisci (es. MIT, GPL-3.0) prima di pubblicare il repository.
