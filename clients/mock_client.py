"""
Mock client per simulare il caricamento dei tipi CDR senza dipendere
da un database Oracle reale. Utile per test e sviluppo offline.
"""
from typing import List, Dict, Any


class MockClient:
    """
    Client fittizio che espone la stessa interfaccia minima usata dal main
    per il caricamento dei tipi di CDR.
    """

    def __repr__(self) -> str:
        return "MockClient(in-memory)"

    # ------------------------------------------------------------------ #
    # API                                                                #
    # ------------------------------------------------------------------ #
    def load_cdr_types(self) -> List[Dict[str, Any]]:
        """
        Restituisce l'elenco completo dei tipi di CDR supportati.

        Ogni elemento contiene:
            - id:          identificativo numerico univoco
            - name:        nome breve del tipo di cartellino
            - index:       indice/sorgente tecnica (modulo.tabella) da cui
                           vengono estratti i dati grezzi
            - description: descrizione semantica del protocollo/evento
                           rappresentato dal cartellino
        """
        return [
            {
                "id": 1,
                "name": "SIP Call",
                "index": "mod_voip.raw_sip",
                "description": (
                    "Cartellino di chiamata VoIP basata sul protocollo SIP "
                    "(Session Initiation Protocol, RFC 3261). Traccia il "
                    "ciclo di vita di una sessione voce/video: INVITE, "
                    "risposte provvisorie e finali, ACK, BYE, durata, "
                    "endpoint coinvolti e codec negoziati."
                ),
            },
            {
                "id": 2,
                "name": "SIP Register",
                "index": "mod_voip.raw_sip_reg",
                "description": (
                    "Registrazione di uno user agent SIP presso il "
                    "registrar (REGISTER). Contiene AOR, contact, expires, "
                    "esito dell'autenticazione e binding dell'utente."
                ),
            },
            {
                "id": 3,
                "name": "H323",
                "index": "mod_voip.raw_h323",
                "description": (
                    "Cartellino di chiamata VoIP secondo lo stack ITU-T "
                    "H.323 (segnalazione H.225/Q.931 e controllo H.245). "
                    "Tipico di reti legacy e gateway PSTN."
                ),
            },
            {
                "id": 4,
                "name": "H248/MEGACO",
                "index": "mod_voip.raw_h248",
                "description": (
                    "Protocollo di controllo gateway H.248/MEGACO "
                    "(RFC 3525) usato tra Media Gateway Controller e "
                    "Media Gateway per gestire terminazioni e contesti "
                    "media in reti NGN."
                ),
            },
            {
                "id": 5,
                "name": "SIP METHOD",
                "index": "mod_voip.raw_sip_method",
                "description": (
                    "Singolo metodo/transazione SIP non strettamente "
                    "legato a una call (es. OPTIONS, MESSAGE, SUBSCRIBE, "
                    "NOTIFY, PUBLISH, INFO, REFER). Utile per analisi "
                    "puntuali a livello di metodo."
                ),
            },
            {
                "id": 6,
                "name": "ISUP",
                "index": "mod_ss7.raw_isup",
                "description": (
                    "ISDN User Part del protocollo SS7: segnalazione di "
                    "chiamata in rete TDM/PSTN (IAM, ACM, ANM, REL, RLC) "
                    "tra centrali di commutazione."
                ),
            },
            {
                "id": 7,
                "name": "IUA",
                "index": "mod_ss7.raw_iua",
                "description": (
                    "ISDN User Adaptation Layer (RFC 4233): trasporto "
                    "della segnalazione ISDN Q.921/Q.931 su SCTP, ponte "
                    "tra mondo TDM e reti IP (SIGTRAN)."
                ),
            },
            {
                "id": 8,
                "name": "ASERI",
                "index": "mod_ss7.raw_aseri",
                "description": (
                    "Cartellino proprietario per la segnalazione ASERI "
                    "(varianti italiane SS7/CAS), usato in interconnessioni "
                    "storiche con la rete Telecom Italia."
                ),
            },
            {
                "id": 9,
                "name": "INAP",
                "index": "mod_ss7.raw_inap",
                "description": (
                    "Intelligent Network Application Part: dialoghi tra "
                    "SSP e SCP per servizi di rete intelligente (numeri "
                    "verdi, prepagato, portabilita, VPN voce)."
                ),
            },
            {
                "id": 10,
                "name": "MAP",
                "index": "mod_ss7.raw_map",
                "description": (
                    "Mobile Application Part (SS7): dialoghi tra HLR, "
                    "VLR, MSC, SMSC e SGSN nelle reti mobili 2G/3G "
                    "(location update, autenticazione, SMS, USSD)."
                ),
            },
            {
                "id": 11,
                "name": "SNM",
                "index": "mod_ss7.raw_snm",
                "description": (
                    "Signalling Network Management messages dell'MTP3 "
                    "SS7: gestione di link e route (COO, COA, CBD, CBA, "
                    "TFP, TFA, ecc.)."
                ),
            },
            {
                "id": 12,
                "name": "SSNM",
                "index": "mod_ss7.raw_ssnm",
                "description": (
                    "SCCP Signalling Network Management: notifiche di "
                    "stato del sottosistema SCCP (SSP, SSA, SST) per la "
                    "raggiungibilita dei subsystem SS7."
                ),
            },
            {
                "id": 13,
                "name": "SCMG",
                "index": "mod_ss7.raw_scmg",
                "description": (
                    "SCCP Management messages: gestione e diagnostica "
                    "del livello SCCP in SS7."
                ),
            },
            {
                "id": 14,
                "name": "LSSU",
                "index": "mod_ss7.raw_lssu",
                "description": (
                    "Link Status Signal Unit dell'MTP2 SS7: segnala lo "
                    "stato del link di segnalazione (allineamento, out "
                    "of service, processor outage)."
                ),
            },
            {
                "id": 15,
                "name": "DNS",
                "index": "mod_dns.raw_dns",
                "description": (
                    "Transazioni Domain Name System (RFC 1035): query e "
                    "response di risoluzione nomi, inclusi record A, "
                    "AAAA, NAPTR, SRV usati anche da ENUM/IMS."
                ),
            },
            {
                "id": 16,
                "name": "DIAMETER",
                "index": "mod_diameter.raw_diameter",
                "description": (
                    "Protocollo Diameter (RFC 6733) per AAA in reti IMS "
                    "ed EPC: interfacce Gx, Gy, Rx, S6a, Sh, Cx ecc. "
                    "per autenticazione, autorizzazione e charging."
                ),
            },
            {
                "id": 17,
                "name": "S3CP",
                "index": "mod_s3cp.raw_s3cp",
                "description": (
                    "Cartellino del protocollo di controllo S3CP "
                    "(Session/Service Control), usato in piattaforme "
                    "interne per il controllo di sessione applicativa."
                ),
            },
            {
                "id": 18,
                "name": "GTP",
                "index": "mod_mobile.raw_gtp",
                "description": (
                    "GPRS Tunneling Protocol nelle sue varianti "
                    "GTP-C (control plane: creazione/modifica/cancellazione "
                    "PDP/PDN context) e GTP-U (user plane), trasversale "
                    "a 2G/3G/4G."
                ),
            },
            {
                "id": 19,
                "name": "LDAP",
                "index": "mod_ldap.raw_ldap",
                "description": (
                    "Lightweight Directory Access Protocol (RFC 4511): "
                    "operazioni bind, search, modify verso directory "
                    "server, comunemente HSS/HLR frontend e profili "
                    "abbonati."
                ),
            },
            {
                "id": 20,
                "name": "CDR",
                "index": "mod_ip.raw_ip_cdr",
                "description": (
                    "Cartellino IP generico di tipo CDR: aggregazione "
                    "di flussi IP (5-tuple) con metriche di volume, "
                    "durata e timestamp, indipendente dal protocollo "
                    "applicativo."
                ),
            },
            {
                "id": 21,
                "name": "CDRI",
                "index": "mod_ip.raw_ip_cdri",
                "description": (
                    "Variante 'intermedia' del CDR IP: record parziali "
                    "emessi periodicamente per flussi di lunga durata "
                    "(interim accounting), prima del record finale."
                ),
            },
            {
                "id": 22,
                "name": "HTTP TR",
                "index": "mod_http.raw_http_tr",
                "description": (
                    "HTTP Transaction: singola coppia request/response "
                    "HTTP/HTTPS con metodo, URL, status code, header "
                    "principali, byte scambiati e tempi di risposta."
                ),
            },
            {
                "id": 23,
                "name": "HTTP SESS",
                "index": "",
                "description": (
                    "HTTP Session: aggregazione di piu transazioni HTTP "
                    "appartenenti alla stessa sessione utente/connessione "
                    "TCP, con metriche complessive di sessione."
                ),
            },
            {
                "id": 24,
                "name": "VIDEO",
                "index": "mod_ip.raw_ip_video",
                "description": (
                    "Cartellino di flusso video IP (RTP/RTSP/HLS/DASH): "
                    "metriche di qualita come bitrate, jitter, packet "
                    "loss, rebuffering e codec usati per streaming."
                ),
            },
            {
                "id": 26,
                "name": "S1AP",
                "index": "mod_mobile.raw_s1ap",
                "description": (
                    "S1 Application Protocol (3GPP TS 36.413): "
                    "segnalazione tra eNodeB e MME nell'EPC LTE per "
                    "gestione dei bearer e mobility dell'UE."
                ),
            },
            {
                "id": 27,
                "name": "S1AP CTX",
                "index": "mod_mobile.raw_s1ap_ctx",
                "description": (
                    "Contesto S1AP per UE: cartellino aggregato che "
                    "riassume l'intero ciclo di vita del contesto di un "
                    "utente sull'interfaccia S1 (attach, handover, "
                    "release)."
                ),
            },
            {
                "id": 28,
                "name": "SGSAP",
                "index": "mod_mobile.raw_sgsap",
                "description": (
                    "SGs Application Protocol (3GPP TS 29.118): "
                    "interlavoro tra MME (LTE) e MSC (CS) per CSFB e "
                    "consegna SMS over SGs."
                ),
            },
            {
                "id": 29,
                "name": "CAMEL",
                "index": "mod_ss7.raw_camel",
                "description": (
                    "Customised Applications for Mobile networks "
                    "Enhanced Logic: dialoghi SS7 per servizi IN su "
                    "reti mobili (prepagato, roaming intelligente, "
                    "VPN mobili)."
                ),
            },
            {
                "id": 30,
                "name": "PFCP",
                "index": "mod_mobile.raw_pfcp",
                "description": (
                    "Packet Forwarding Control Protocol (3GPP TS 29.244): "
                    "interfaccia Sx/N4 tra control plane (SMF/SGW-C) e "
                    "user plane (UPF/SGW-U) in EPC CUPS e 5GC."
                ),
            },
            {
                "id": 31,
                "name": "MOSTI",
                "index": "mod_mobile.raw_mosti",
                "description": (
                    "Cartellino interno MOSTI per il monitoraggio di "
                    "sessioni mobili e correlazione di eventi cross-"
                    "interfaccia."
                ),
            },
            {
                "id": 32,
                "name": "NAUSF",
                "index": "mod_mobile.raw_nausf",
                "description": (
                    "Service Based Interface Nausf del 5G Core: "
                    "autenticazione primaria dell'UE gestita dall'AUSF "
                    "verso AMF e UDM."
                ),
            },
            {
                "id": 33,
                "name": "NGAP CTX",
                "index": "mod_mobile.raw_ngap_ctx",
                "description": (
                    "Contesto NGAP per UE: aggregazione del ciclo di "
                    "vita dell'utente sull'interfaccia N2 tra gNB e AMF "
                    "(registration, PDU session, handover)."
                ),
            },
            {
                "id": 34,
                "name": "NUDM",
                "index": "mod_mobile.raw_nudm",
                "description": (
                    "Service Based Interface Nudm del 5G Core: accesso "
                    "ai dati di sottoscrizione gestiti dall'UDM "
                    "(profili, autenticazione, autorizzazioni)."
                ),
            },
            {
                "id": 35,
                "name": "NGAP",
                "index": "mod_mobile.raw_ngap",
                "description": (
                    "NG Application Protocol (3GPP TS 38.413): "
                    "segnalazione tra gNB e AMF sull'interfaccia N2 "
                    "del 5G Core."
                ),
            },
            {
                "id": 36,
                "name": "NAMF",
                "index": "mod_mobile.raw_namf",
                "description": (
                    "Service Based Interface Namf del 5G Core: servizi "
                    "esposti dall'AMF (Access and Mobility Management "
                    "Function) per gestione registrazione e mobility."
                ),
            },
            {
                "id": 37,
                "name": "NSMF",
                "index": "mod_mobile.raw_nsmf",
                "description": (
                    "Service Based Interface Nsmf del 5G Core: servizi "
                    "dell'SMF (Session Management Function) per "
                    "creazione e gestione delle PDU session."
                ),
            },
            {
                "id": 38,
                "name": "NSMSF",
                "index": "mod_mobile.raw_nsmsf",
                "description": (
                    "Service Based Interface Nsmsf del 5G Core: "
                    "servizi dell'SMSF per il trasporto SMS over NAS "
                    "in 5G."
                ),
            },
            {
                "id": 39,
                "name": "NNSSF",
                "index": "mod_mobile.raw_nnssf",
                "description": (
                    "Service Based Interface Nnssf del 5G Core: "
                    "selezione del network slice tramite NSSF "
                    "(Network Slice Selection Function)."
                ),
            },
            {
                "id": 40,
                "name": "IUPS",
                "index": "mod_mobile.raw_iups",
                "description": (
                    "Interfaccia Iu-PS (3G UTRAN): segnalazione RANAP "
                    "tra RNC e SGSN per il packet switched domain."
                ),
            },
            {
                "id": 41,
                "name": "A",
                "index": "mod_mobile.raw_mobile_a",
                "description": (
                    "Interfaccia A (2G GERAN): segnalazione BSSAP tra "
                    "BSC e MSC per il circuit switched domain GSM."
                ),
            },
            {
                "id": 42,
                "name": "IUCS",
                "index": "mod_mobile.raw_iucs",
                "description": (
                    "Interfaccia Iu-CS (3G UTRAN): segnalazione RANAP "
                    "tra RNC e MSC per il circuit switched domain UMTS."
                ),
            },
            {
                "id": 43,
                "name": "GB",
                "index": "mod_mobile.raw_gb",
                "description": (
                    "Interfaccia Gb (2G/2.5G): segnalazione BSSGP/NS "
                    "tra BSS e SGSN per il packet switched domain GPRS/"
                    "EDGE."
                ),
            },
            {
                "id": 44,
                "name": "NPCF",
                "index": "mod_mobile.raw_npcf",
                "description": (
                    "Service Based Interface Npcf del 5G Core: policy "
                    "control esposto dal PCF (Policy Control Function) "
                    "per QoS e charging rules."
                ),
            },
            {
                "id": 45,
                "name": "GEOLOCATION",
                "index": "mod_geolocation.raw_geolocation",
                "description": (
                    "Cartellino di geolocalizzazione: posizione stimata "
                    "di terminali/utenti (cell-id, TA, GPS, A-GPS, "
                    "trilateraziona) con timestamp e accuratezza."
                ),
            },
            {
                "id": 46,
                "name": "NNRF",
                "index": "mod_mobile.raw_nnrf",
                "description": (
                    "Service Based Interface Nnrf del 5G Core: "
                    "registrazione e discovery delle Network Function "
                    "tramite NRF (Network Repository Function)."
                ),
            },
            {
                "id": 47,
                "name": "SIP SCENARIO",
                "index": "mod_voip.raw_sip_scenario",
                "description": (
                    "Scenario SIP end-to-end: correlazione di piu "
                    "dialoghi/transazioni SIP appartenenti a una stessa "
                    "esperienza utente (es. call forking, transfer, "
                    "forwarding)."
                ),
            },
            {
                "id": 48,
                "name": "S1AP USER",
                "index": "mod_mobile.raw_s1ap_user",
                "description": (
                    "Vista user-centric dei dati S1AP: cartellino "
                    "aggregato per singolo utente LTE con tutti gli "
                    "eventi S1 a esso associati."
                ),
            },
            {
                "id": 49,
                "name": "EBM EVENTS",
                "index": "mod_tma.raw_ebm_event",
                "description": (
                    "Eventi EBM (Event Based Monitoring) prodotti dal "
                    "modulo TMA: notifiche puntuali su soglie, anomalie "
                    "e KPI di rete."
                ),
            },
        ]

