import argparse
from langchain_ollama import ChatOllama

from clients import MockClient
from clients.oracle_client import OracleClient
from resolvers.cdr_type_resolver import CdrTypeResolver


# ─────────────────────────────────────────────────────────────────────────────
# Data Functions
# ─────────────────────────────────────────────────────────────────────────────
def load_cdr_types(mock_client: MockClient):
    """Carica i tipi di CDR"""
    return mock_client.load_cdr_types()

# ─────────────────────────────────────────────────────────────────────────────
# Init Functions
# ─────────────────────────────────────────────────────────────────────────────
def init_llm(args):
    """Inizializza e restituisce l'istanza dell'LLM configurata da CLI."""
    # client_kwargs = {"timeout": args.llm_timeout}
    client_kwargs = {}
    if args.llm_api_key != "":
        client_kwargs["headers"] = {"Authorization": f"Bearer {args.llm_api_key}"}

    llm = ChatOllama(
        base_url = args.llm_url,
        model = args.llm_model,
        temperature = 0.3,
        client_kwargs = client_kwargs,
    )
    print(f"[OK] LLM inizializzato.")

    return llm


def init_clients(args) -> dict:
    """
    Inizializza tutti i client verso sistemi esterni (ORACLE, ES, ecc.).

    Returns:
        dict con i client pronti all'uso, indicizzati per nome logico.
    """
    clients = {}

    clients["mock"] = MockClient()

    clients["oracle"] = OracleClient(
        host = args.oracle_host,
        port = args.oracle_port,
        service_name = args.oracle_service,
        user = args.oracle_user,
        password = args.oracle_password,
    )

    print(f"[OK] Client inizializzati. {', '.join(clients.keys())}")

    return clients


def init_resolvers(llm) -> dict:
    """
    Inizializza tutti i resolver semantici basati sull'LLM.

    Args:
        llm: istanza dell'LLM da iniettare nei resolver.

    Returns:
        dict con i resolver pronti all'uso, indicizzati per nome logico.
    """
    resolvers = {}

    resolvers["cdr_type"] = CdrTypeResolver(llm = llm)

    print(f"[OK] Resolver inizializzati: {', '.join(resolvers.keys())}")
    return resolvers


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Gemini Query Chat (for API)")

    # LLM parameters
    # parser.add_argument("--llm-url", default="http://localhost:11434", help="LLM - Url")
    # parser.add_argument("--llm-api-key", default="", help="LLM - Api Key")
    # parser.add_argument("--llm-model", default="qwen3.5:4b", help="LLM - Model")
    # parser.add_argument("--llm-timeout", default=120, type=int, help="LLM - Timeout (secondi)")

    parser.add_argument("--llm-url", default="https://api.ollama.com", help="LLM - Url")
    parser.add_argument("--llm-api-key", default="7177994c33354bfd80b7244667f61406.ASx9X2-zM-diubtImF1VQ8qH", help="LLM - Api Key")
    parser.add_argument("--llm-model", default="gemma3:12b", help="LLM - Model")
    parser.add_argument("--llm-timeout", default=120, type=int, help="LLM - Timeout (secondi)")


# Oracle DB parameters
    parser.add_argument("--oracle-host", default="192.168.15.5", help="Oracle - Host")
    parser.add_argument("--oracle-port", default=1521, type=int, help="Oracle - Port")
    parser.add_argument("--oracle-service", default="PDB1_WORKLOAD", help="Oracle - Service Name")
    parser.add_argument("--oracle-user", default="analyzer", help="Oracle - Username")
    parser.add_argument("--oracle-password", default="anacleto", help="Oracle - Password")

    args = parser.parse_args()

    # Inizializza
    llm = init_llm(args)
    resolvers = init_resolvers(llm)
    clients = init_clients(args)

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
