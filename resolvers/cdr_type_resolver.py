"""
Modulo per la risoluzione del tipo CDR dalle richieste utente.

La classe ``CdrTypeResolver`` interpreta semanticamente (tramite LLM) una
query in linguaggio naturale italiano e la mappa su uno degli id presenti
nella lista dei tipi CDR fornita dal chiamante.

Regole funzionali:
    1. La query viene interpretata semanticamente (NON con string matching).
    2. Il modello deve riconoscere il protocollo / dominio (es. SIP, GTP, ...).
    3. Deve distinguere il livello di granularita' richiesto:
         - "chiamate SIP"     -> solo SIP Call (id=1)
         - "cartellini SIP"   -> tutti i tipi SIP (1, 2, 5, 47)
    4. Se la query e' ambigua, il modello puo' restituire piu' id candidati.
    5. La funzione pubblica ``resolve`` deve ritornare un SOLO id: se i
       candidati sono piu' di uno viene chiesto all'utente di scegliere.
    6. L'utente puo' uscire in qualsiasi momento digitando ``esci``
       (oltre a ``exit``, ``quit``, ``q``).
"""
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages import HumanMessage, SystemMessage


# Comandi che permettono all'utente di uscire in qualsiasi momento.
EXIT_COMMANDS = {"esci", "exit", "quit", "q"}


