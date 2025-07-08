"""
Endpoints para gerenciamento do sistema de Pagamentos
Inclui payment_providers, payment_customers, payment_methods e invoices
ATENÇÃO: Dados sensíveis de pagamento - máxima segurança
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime, date

from synapse.api.deps import get_db, get_current_user, require_admin
from synapse.models.user import User
from synapse.models.payment import (
    PaymentProvider,
    PaymentCustomer,
    PaymentMethod,
    Invoice,
)
from synapse.schemas.payment import (
    PaymentProviderCreate,
    PaymentProviderResponse,
    PaymentCustomerCreate,
    PaymentCustomerResponse,
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse,
    PaymentMethodListResponse,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    PaginatedResponse,
)

router = APIRouter()


# ===== PAYMENT PROVIDERS ENDPOINTS (APENAS SUPER ADMINS) =====


@router.get("/providers", response_model=List[PaymentProviderResponse])
async def list_payment_providers(
    db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    """
    Lista provedores de pagamento (apenas super admins)
    ATENÇÃO: Não expor configurações sensíveis
    """
    # Apenas super admins podem ver providers
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a super administradores",
        )

    providers = db.query(PaymentProvider).all()

    # Remover informações sensíveis das configurações
    safe_providers = []
    for provider in providers:
        provider_data = PaymentProviderResponse.model_validate(provider)
        # Mascarar configurações sensíveis
        if provider_data.configuration:
            provider_data.configuration = {
                "configured": True,
                "keys_count": len(provider_data.configuration),
            }
        safe_providers.append(provider_data)

    return safe_providers


@router.post(
    "/providers",
    response_model=PaymentProviderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_provider(
    provider_data: PaymentProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Cria um novo provedor de pagamento (apenas super admins)
    """
    # Apenas super admins podem criar providers
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a super administradores",
        )

    # Verificar se já existe provider com o mesmo código
    existing_provider = (
        db.query(PaymentProvider)
        .filter(PaymentProvider.code == provider_data.code)
        .first()
    )

    if existing_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provedor com este código já existe",
        )

    # Criar provider
    provider = PaymentProvider(**provider_data.model_dump())

    db.add(provider)
    db.commit()
    db.refresh(provider)

    # Retornar sem configurações sensíveis
    provider_response = PaymentProviderResponse.model_validate(provider)
    if provider_response.configuration:
        provider_response.configuration = {"configured": True}

    return provider_response


# ===== PAYMENT CUSTOMERS ENDPOINTS =====


@router.get("/customers/current", response_model=PaymentCustomerResponse)
async def get_current_customer(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Obtém customer de pagamento do tenant atual
    """
    customer = (
        db.query(PaymentCustomer)
        .filter(PaymentCustomer.tenant_id == current_user.tenant_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer de pagamento não encontrado para este tenant",
        )

    return PaymentCustomerResponse.model_validate(customer)


@router.post(
    "/customers",
    response_model=PaymentCustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_customer(
    customer_data: PaymentCustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Cria um customer de pagamento (apenas admins)
    """
    # Verificar se já existe customer para este tenant
    existing_customer = (
        db.query(PaymentCustomer)
        .filter(PaymentCustomer.tenant_id == customer_data.tenant_id)
        .first()
    )

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer já existe para este tenant",
        )

    # Verificar se o provider existe
    provider = (
        db.query(PaymentProvider)
        .filter(PaymentProvider.id == customer_data.provider_id)
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provedor de pagamento não encontrado",
        )

    # Criar customer
    customer = PaymentCustomer(**customer_data.model_dump())

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return PaymentCustomerResponse.model_validate(customer)


# ===== PAYMENT METHODS ENDPOINTS =====


