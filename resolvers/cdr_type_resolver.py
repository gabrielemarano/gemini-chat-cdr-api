"""
Modulo per la risoluzione del tipo CDR dalle richieste utente.

La classe ``CdrTypeResolver`` interpreta semanticamente (tramite LLM) una
query in linguaggio naturale e la mappa su uno degli id presenti nella lista
dei tipi CDR fornita dal chiamante.

Pipeline:
    1. Pre-filtro via embeddings: vettorizza la richiesta e il campo ``metadata``
       di ogni CDR, restituisce i top-k per similarità coseno.
    2. LLM generativo: sceglie tra i candidati ristretti e restituisce gli id.
    3. Disambiguazione interattiva se i candidati sono più di uno.
"""
import json
import math
import re
import sys
from typing import Any, Dict, List, Optional, Tuple
from langchain_core.messages import HumanMessage, SystemMessage


EXIT_COMMANDS = {"esci", "exit", "quit", "q"}


class _NewQuery(Exception):
    """Segnala che l'utente ha digitato una nuova query durante la disambiguazione."""
    def __init__(self, query: str):
        self.query = query


class CdrTypeResolver:
    """
    Resolver semantico dei tipi CDR.

    Usa embeddings sul campo ``metadata`` dei CDR per un pre-filtro
    language-agnostic e zero-hardcoding, poi delega la scelta finale all'LLM.
    """

    def __init__(self, llm_chat, llm_embed):
        """
        Args:
            llm_chat:  modello generativo LangChain (es. ChatOllama).
            llm_embed: modello di embedding LangChain (es. OllamaEmbeddings).
        """
        self.llm_chat = llm_chat
        self.llm_embed = llm_embed
        self._cache: Dict[str, List[float]] = {}

    # ------------------------------------------------------------------ #
    # API pubblica                                                       #
    # ------------------------------------------------------------------ #
    def resolve(
        self,
        user_request: str,
        cdr_types: List[Dict[str, Any]],
    ) -> Tuple[Any, Optional[str]]:
        if not cdr_types:
            raise ValueError("La lista dei tipi CDR e' vuota.")

        types_by_id = {self._normalize_id(t["id"]): t for t in cdr_types}

        current_request = user_request
        while True:
            filtered = self._pre_filter(current_request, cdr_types)

            if len(filtered) < len(cdr_types):
                print(f"[*] Pre-filtro: ridotti da {len(cdr_types)} a {len(filtered)} candidati")

            candidate_ids = self._ask_llm(current_request, filtered)
            candidate_ids = [cid for cid in candidate_ids if cid in types_by_id]
            candidate_ids = list(dict.fromkeys(candidate_ids))

            # Retry con prompt semplificato se l'LLM non ha restituito id
            # ma il pre-filtro aveva già ristretto la lista
            if len(candidate_ids) == 0 and len(filtered) < len(cdr_types):
                print("[*] Retry LLM con prompt semplificato...")
                candidate_ids = self._ask_llm(current_request, filtered, simplified=True)
                candidate_ids = [cid for cid in candidate_ids if cid in types_by_id]
                candidate_ids = list(dict.fromkeys(candidate_ids))

            if len(candidate_ids) == 1:
                selected = types_by_id[candidate_ids[0]]
                return selected["id"], selected.get("name")

            if len(candidate_ids) == 0:
                # Se il pre-filtro ha trovato candidati ma l'LLM non ha capito
                # la richiesta (es. termine generico come "cartellini"), mostra
                # direttamente i candidati del pre-filtro all'utente.
                if len(filtered) < len(cdr_types):
                    if len(filtered) == 1:
                        selected = filtered[0]
                        return selected["id"], selected.get("name")
                    print("[*] Il termine e' generico: mostro tutti i candidati trovati.")
                    try:
                        selected = self._disambiguate(filtered)
                        return selected["id"], selected.get("name")
                    except _NewQuery as nq:
                        current_request = nq.query
                        continue

                print("[!] Non sono riuscito a individuare un tipo CDR adatto alla richiesta.")
                current_request = self._prompt_user("Riformula la richiesta (o 'esci' per uscire) > ")
                continue

            try:
                selected = self._disambiguate([types_by_id[cid] for cid in candidate_ids])
                return selected["id"], selected.get("name")
            except _NewQuery as nq:
                current_request = nq.query
                continue

        raise RuntimeError("Impossibile risolvere il tipo CDR.")

    # ------------------------------------------------------------------ #
    # Pre-filtro via embeddings su metadata                              #
    # ------------------------------------------------------------------ #
    def _embed(self, text: str) -> List[float]:
        """Embedding con cache per evitare chiamate ripetute sui CDR."""
        if text not in self._cache:
            self._cache[text] = self.llm_embed.embed_query(text)
        return self._cache[text]

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        return dot / (na * nb) if na and nb else 0.0

    def _pre_filter(
        self,
        user_request: str,
        cdr_types: List[Dict[str, Any]],
        top_k: int = 8,
        gap: float = 0.18,
    ) -> List[Dict[str, Any]]:
        """
        Pre-filtro ibrido in due fasi:

        Fase 1 — match letterale sui token tecnici estratti dai nomi CDR.
           I nomi contengono termini tecnici inequivocabili (SIP, GTP, HTTP,
           NGAP, ecc.) estratti dai dati stessi, zero hardcoding.
           "cartellini sip di oggi" → trova "sip" → tutti i CDR SIP.

        Fase 2 — fallback embeddings su name + metadata.
           Usata quando la richiesta non contiene token tecnici riconoscibili
           (es. "segnalazione mobile", "traffico voce").
        """
        request_lower = user_request.lower()

        # Fase 1: match letterale sui token dei nomi CDR (word boundary)
        matched = []
        for cdr in cdr_types:
            name_tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9./+\-]*", str(cdr.get("name", "")))
            for token in name_tokens:
                if len(token) > 1 and re.search(r"\b" + re.escape(token.lower()) + r"\b", request_lower):
                    matched.append(cdr)
                    break

        if matched:
            return matched

        # Fase 2: fallback embeddings su name + metadata
        try:
            req_vec = self._embed(user_request)
            scored = []
            for cdr in cdr_types:
                text = f"{cdr.get('name', '')} {cdr.get('metadata', '')}".strip()
                cdr_vec = self._embed(text)
                scored.append((self._cosine(req_vec, cdr_vec), cdr))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_sim = scored[0][0]
            return [cdr for sim, cdr in scored[:top_k] if top_sim - sim <= gap] or cdr_types

        except Exception as e:
            print(f"[!] Embedding non disponibile, uso lista completa ({e})")
            return cdr_types

    # ------------------------------------------------------------------ #
    # Interazione con l'LLM                                              #
    # ------------------------------------------------------------------ #
    def _ask_llm(self, user_request: str, cdr_types: List[Dict[str, Any]], simplified: bool = False) -> List[Any]:
        if simplified:
            system_prompt = """\
Sei un classificatore di tipi CDR in ambito telecomunicazioni.
Scegli il o i CDR più coerenti con la richiesta utente tra quelli forniti.
Devi SEMPRE restituire almeno un id: scegli quello più probabile.
Non restituire mai una lista vuota se ci sono candidati forniti.
Formato TASSATIVO - solo JSON valido, nessun testo extra:
{"ids": [<id1>, <id2>, ...]}"""
        else:
            system_prompt = """\
Sei un classificatore semantico di tipi di Call Detail Record (CDR) in
ambito telecomunicazioni.

Per ogni CDR hai a disposizione:
  - id:       identificativo univoco
  - name:     nome del tipo
  - metadata: descrizione semantica del cartellino

Scegli il o i CDR più coerenti con la richiesta utente.

IMPORTANTE — termini generici vs. termini specifici:
  - Se la richiesta contiene un termine generico che descrive una categoria
    (es. un tipo di traffico, un dominio tecnologico, una funzione di rete)
    senza indicare un protocollo o un tipo preciso, interpretalo come la
    volontà di ottenere TUTTI i CDR appartenenti a quella categoria.
  - Se invece la richiesta contiene un identificativo tecnico preciso
    (nome di protocollo, standard, interfaccia, ecc.), seleziona solo i CDR
    che corrispondono esattamente a quell'identificativo.
  - In caso di ambiguità, preferisci restituire più id piuttosto che uno solo.

IMPORTANTE — combinazione protocollo + tipo evento:
  - Se la richiesta specifica sia un identificativo tecnico preciso sia un
    tipo di evento o funzione, seleziona SOLO il CDR il cui name e metadata
    rappresentano esattamente quella combinazione, senza allargare ad altri
    CDR dello stesso protocollo o della stessa famiglia di eventi.

Regole:
  - protocollo + tipo evento specifici → restituisci SOLO l'id che li combina entrambi
  - termine tecnico specifico senza tipo evento → restituisci tutti gli id di quel protocollo
  - termine generico di categoria senza protocollo → restituisci TUTTI gli id della famiglia
  - richiesta ampia o che copre più famiglie → restituisci tutti gli id pertinenti
  - richiesta incomprensibile o non mappabile su alcun CDR → restituisci lista vuota
  - non inventare id: usa solo quelli presenti nella lista

Formato TASSATIVO - solo JSON valido, nessun testo extra:
{"ids": [<id1>, <id2>, ...]}"""

        compact = [
            {"id": c.get("id"), "name": c.get("name"), "metadata": c.get("metadata", "")}
            for c in cdr_types
        ]

        user_prompt = (
            f'Richiesta utente:\n"""\n{user_request}\n"""\n\n'
            f"Lista CDR disponibili (JSON):\n{json.dumps(compact, ensure_ascii=False, default=str)}\n\n"
            f'Rispondi SOLO con il JSON {{"ids": [...]}}.'
        )

        print(f"Caratteri: ( system_prompt: {len(system_prompt)} + user_prompt: {len(user_prompt)} ) = {len(system_prompt) + len(user_prompt)}")

        response = self.llm_chat.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        return self._parse_ids(getattr(response, "content", str(response)))

    # ------------------------------------------------------------------ #
    # Parsing risposta LLM                                               #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_ids(raw: str) -> List[Any]:
        if not raw:
            return []
        text = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        text = re.sub(r"\s*```$", "", text)
        for attempt in [text, (re.search(r"\{.*}", text, re.DOTALL) or type("", (), {"group": lambda *a: ""})()).group(0)]:
            try:
                data = json.loads(attempt)
                if isinstance(data, dict) and isinstance(data.get("ids"), list):
                    return [CdrTypeResolver._normalize_id(x) for x in data["ids"]]
                if isinstance(data, list):
                    return [CdrTypeResolver._normalize_id(x) for x in data]
            except (json.JSONDecodeError, AttributeError):
                pass
        return []

    @staticmethod
    def _normalize_id(value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    # ------------------------------------------------------------------ #
    # Disambiguazione interattiva                                        #
    # ------------------------------------------------------------------ #
    def _disambiguate(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("\n[?] Sono stati individuati più tipi CDR compatibili. Seleziona quello desiderato:")
        for idx, cdr in enumerate(candidates, start=1):
            print(f"  [{idx}] {cdr.get('name', '')} — {cdr.get('metadata', '')}")

        valid = {str(i) for i in range(1, len(candidates) + 1)}
        while True:
            choice = self._prompt_user("\nScegli il numero (o scrivi una nuova ricerca) > ")
            if choice in valid:
                return candidates[int(choice) - 1]
            # L'utente ha digitato testo libero: trattalo come nuova query
            print(f"[*] Nuova ricerca: '{choice}'")
            raise _NewQuery(choice)

    # ------------------------------------------------------------------ #
    # Helper input utente                                                #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _prompt_user(prompt: str) -> str:
        try:
            value = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[*] Uscita dalla chat...")
            sys.exit(0)
        if value.lower() in EXIT_COMMANDS:
            print("[*] Uscita dalla chat...")
            sys.exit(0)

        return value