class CdrTypeResolver:
    """
    Resolver semantico dei tipi CDR basato su LLM.

    Non assume nessun campo specifico nei dizionari ``cdr_types`` se non
    il campo obbligatorio ``id``: l'intera lista viene serializzata in
    JSON e passata al modello, che ragiona sui campi disponibili
    (tipicamente ``name``, ``index``, ``description``).
    """

    def __init__(self, llm):
        """
        Args:
            llm: istanza di un modello LangChain compatibile (es. ChatOllama).
        """
        self.llm = llm

    # ------------------------------------------------------------------ #
    # API pubblica                                                       #
    # ------------------------------------------------------------------ #
    def resolve(
        self,
        user_request: str,
        cdr_types: List[Dict[str, Any]],
    ) -> Tuple[Any, Optional[str]]:
        """
        Determina l'id (uno e uno solo) del tipo CDR pertinente alla
        richiesta utente.

        Args:
            user_request: testo libero in italiano scritto dall'utente.
            cdr_types:    lista di dizionari che descrivono i tipi CDR.
                          L'unico campo obbligatorio e' ``id``.

        Returns:
            Tupla ``(id, name)``. ``name`` puo' essere ``None`` se i
            tipi CDR non espongono tale campo.
        """
        if not cdr_types:
            raise ValueError("La lista dei tipi CDR e' vuota.")

        # Indicizza i tipi CDR per id (normalizzato) per lookup rapido.
        types_by_id = {self._normalize_id(t["id"]): t for t in cdr_types}

        current_request = user_request
        while True:
            candidate_ids = self._ask_llm(current_request, cdr_types)

            # Filtra eventuali id "inventati" non presenti nella lista
            # e rimuove duplicati preservando l'ordine.
            candidate_ids = [cid for cid in candidate_ids if cid in types_by_id]
            candidate_ids = list(dict.fromkeys(candidate_ids))

            # Caso 1: un solo candidato -> ritorno diretto.
            if len(candidate_ids) == 1:
                selected = types_by_id[candidate_ids[0]]
                return selected["id"], selected.get("name")

            # Caso 2: nessun candidato -> chiedi di riformulare.
            if len(candidate_ids) == 0:
                print("[!] Non sono riuscito a individuare un tipo CDR adatto "
                      "alla richiesta.")
                current_request = self._prompt_user(
                    "Riformula la richiesta (o 'esci' per uscire) > "
                )
                continue

            # Caso 3: piu' candidati -> disambiguazione interattiva.
            selected = self._disambiguate(
                [types_by_id[cid] for cid in candidate_ids]
            )
            return selected["id"], selected.get("name")

    # ------------------------------------------------------------------ #
    # Interazione con l'LLM                                              #
    # ------------------------------------------------------------------ #
    def _ask_llm(
        self,
        user_request: str,
        cdr_types: List[Dict[str, Any]],
    ) -> List[Any]:
        """
        Invoca l'LLM e restituisce la lista degli id candidati.
        """
        system_prompt = """\
Sei un assistente esperto di reti di telecomunicazione e di Call Detail
Record (CDR). Ricevi:
  - una richiesta in linguaggio naturale (italiano) di un operatore;
  - una lista di tipi di CDR disponibili (in formato JSON), ognuno con
    almeno un campo 'id' e tipicamente anche 'name', 'index' e
    'description'.

Il tuo compito e' selezionare gli id dei tipi CDR semanticamente
pertinenti alla richiesta. Devi ragionare sul SIGNIFICATO dei campi
(in particolare 'description'), non fare un semplice match testuale.

Linee guida fondamentali:
  * Riconosci il protocollo o il dominio menzionato nella richiesta
    (es. SIP, H.323, ISUP, GTP, S1AP, NGAP, HTTP, DNS, DIAMETER, ecc.)
    e considera SOLO i tipi CDR di quel dominio.
  * Distingui il livello di granularita':
      - se l'utente chiede esplicitamente le 'chiamate' di un
        protocollo, seleziona solo il tipo che rappresenta la chiamata
        vera e propria (es. 'chiamate SIP' -> solo SIP Call, id=1);
      - se l'utente parla genericamente di 'cartellini', 'eventi',
        'traffico' di un protocollo, includi TUTTI i tipi CDR di quel
        protocollo (es. 'cartellini SIP' -> SIP Call, SIP Register,
        SIP METHOD, SIP SCENARIO).
  * Ignora completamente i tipi CDR che NON appartengono al dominio
    richiesto.
  * Se la richiesta e' ambigua, includi piu' id candidati: sara'
    l'utente a scegliere.
  * Non inventare id: usa SOLO quelli presenti nella lista fornita,
    copiandoli esattamente (rispettando il tipo: intero o stringa).

Formato di risposta TASSATIVO:
  Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza testo
  aggiuntivo, senza markdown e senza commenti.
  Schema: {"ids": [<id1>, <id2>, ...]}
  Se nessun tipo CDR e' pertinente: {"ids": []}."""

        user_prompt = f"""\
Richiesta utente:
\"\"\"
{user_request}
\"\"\"

Lista dei tipi CDR disponibili (JSON):
{json.dumps(cdr_types, ensure_ascii=False, default=str)}

Rispondi SOLO con il JSON {{"ids": [...]}}."""

        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])

        content = getattr(response, "content", str(response))
        return self._parse_ids(content)

    # ------------------------------------------------------------------ #
    # Parsing della risposta dell'LLM                                    #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_ids(raw: str) -> List[Any]:
        """
        Estrae la lista di id dalla risposta testuale dell'LLM.
        Tollerante a fence markdown e a testo extra prima/dopo il JSON.
        """
        if raw is None:
            return []

        text = raw.strip()
        # Rimuove eventuali fence markdown ```json ... ```
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        candidates = []

        # Tentativo 1: l'intero testo e' JSON valido.
        try:
            candidates.append(json.loads(text))
        except json.JSONDecodeError:
            pass

        # Tentativo 2: cerca il primo oggetto JSON nel testo.
        if not candidates:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    candidates.append(json.loads(match.group(0)))
                except json.JSONDecodeError:
                    pass

        for data in candidates:
            if isinstance(data, dict) and isinstance(data.get("ids"), list):
                return [CdrTypeResolver._normalize_id(x) for x in data["ids"]]
            if isinstance(data, list):
                return [CdrTypeResolver._normalize_id(x) for x in data]

        return []

    @staticmethod
    def _normalize_id(value: Any) -> Any:
        """
        Normalizza un id per il confronto. Le stringhe vengono trimmate,
        gli altri tipi (es. interi) vengono lasciati invariati.
        """
        if isinstance(value, str):
            return value.strip()
        return value

    # ------------------------------------------------------------------ #
    # Disambiguazione interattiva                                        #
    # ------------------------------------------------------------------ #
    def _disambiguate(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Mostra l'elenco dei candidati e chiede all'utente di selezionarne
        uno (per indice o direttamente per id).
        """
        print("\n[?] Sono stati individuati piu' tipi CDR compatibili. "
              "Seleziona quello desiderato:")
        for idx, cdr in enumerate(candidates, start=1):
            name = cdr.get("name").strip()
            print(f"  [{idx}] - {name}")

        valid_indexes = {str(i) for i in range(1, len(candidates) + 1)}

        while True:
            choice = self._prompt_user(
                "\nScegli il numero (o 'esci' per uscire) > "
            )

            if choice in valid_indexes:
                return candidates[int(choice) - 1]

            print("[!] Scelta non valida, riprova.")

    # ------------------------------------------------------------------ #
    # Helper input utente con gestione "esci"                            #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _prompt_user(prompt: str) -> str:
        """
        Legge una riga dall'utente. Se viene digitato un comando di uscita
        (``esci``, ``exit``, ``quit``, ``q``) o viene premuto Ctrl+C/EOF,
        termina immediatamente la sessione con ``sys.exit(0)``.
        """
        try:
            value = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[*] Uscita dalla chat...")
            sys.exit(0)

        if value.lower() in EXIT_COMMANDS:
            print("[*] Uscita dalla chat...")
            sys.exit(0)

        return value