@router.get("/methods", response_model=PaymentMethodListResponse)
async def list_payment_methods(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(True, description="Filtrar por métodos ativos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista métodos de pagamento do tenant atual
    """
    # Buscar customer do tenant atual
    customer = (
        db.query(PaymentCustomer)
        .filter(PaymentCustomer.tenant_id == current_user.tenant_id)
        .first()
    )

    if not customer:
        return PaymentMethodListResponse(items=[], total=0, page=1, pages=0, size=limit)

    query = db.query(PaymentMethod).filter(PaymentMethod.customer_id == customer.id)

    if is_active is not None:
        query = query.filter(PaymentMethod.is_active == is_active)

    total = query.count()
    methods = query.offset(skip).limit(limit).all()

    return PaymentMethodListResponse(
        items=[PaymentMethodResponse.model_validate(method) for method in methods],
        total=total,
        page=(skip // limit) + 1,
        pages=((total - 1) // limit) + 1 if total > 0 else 0,
        size=limit,
    )


@router.post(
    "/methods",
    response_model=PaymentMethodResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_method(
    method_data: PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Adiciona um novo método de pagamento
    ATENÇÃO: Não armazenar dados sensíveis do cartão - usar tokens do provedor
    """
    # Verificar se o customer pertence ao tenant atual
    customer = (
        db.query(PaymentCustomer)
        .filter(
            PaymentCustomer.id == method_data.customer_id,
            PaymentCustomer.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer não encontrado ou não pertence ao seu tenant",
        )

    # Se este método deve ser o padrão, desmarcar outros
    if method_data.is_default:
        db.query(PaymentMethod).filter(
            PaymentMethod.customer_id == method_data.customer_id
        ).update({"is_default": False})

    # Criar método de pagamento
    payment_method = PaymentMethod(
        **method_data.model_dump(), tenant_id=current_user.tenant_id
    )

    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)

    return PaymentMethodResponse.model_validate(payment_method)


@router.get("/methods/{method_id}", response_model=PaymentMethodResponse)
async def get_payment_method(
    method_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtém detalhes de um método de pagamento específico
    """
    method = (
        db.query(PaymentMethod)
        .filter(
            PaymentMethod.id == method_id,
            PaymentMethod.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Método de pagamento não encontrado",
        )

    return PaymentMethodResponse.model_validate(method)


@router.put("/methods/{method_id}", response_model=PaymentMethodResponse)
async def update_payment_method(
    method_id: uuid.UUID,
    method_data: PaymentMethodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Atualiza um método de pagamento
    """
    method = (
        db.query(PaymentMethod)
        .filter(
            PaymentMethod.id == method_id,
            PaymentMethod.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Método de pagamento não encontrado",
        )

    # Se este método deve ser o padrão, desmarcar outros
    if method_data.is_default:
        db.query(PaymentMethod).filter(
            PaymentMethod.customer_id == method.customer_id,
            PaymentMethod.id != method_id,
        ).update({"is_default": False})

    # Atualizar campos
    for field, value in method_data.model_dump(exclude_unset=True).items():
        setattr(method, field, value)

    db.commit()
    db.refresh(method)

    return PaymentMethodResponse.model_validate(method)


@router.delete("/methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(
    method_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove um método de pagamento
    """
    method = (
        db.query(PaymentMethod)
        .filter(
            PaymentMethod.id == method_id,
            PaymentMethod.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Método de pagamento não encontrado",
        )

    # Verificar se há subscriptions ativas usando este método
    from synapse.models.subscription import UserSubscription

    active_subscriptions = (
        db.query(UserSubscription)
        .filter(
            UserSubscription.payment_method_id == method_id,
            UserSubscription.status == "active",
        )
        .count()
    )

    if active_subscriptions > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover método usado em subscriptions ativas",
        )

    db.delete(method)
    db.commit()


# ===== INVOICES ENDPOINTS =====


@router.get("/invoices", response_model=InvoiceListResponse)
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    start_date: Optional[date] = Query(None, description="Data de início"),
    end_date: Optional[date] = Query(None, description="Data de fim"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista faturas do tenant atual
    """
    query = db.query(Invoice).filter(Invoice.tenant_id == current_user.tenant_id)

    if status:
        query = query.filter(Invoice.status == status)

    if start_date:
        query = query.filter(Invoice.created_at >= start_date)

    if end_date:
        query = query.filter(Invoice.created_at <= end_date)

    # Ordenar por data de criação descendente
    query = query.order_by(Invoice.created_at.desc())

    total = query.count()
    invoices = query.offset(skip).limit(limit).all()

    return InvoiceListResponse(
        items=[InvoiceResponse.model_validate(invoice) for invoice in invoices],
        total=total,
        page=(skip // limit) + 1,
        pages=((total - 1) // limit) + 1 if total > 0 else 0,
        size=limit,
    )


@router.post(
    "/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED
)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Cria uma nova fatura (apenas admins)
    """
    # Verificar se o tenant corresponde ao usuário atual ou se é super admin
    if (
        invoice_data.tenant_id != current_user.tenant_id
        and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível criar fatura para outro tenant",
        )

    # Verificar se o invoice_number é único
    existing_invoice = (
        db.query(Invoice)
        .filter(
            Invoice.invoice_number == invoice_data.invoice_number,
            Invoice.tenant_id == invoice_data.tenant_id,
        )
        .first()
    )

    if existing_invoice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de fatura já existe para este tenant",
        )

    # Criar fatura
    invoice = Invoice(**invoice_data.model_dump())

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return InvoiceResponse.model_validate(invoice)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtém detalhes de uma fatura específica
    """
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fatura não encontrada"
        )

    return InvoiceResponse.model_validate(invoice)


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: uuid.UUID,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Atualiza uma fatura (apenas admins)
    """
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fatura não encontrada"
        )

    # Não permitir edição de faturas pagas
    if invoice.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível editar fatura já paga",
        )

    # Atualizar campos
    for field, value in invoice_data.model_dump(exclude_unset=True).items():
        setattr(invoice, field, value)

    # Se está marcando como paga, definir data de pagamento
    if invoice_data.status == "paid" and not invoice.paid_at:
        invoice.paid_at = datetime.utcnow()

    db.commit()
    db.refresh(invoice)

    return InvoiceResponse.model_validate(invoice)


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Remove uma fatura (apenas admins)
    """
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fatura não encontrada"
        )

    # Não permitir remoção de faturas pagas
    if invoice.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover fatura paga",
        )

    db.delete(invoice)
    db.commit()


# ===== UTILITY ENDPOINTS =====


@router.get("/invoices/{invoice_id}/download")
async def download_invoice_pdf(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gera e baixa PDF da fatura
    TODO: Implementar geração de PDF
    """
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fatura não encontrada"
        )

    # TODO: Implementar geração de PDF da fatura
    return {
        "message": "Funcionalidade de PDF em desenvolvimento",
        "invoice_number": invoice.invoice_number,
    }


@router.post("/invoices/{invoice_id}/pay")
async def pay_invoice(
    invoice_id: uuid.UUID,
    payment_method_id: Optional[uuid.UUID] = Query(
        None, description="ID do método de pagamento"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Processa pagamento de uma fatura
    TODO: Integrar com provedor de pagamento
    """
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fatura não encontrada"
        )

    if invoice.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Fatura já foi paga"
        )

    # Verificar método de pagamento se fornecido
    if payment_method_id:
        payment_method = (
            db.query(PaymentMethod)
            .filter(
                PaymentMethod.id == payment_method_id,
                PaymentMethod.tenant_id == current_user.tenant_id,
                PaymentMethod.is_active == True,
            )
            .first()
        )

        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Método de pagamento não encontrado ou inativo",
            )

    # TODO: Integrar com provedor de pagamento (Stripe, PayPal, etc.)
    # Por enquanto, apenas simular o pagamento

    invoice.status = "paid"
    invoice.paid_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Pagamento processado com sucesso (simulado)",
        "invoice_id": invoice_id,
        "amount": invoice.total_amount,
        "paid_at": invoice.paid_at,
    }
