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
            - id:       identificativo numerico univoco
            - name:     nome breve del tipo di cartellino
            - metadata: descrizione breve per ricerca semantica via embedding
        """
        def cdr(cdr_id: int, name: str, metadata: str) -> Dict[str, Any]:
            return {"id": cdr_id, "name": name, "metadata": metadata}

        return [
            # VOIP / SIP
            cdr(1,  "SIP Call",      "Cartellino di chiamata VoIP SIP: sessione voce/video completa con INVITE, ACK, BYE, durata, endpoint, codec."),
            cdr(2,  "SIP Register",  "Registrazione utente SIP al registrar: AOR, contact, expires, esito autenticazione."),
            cdr(5,  "SIP METHOD",    "Singola call o metodo SIP: OPTIONS, MESSAGE, SUBSCRIBE, NOTIFY, REFER, INFO."),
            cdr(47, "SIP SCENARIO",  "Scenario SIP end-to-end: correlazione di più dialoghi SIP per call forking, transfer, forwarding."),

            # VOIP / H323 e Gateway
            cdr(3,  "H323",          "Chiamata VoIP H.323: segnalazione H.225/Q.931 e controllo H.245, tipica di gateway PSTN legacy."),
            cdr(4,  "H248/MEGACO",   "Controllo gateway H.248/MEGACO tra MGC e MG: gestione terminazioni e contesti media in reti NGN."),

            # SS7 / Segnalazione PSTN e mobile 2G-3G
            cdr(6,  "ISUP",          "Segnalazione SS7 ISUP: chiamata TDM/PSTN tra centrali con IAM, ACM, ANM, REL, RLC."),
            cdr(7,  "IUA",           "Trasporto segnalazione ISDN Q.921/Q.931 su SCTP (SIGTRAN IUA): ponte TDM-IP."),
            cdr(8,  "ASERI",         "Segnalazione proprietaria ASERI/CAS per interconnessioni storiche rete italiana TDM."),
            cdr(9,  "INAP",          "Dialogo SS7 INAP tra SSP e SCP per servizi rete intelligente: numeri verdi, prepagato, VPN voce."),
            cdr(10, "MAP",           "Segnalazione SS7 MAP tra HLR, VLR, MSC, SMSC, SGSN: location update, autenticazione, SMS, USSD mobile 2G/3G."),
            cdr(11, "SNM",           "Messaggi gestione rete di segnalazione MTP3 SS7: link e route COO, COA, TFP, TFA."),
            cdr(12, "SSNM",          "Notifiche stato sottosistema SCCP SS7: SSP, SSA, SST per raggiungibilità subsystem."),
            cdr(13, "SCMG",          "Gestione e diagnostica livello SCCP SS7."),
            cdr(14, "LSSU",          "Link Status Signal Unit MTP2 SS7: allineamento e stato link di segnalazione."),
            cdr(29, "CAMEL",         "Dialogo SS7 CAMEL tra SSF e SCF per servizi mobili intelligenti: prepagato, roaming, VPN mobile."),

            # DNS
            cdr(15, "DNS",           "Transazione DNS: query e response di risoluzione nomi, record A, AAAA, NAPTR, SRV, ENUM."),

            # DIAMETER / AAA
            cdr(16, "DIAMETER",      "Sessione Diameter AAA per reti IMS ed EPC: interfacce Gx, Gy, Rx, S6a, Cx per autenticazione e charging."),

            # S3CP
            cdr(17, "S3CP",          "Controllo sessione applicativa S3CP: protocollo interno per session e service control."),

            # LDAP
            cdr(19, "LDAP",          "Operazione LDAP su directory server: bind, search, modify verso HSS/HLR frontend e profili abbonati."),

            # HTTP
            cdr(22, "HTTP TR",       "Transazione HTTP singola: request/response con metodo, URL, status code, header, byte e tempi."),
            cdr(23, "HTTP SESS",     "Sessione HTTP: aggregazione di più transazioni HTTP sulla stessa connessione TCP con metriche complessive."),

            # IP / Traffic
            cdr(20, "CDR",           "Cartellino IP generico CDR: flusso IP a 5-tuple con volume, durata e timestamp."),
            cdr(21, "CDRI",          "Cartellino IP intermedio CDRI: record parziale emesso periodicamente per flussi di lunga durata (interim accounting)."),
            cdr(24, "VIDEO",         "Flusso video IP RTP/RTSP/HLS/DASH: bitrate, jitter, packet loss, rebuffering, codec per streaming."),

            # GEOLOCATION
            cdr(45, "GEOLOCATION",   "Geolocalizzazione terminale: posizione stimata con cell-id, TA, GPS, A-GPS, trilaterazione, timestamp e accuratezza."),

            # MOBILE / LTE 4G
            cdr(18, "GTP",           "Tunneling GTP control e user plane: creazione e gestione PDP/PDN context tra SGSN/SGW e GGSN/PGW in 2G/3G/4G."),
            cdr(26, "S1AP",          "Segnalazione S1AP LTE tra eNodeB e MME: gestione bearer e mobilità UE sull'interfaccia S1."),
            cdr(27, "S1AP CTX",      "Contesto S1AP aggregato per UE LTE: ciclo di vita completo su interfaccia S1 con attach, handover, release."),
            cdr(28, "SGSAP",         "Protocollo SGs tra MME e MSC: interworking LTE-CS per CSFB e SMS over SGs."),
            cdr(48, "S1AP USER",     "Vista user-centric S1AP: aggregazione di tutti gli eventi S1 associati a un singolo utente LTE."),
            cdr(40, "IUPS",          "Segnalazione RANAP interfaccia Iu-PS 3G: RNC e SGSN per packet switched domain UMTS."),
            cdr(41, "A",             "Segnalazione BSSAP interfaccia A 2G: BSC e MSC per circuit switched domain GSM."),
            cdr(42, "IUCS",          "Segnalazione RANAP interfaccia Iu-CS 3G: RNC e MSC per circuit switched domain UMTS."),
            cdr(43, "GB",            "Segnalazione BSSGP/NS interfaccia Gb 2G/GPRS: BSS e SGSN per packet switched GPRS/EDGE."),
            cdr(30, "PFCP",          "Controllo PFCP interfaccia N4/Sx: SMF/SGW-C verso UPF/SGW-U per separazione control e user plane in EPC CUPS e 5GC."),
            cdr(31, "MOSTI",         "Monitoraggio sessioni mobili MOSTI: correlazione eventi cross-interfaccia per analisi esperienza utente mobile."),

            # MOBILE / 5G Core SBA
            cdr(32, "NAUSF",         "Servizio 5G Core Nausf: autenticazione primaria UE tra AUSF, AMF e UDM."),
            cdr(33, "NGAP CTX",      "Contesto NGAP aggregato per UE 5G: ciclo di vita su interfaccia N2 con registration, PDU session, handover."),
            cdr(34, "NUDM",          "Servizio 5G Core Nudm: accesso dati di sottoscrizione UDM per profili, autenticazione e autorizzazioni."),
            cdr(35, "NGAP",          "Segnalazione NGAP interfaccia N2 5G: gNB e AMF per gestione accesso e mobilità."),
            cdr(36, "NAMF",          "Servizio 5G Core Namf: AMF per registrazione UE, gestione mobilità e sessioni NAS."),
            cdr(37, "NSMF",          "Servizio 5G Core Nsmf: SMF per creazione, modifica e rilascio PDU session."),
            cdr(38, "NSMSF",         "Servizio 5G Core Nsmsf: SMSF per trasporto SMS over NAS in 5G."),
            cdr(39, "NNSSF",         "Servizio 5G Core Nnssf: NSSF per selezione e gestione network slice."),
            cdr(44, "NPCF",          "Servizio 5G Core Npcf: PCF per policy control, QoS e charging rules."),
            cdr(46, "NNRF",          "Servizio 5G Core Nnrf: NRF per registrazione e discovery delle network function."),
            cdr(49, "EBM EVENTS",    "Eventi EBM (Event Based Monitoring): notifiche puntuali su soglie, anomalie e KPI di rete prodotti dal modulo TMA."),
        ]
