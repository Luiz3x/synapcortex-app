# =================================================================================
# SYNAPCORTEX - ARQUIVO DE MODELOS DO BANCO DE DADOS (v3.0 - Final)
# A planta baixa de todos os dados da nossa aplicação.
# Define a estrutura das tabelas AppUser, AnalyticsEvent e PaymentEvent.
# =================================================================================

from __future__ import annotations
import datetime
from typing import Dict, Any, List, Optional

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, UniqueConstraint

# A instância do db é criada em `extensions.py` e inicializada em `__init__.py`
# Aqui, apenas a importamos para usar nos modelos.
from .extensions import db

class SubscriptionStatus:
    """
    Centraliza os status da assinatura para evitar erros de digitação (magic strings)
    e facilitar a manutenção do código.
    """
    ACTIVE = 'active'
    TRIAL = 'trial'
    PAST_DUE = 'past_due' # Adicionado para falhas de pagamento
    CANCELED = 'canceled'
    DEMO = 'demo'
    
    # 'frozenset' é ideal para um conjunto de constantes imutáveis e de alta performance.
    VALID_STATUSES = frozenset({ACTIVE, TRIAL, DEMO})


class AppUser(db.Model, UserMixin):
    """
    Representa uma conta de cliente (uma empresa) na plataforma SynapCortex.
    Herda de UserMixin para integração nativa com Flask-Login.
    """
    __tablename__ = 'app_user'

    # --- Colunas da Tabela ---
    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    api_key: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    
    # --- Colunas de Assinatura (Stripe) ---
    subscription_status: Mapped[str] = mapped_column(String(20), default=SubscriptionStatus.TRIAL)
    trial_end_date: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(120), unique=True, nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(120), unique=True, nullable=True)

    # --- Colunas de Configuração (JSON) ---
    settings: Mapped[Dict[str, Any]] = mapped_column(db.JSON, default=lambda: {})
    campaign_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(db.JSON, nullable=True, default=lambda: {})
    is_campaign_active: Mapped[bool] = mapped_column(default=False)
    campaign_start_date: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True)
    campaign_end_date: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True)

    # --- Relações ---
    events: Mapped[List["AnalyticsEvent"]] = relationship(
        back_populates="owner", lazy="dynamic", cascade="all, delete-orphan"
    )

    # --- Propriedades (Lógica de Negócio) ---
    @property
    def is_trial_active(self) -> bool:
        """Verifica se o período de teste do usuário ainda está ativo."""
        return (self.subscription_status == SubscriptionStatus.TRIAL and
                self.trial_end_date and
                datetime.datetime.utcnow() < self.trial_end_date)

    @property
    def is_subscription_valid(self) -> bool:
        """Centraliza a lógica principal de validação de acesso ao painel."""
        return self.subscription_status in SubscriptionStatus.VALID_STATUSES or self.is_trial_active

    def __repr__(self) -> str:
        """Representação textual do objeto, útil para depuração."""
        return f"<AppUser id={self.id} email='{self.email}' status='{self.subscription_status}'>"


class AnalyticsEvent(db.Model):
    """
    Representa um único evento de rastreamento coletado (ex: page_view, add_to_cart).
    """
    __tablename__ = 'analytics_event'

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('app_user.id'), index=True)
    visitor_id: Mapped[str] = mapped_column(String(100), index=True)
    event_name: Mapped[str] = mapped_column(String(50), index=True)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(db.JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True)

    # --- Relações ---
    owner: Mapped["AppUser"] = relationship(back_populates="events")

    def __repr__(self) -> str:
        """Representação textual do objeto para depuração."""
        return f"<AnalyticsEvent id={self.id} owner_id={self.owner_id} name='{self.event_name}'>"


class PaymentEvent(db.Model):
    """
    Armazena um registro de cada evento de webhook recebido do Stripe.
    Serve como um livro-caixa para auditoria e depuração.
    """
    __tablename__ = 'payment_event'

    id: Mapped[int] = mapped_column(primary_key=True)
    stripe_event_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(255), index=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(db.JSON)
    status: Mapped[str] = mapped_column(String(50), default='received', index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PaymentEvent id={self.id} stripe_event_id='{self.stripe_event_id}' status='{self.status}'>"