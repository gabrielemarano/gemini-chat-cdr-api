import argparse
import sys
import yaml
from langchain_ollama import ChatOllama, OllamaEmbeddings

from clients import MockClient
from clients.oracle_client import OracleClient
from resolvers.cdr_type_resolver import CdrTypeResolver


# ─────────────────────────────────────────────────────────────────────────────
# Data Functions
# ─────────────────────────────────────────────────────────────────────────────
def load_cdr_types(mock_client: MockClient):
    """Carica i tipi di CDR"""
    return mock_client.load_cdr_types()


def load_config(path: str) -> dict:
    """Carica la configurazione da file YAML."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[ERROR] File di configurazione non trovato: {path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"[ERROR] Errore nel parsing del file YAML: {e}")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Init Functions
# ─────────────────────────────────────────────────────────────────────────────
def init_llm(cfg: dict) -> dict:
    """
    Inizializza tutti i modelli LLM definiti nel config.

    Riconosce automaticamente le sezioni che iniziano con 'llm-' e
    istanzia ChatOllama o OllamaEmbeddings in base al nome:
      - llm-chat  → ChatOllama  (modello generativo)
      - llm-embed → OllamaEmbeddings (modello di embedding)

    Returns:
        dict con i modelli pronti all'uso, indicizzati per nome logico.
    """
    llms = {}
    for key, llm_cfg in cfg.items():
        if not key.startswith("llm-"):
            continue

        client_kwargs = {}
        if llm_cfg.get("api_key"):
            client_kwargs["headers"] = {"Authorization": f"Bearer {llm_cfg['api_key']}"}

        if key == "llm-embed":
            llms[key] = OllamaEmbeddings(
                base_url=llm_cfg["url"],
                model=llm_cfg["model"],
                client_kwargs=client_kwargs,
            )
        else:
            llms[key] = ChatOllama(
                base_url=llm_cfg["url"],
                model=llm_cfg["model"],
                temperature=0.1,
                client_kwargs=client_kwargs,
            )

        print(f"[OK] LLM inizializzato: {key} (model={llm_cfg['model']}).")

    return llms


def init_clients(cfg: dict) -> dict:
    """
    Inizializza tutti i client verso sistemi esterni (ORACLE, ES, ecc.).

    Returns:
        dict con i client pronti all'uso, indicizzati per nome logico.
    """
    oracle_cfg = cfg["oracle"]
    clients = {}

    clients["mock"] = MockClient()

    clients["oracle"] = OracleClient(
        host=oracle_cfg["host"],
        port=oracle_cfg["port"],
        service_name=oracle_cfg["service"],
        user=oracle_cfg["user"],
        password=oracle_cfg["password"],
    )

    print(f"[OK] Client inizializzati. {', '.join(clients.keys())}")
    return clients


def init_resolvers(llm_chat, llm_embed) -> dict:
    """
    Inizializza tutti i resolver semantici.

    Args:
        llm_chat:  modello generativo per la classificazione finale.
        llm_embed: modello di embedding per il pre-filtro semantico su metadata.

    Returns:
        dict con i resolver pronti all'uso, indicizzati per nome logico.
    """
    resolvers = {}

    resolvers["cdr_type"] = CdrTypeResolver(llm_chat=llm_chat, llm_embed=llm_embed)

    print(f"[OK] Resolver inizializzati: {', '.join(resolvers.keys())}")
    return resolvers


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Gemini Query Chat (for API)")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Percorso del file di configurazione YAML (default: config.yaml)",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)

    # Inizializza
    llms = init_llm(cfg)
    resolvers = init_resolvers(llms["llm-chat"], llms["llm-embed"])
    clients = init_clients(cfg)

    cdr_types = load_cdr_types(clients["mock"])

    # Chat loop interattiva
    print("\n" + "="*70)
    print("Chat CDR Analyzer - Digita 'esci' per uscire")
    print("="*70)

    try:
        while True:
            # Richiedi input dall'utente
            print("\n")
            user_request = input("[USER] > ").strip()

            # Comandi di uscita
            if user_request.lower() in ['exit', 'quit', 'q', 'esci']:
                print("\n[*] Uscita dalla chat...")
                break

            # Salta richieste vuote
            if not user_request:
                print("[!] Inserisci una richiesta valida")
                continue

            # Estrai il tipo di CDR dalla richiesta
            print("[*] Analisi della richiesta...")
            cdr_type_id, cdr_type_name = resolvers["cdr_type"].resolve(user_request, cdr_types)

            print(f"\n[OK] Tipo CDR selezionato: ({cdr_type_id}) {cdr_type_name}")

    except KeyboardInterrupt:
        print("\n\n[*] Interrotto dall'utente (Ctrl+C)")
    except Exception as e:
        print(f"\n[ERROR] Errore durante l'esecuzione: {e}")

    print("\n[*] Sessione terminata")


if __name__ == "__main__":
    main()
