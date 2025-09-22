from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date
import logging
import atexit

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SorteioScheduler:
    """Classe responsável pelo agendamento automático dos sorteios"""
    
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o scheduler com a aplicação Flask"""
        self.app = app
        
        # Configura o scheduler para executar o sorteio diariamente às 20:00
        self.scheduler.add_job(
            func=self.executar_sorteio_diario,
            trigger=CronTrigger(hour=20, minute=0),  # 20:00 todos os dias
            id='sorteio_diario',
            name='Sorteio Diário às 20:00',
            replace_existing=True
        )
        
        # Inicia o scheduler
        self.scheduler.start()
        logger.info("Scheduler de sorteios iniciado - Sorteio diário às 20:00")
        
        # Garante que o scheduler seja finalizado quando a aplicação for fechada
        atexit.register(lambda: self.scheduler.shutdown())
    
    def executar_sorteio_diario(self):
        """Executa o sorteio diário automaticamente"""
        try:
            with self.app.app_context():
                from src.models.sorteio import Sorteio
                from src.models.database import db
                
                logger.info(f"Iniciando sorteio automático - {datetime.now()}")
                
                # Pega o sorteio de hoje
                sorteio = Sorteio.get_sorteio_atual()
                
                if sorteio.status != 'aberto':
                    logger.warning(f"Sorteio do dia {sorteio.data_sorteio} não está aberto. Status: {sorteio.status}")
                    return
                
                # Realiza o sorteio
                if sorteio.realizar_sorteio():
                    logger.info(f"Sorteio realizado! Número sorteado: {sorteio.numero_sorteado}")
                    
                    # Finaliza o sorteio (distribui prêmios)
                    if sorteio.finalizar_sorteio():
                        apostas_ganhadoras = sorteio.get_apostas_ganhadoras()
                        logger.info(f"Sorteio finalizado! {len(apostas_ganhadoras)} ganhadores")
                        
                        if apostas_ganhadoras:
                            premio_por_ganhador = sorteio.premio_total / len(apostas_ganhadoras)
                            logger.info(f"Prêmio por ganhador: R$ {premio_por_ganhador:.2f}")
                        else:
                            logger.info("Nenhum ganhador neste sorteio")
                    else:
                        logger.error("Erro ao finalizar o sorteio")
                else:
                    logger.error("Erro ao realizar o sorteio")
                    
        except Exception as e:
            logger.error(f"Erro durante execução do sorteio automático: {str(e)}")
    
    def executar_sorteio_manual(self, data_sorteio=None):
        """Executa um sorteio manualmente (para testes ou casos especiais)"""
        try:
            with self.app.app_context():
                from src.models.sorteio import Sorteio
                from src.models.database import db
                
                if data_sorteio is None:
                    data_sorteio = date.today()
                
                logger.info(f"Iniciando sorteio manual para {data_sorteio}")
                
                # Busca ou cria o sorteio para a data especificada
                sorteio = Sorteio.query.filter_by(data_sorteio=data_sorteio).first()
                
                if not sorteio:
                    sorteio = Sorteio(data_sorteio=data_sorteio)
                    db.session.add(sorteio)
                    db.session.commit()
                
                if sorteio.status != 'aberto':
                    logger.warning(f"Sorteio do dia {sorteio.data_sorteio} não está aberto. Status: {sorteio.status}")
                    return False
                
                # Realiza o sorteio
                if sorteio.realizar_sorteio():
                    logger.info(f"Sorteio manual realizado! Número sorteado: {sorteio.numero_sorteado}")
                    
                    # Finaliza o sorteio
                    if sorteio.finalizar_sorteio():
                        apostas_ganhadoras = sorteio.get_apostas_ganhadoras()
                        logger.info(f"Sorteio manual finalizado! {len(apostas_ganhadoras)} ganhadores")
                        return True
                    else:
                        logger.error("Erro ao finalizar o sorteio manual")
                        return False
                else:
                    logger.error("Erro ao realizar o sorteio manual")
                    return False
                    
        except Exception as e:
            logger.error(f"Erro durante execução do sorteio manual: {str(e)}")
            return False
    
    def get_proximo_sorteio(self):
        """Retorna informações sobre o próximo sorteio agendado"""
        job = self.scheduler.get_job('sorteio_diario')
        if job:
            return {
                'proximo_sorteio': job.next_run_time.isoformat() if job.next_run_time else None,
                'status': 'ativo' if self.scheduler.running else 'parado'
            }
        return None
    
    def parar_scheduler(self):
        """Para o scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler de sorteios parado")
    
    def reiniciar_scheduler(self):
        """Reinicia o scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler de sorteios reiniciado")

# Instância global do scheduler
sorteio_scheduler = SorteioScheduler()

