import os
from typing import Callable
from stable_baselines3 import PPO
from snake_env import SnakeEnv

def linear_schedule(initial_value: float) -> Callable[[float], float]:
    """
    Crea un programma di decremento lineare del Learning Rate.
    progress_remaining scende da 1.0 (inizio) a 0.0 (fine addestramento).
    """
    def func(progress_remaining: float) -> float:
        return progress_remaining * initial_value
    return func

# Creiamo l'ambiente
env = SnakeEnv()
nome_modello = "snake_model"

# Iperparametri pensati per episodi lunghi e per mantenere l'esplorazione
policy_kwargs = dict(net_arch=dict(pi=[256, 256], vf=[256, 256]))

# CONTROLLO SALVATAGGIO: Se il modello esiste, lo carichiamo per continuare i progressi!
if os.path.exists(f"{nome_modello}.zip"):
    print("🧠 Cervello esistente trovato! Caricamento in corso per continuare l'addestramento...")
    model = PPO.load(nome_modello, env=env)
    model.ent_coef = 0.01
    # Applichiamo lo schedule decrescente anche sul modello caricato per rifinire i pesi
    model.learning_rate = linear_schedule(1.5e-4)
else:
    print("🌱 Nessun salvataggio trovato. Creazione di un nuovo cervello da zero...")
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        policy_kwargs=policy_kwargs,
        ent_coef=0.01,      # mantiene l'esplorazione ed evita la convergenza prematura
        gamma=0.999,        # orizzonte temporale lungo (fondamentale per muoversi su tutta la mappa)
        learning_rate=linear_schedule(3e-4), # Learning rate adattivo lineare
        n_steps=2048,
    )

# Avvio dell'addestramento
print("🚀 Avvio dell'addestramento... Premi CTRL+C nella console per interrompere e salvare in qualsiasi momento.")
try:
    # Impostiamo un totale di timesteps ideale (es. 2 milioni)
    model.learn(total_timesteps=2_500_000, log_interval=10)
except KeyboardInterrupt:
    print("\n🛑 Addestramento interrotto manualmente dall'utente.")

print(f"💾 Salvataggio del modello in {nome_modello}.zip...")
model.save(nome_modello)
print("✅ Modello salvato con successo! Ora puoi avviare main.py per vederlo all'opera.")