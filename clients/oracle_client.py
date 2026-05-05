"""
Modulo per la gestione delle connessioni e query Oracle.
"""
import oracledb
from typing import List, Dict, Any, Optional


class OracleClient:
    """
    Classe per gestire connessioni e query al database Oracle.
    Converte automaticamente i risultati in liste di dizionari Python.
    """
    
    def __init__(self, host: str, port: int, service_name: str, user: str, password: str):
        """
        Inizializza la connessione al database Oracle.
        
        Args:
            host: Host del database Oracle
            port: Porta del database
            service_name: Nome del servizio Oracle
            user: Username per l'autenticazione
            password: Password per l'autenticazione
        """
        self.host = host
        self.port = port
        self.service_name = service_name
        self.user = user
        self.password = password
        self._connection = None
        
    def connect(self) -> None:
        """Apre la connessione al database Oracle."""
        if self._connection is None:
            dsn = oracledb.makedsn(self.host, self.port, service_name=self.service_name)
            self._connection = oracledb.connect(user=self.user, password=self.password, dsn=dsn)
    
    def disconnect(self) -> None:
        """Chiude la connessione al database Oracle."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    def is_connected(self) -> bool:
        """Verifica se la connessione è attiva."""
        return self._connection is not None
    
    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Esegue una query SQL e restituisce i risultati come lista di dizionari.
        Gestisce automaticamente la connessione e disconnessione al database.
        
        Args:
            sql: Query SQL da eseguire
            params: Parametri opzionali per la query (dizionario)
        
        Returns:
            Lista di dizionari dove ogni riga è un dizionario {colonna: valore}
        
        Raises:
            oracledb.DatabaseError: Se c'è un errore nell'esecuzione della query
        
        Example:
            >> oracle_client = OracleClient("localhost", 1521, "ORCL", "user", "pass")
            >> results = oracle_client.execute_query("SELECT id, name FROM cdr_type")
            >> print(results)
            [{"id": 1, "name": "SIP"}, {"id": 2, "name": "GTP"}]
        """
        # Connessione automatica
        self.connect()
        
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Converti i risultati in lista di dizionari
            columns = [col[0].lower() for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results
        finally:
            cursor.close()
            # Disconnessione automatica
            self.disconnect()
    
    def __repr__(self) -> str:
        """Rappresentazione stringa della classe."""
        status = "connected" if self.is_connected() else "disconnected"
        return f"OracleClient(host='{self.host}', service='{self.service_name}', status='{status}')"

