#!/usr/bin/env python3
"""
AvertaSaaS - Comprehensive Database Seed Script

Populates database with:
1. Admin user (admin@admin / admin)
2. Test companies, clients, carriers, branches
4. Contracts with freight tables
5. Documents (CTe, NFe) with discrepancies
6. Contests with items, communications, payments
7. Rules engine data
8. Notifications, audit logs

Usage:
    python prisma/seed.py
    or
    poetry run python prisma/seed.py
"""

import asyncio
import random
from datetime import datetime, timedelta

from passlib.context import CryptContext

from generated.prisma import Prisma

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =============================================================================
# CONFIGURATION
# =============================================================================

# Scale multipliers - adjust for performance testing
# DOUBLED for performance testing (original values in comments)
SCALE = {
    "companies": 10,              # was 5
    "clients_per_company": 20,    # was 10
    "carriers_per_company": 16,   # was 8
    "branches_per_client": 6,     # was 3
    "contracts_per_client": 4,    # was 2
    "documents_per_client": 100,  # was 50 - 100 docs per client = 20,000 total at scale
    "discrepancies_per_document": 6,  # was 3
    "contests_per_client": 10,    # was 5
    "contest_items_per_contest": 8,   # was 4
}

# Password for all test users (including admin)
DEFAULT_PASSWORD = "Incorreta1@"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def random_date(start: datetime, end: datetime) -> datetime:
    """Generate a random date between start and end."""
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))


def random_cnpj() -> str:
    """Generate a random valid CNPJ (Brazilian company ID)."""
    # Generate 12 random digits
    digits = [random.randint(0, 9) for _ in range(12)]

    # Calculate first check digit
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum1 = sum(d * w for d, w in zip(digits, weights1, strict=False))
    digit1 = 11 - (sum1 % 11)
    if digit1 >= 10:
        digit1 = 0
    digits.append(digit1)

    # Calculate second check digit
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum2 = sum(d * w for d, w in zip(digits, weights2, strict=False))
    digit2 = 11 - (sum2 % 11)
    if digit2 >= 10:
        digit2 = 0
    digits.append(digit2)

    # Format as XX.XXX.XXX/XXXX-XX
    cnpj = "".join(map(str, digits))
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def random_nfe_key() -> str:
    """Generate a random NFe access key (44 digits)."""
    return "".join(str(random.randint(0, 9)) for _ in range(44))


def random_cte_key() -> str:
    """Generate a random CTe access key (44 digits)."""
    return "".join(str(random.randint(0, 9)) for _ in range(44))


# =============================================================================
# SEED DATA DEFINITIONS
# =============================================================================

# Brazilian states for addresses
STATES = [
    "SP",
    "RJ",
    "MG",
    "RS",
    "PR",
    "SC",
    "BA",
    "GO",
    "PE",
    "CE",
    "PA",
    "MA",
    "MT",
    "MS",
    "ES",
    "PB",
    "RN",
    "AL",
    "PI",
    "SE",
]

CITIES_BY_STATE = {
    "SP": ["São Paulo", "Campinas", "Santos", "Ribeirão Preto", "São José dos Campos"],
    "RJ": ["Rio de Janeiro", "Niterói", "Petrópolis", "Volta Redonda", "Campos dos Goytacazes"],
    "MG": ["Belo Horizonte", "Uberlândia", "Contagem", "Juiz de Fora", "Betim"],
    "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Canoas", "Santa Maria"],
    "PR": ["Curitiba", "Londrina", "Maringá", "Ponta Grossa", "Cascavel"],
    "SC": ["Florianópolis", "Joinville", "Blumenau", "São José", "Criciúma"],
    "BA": ["Salvador", "Feira de Santana", "Vitória da Conquista", "Camaçari", "Itabuna"],
    "GO": ["Goiânia", "Aparecida de Goiânia", "Anápolis", "Rio Verde", "Águas Lindas"],
    "PE": ["Recife", "Jaboatão dos Guararapes", "Olinda", "Caruaru", "Petrolina"],
    "CE": ["Fortaleza", "Caucaia", "Juazeiro do Norte", "Maracanaú", "Sobral"],
}

# Document types and statuses
DOCUMENT_TYPES = ["CTE", "NFE", "CTE_COMPLEMENTAR", "NFE_COMPLEMENTAR"]
DOCUMENT_STATUSES = ["UPLOADED", "PENDING", "PROCESSING", "COMPLETED", "FAILED", "ARCHIVED"]

# Discrepancy types and statuses
DISCREPANCY_TYPES = [
    "ICMS_DIFFERENTIAL",
    "ICMS_FCP",
    "ICMS_ST",
    "FREIGHT_WEIGHT_VALUE",
    "FREIGHT_CUBAGE",
    "REDESPACHO",
    "TOLL_PLAZA",
    "AD_VALOREM",
    "GRIS",
    "SICOBAN_TABLE",
    "COMPLEMENTARY_CTE",
    "PESO_REAL_VS_FATURADO",
    "VALOR_MINIMO_FRETE",
    "OTHER",
]
DISCREPANCY_STATUSES = [
    "DETECTED",
    "OPEN",
    "IN_REVIEW",
    "CONTESTED",
    "APPROVED",
    "REJECTED",
    "PAID",
    "CLOSED",
]
DISCREPANCY_SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Contest statuses
CONTEST_STATUSES = [
    "DRAFT",
    "SENT",
    "ACKNOWLEDGED",
    "NEGOTIATING",
    "ACCEPTED",
    "PARTIAL",
    "REJECTED",
    "EXPIRED",
]

# Notification types
NOTIFICATION_TYPES = [
    "DISCREPANCY_FOUND",
    "CONTEST_APPROVED",
    "CONTEST_SENT",
    "CONTEST_RESPONSE",
    "RECOVERY_CONFIRMED",
    "WEEKLY_REPORT",
    "SYSTEM_ALERT",
    "CONTRACT_EXPIRING",
    "WELCOME",
    "PASSWORD_RESET",
]

# =============================================================================
# MAIN SEED FUNCTION
# =============================================================================


async def seed_database():
    """Main seeding function."""

    prisma = Prisma()
    await prisma.connect()

    try:
        # Clear existing data (optional - comment out to preserve)
        await clear_database(prisma)

        # 1. Create admin user
        admin_user = await create_admin_user(prisma)

        # 2. Create companies with full hierarchy
        await create_companies(prisma, admin_user)

        # 3. Create rules
        await create_rules(prisma)


    except Exception:
        raise
    finally:
        await prisma.disconnect()


async def clear_database(prisma: Prisma):
    """Clear all data from database (in correct order due to FK constraints)."""
    tables = [
        "Payment",
        "Communication",
        "ContestItem",
        "Contest",
        "Discrepancy",
        "Document",
        "FreightTable",
        "Contract",
        "Branch",
        "Carrier",
        "Client",
        "Notification",
        "AuditLog",
        "User",
        "Company",
        "Rule",
        "SystemConfig",
    ]
    for table in tables:
        try:
            await prisma.execute_raw(f'TRUNCATE TABLE "{table}" CASCADE')
        except Exception:
            pass  # Table might not exist or be empty


async def create_admin_user(prisma: Prisma):
    """Create the admin@admin user."""
    # Create a default company for admin if needed
    admin_company = await prisma.company.create(
        data={
            "name": "Averta Admin",
            "tradeName": "Averta Admin",
            "cnpj": "00.000.000/0001-00",
            "email": "admin@averta.com.br",
            "isActive": True,
            "settings": {"is_admin_company": True},
        }
    )

    admin_user = await prisma.user.create(
        data={
            "email": "admin@admin",
            "passwordHash": hash_password(DEFAULT_PASSWORD),
            "fullName": "Admin User",
            "role": "ADMIN",
            "status": "ACTIVE",
            "companyId": admin_company.id,
            "lastLoginAt": datetime.now(),
        }
    )

    return admin_user


async def create_companies(prisma: Prisma, admin_user) -> list:
    """Create companies with full hierarchy."""
    companies = []

    for i in range(SCALE["companies"]):
        state = random.choice(STATES)
        city = random.choice(CITIES_BY_STATE[state])

        company = await prisma.company.create(
            data={
                "name": f"Empresa {i + 1:03d} Ltda",
                "tradeName": f"Empresa {i + 1:03d}",
                "cnpj": random_cnpj(),
                "stateReg": f"{random.randint(100000000, 999999999)}",
                "municipalReg": f"{random.randint(100000, 999999)}",
                "address": {
                    "street": f"Rua {random.randint(1, 999)}",
                    "number": str(random.randint(1, 9999)),
                    "complement": f"Sala {random.randint(1, 50)}",
                    "neighborhood": "Centro",
                    "city": city,
                    "state": state,
                    "zipCode": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                    "country": "Brasil",
                },
                "phone": f"(11) {random.randint(2000, 9999)}-{random.randint(1000, 9999)}",
                "email": f"contato@empresa{i + 1:03d}.com.br",
                "website": f"https://empresa{i + 1:03d}.com.br",
                "isActive": True,
                "settings": {
                    "notificationEmail": f"notificacoes@empresa{i + 1:03d}.com.br",
                    "currency": "BRL",
                    "timezone": "America/Sao_Paulo",
                },
            }
        )
        companies.append(company)

        # Create users for this company
        await create_company_users(prisma, company, admin_user)

        # Create clients
        clients = await create_clients(prisma, company)

        # Create carriers
        carriers = await create_carriers(prisma, company)

        # Create branches
        branches = await create_branches(prisma, company, clients)

        # Create contracts
        contracts = await create_contracts(prisma, company, clients, carriers)

        # Create documents, discrepancies, contests
        await create_documents_and_discrepancies(
            prisma, company, clients, carriers, contracts, branches
        )
        await create_contests(prisma, company, clients, carriers, contracts)

        # Create notifications and audit logs
        await create_notifications(prisma, company, clients)
        await create_audit_logs(prisma, company, admin_user)


    return companies


async def create_company_users(prisma: Prisma, company, admin_user):
    """Create users for a company."""
    roles = ["MANAGER", "AUDITOR", "CLIENT", "CLIENT"]

    for i, role in enumerate(roles):
        await prisma.user.create(
            data={
                "email": f"user{i + 1}@{company.cnpj.replace('.', '').replace('/', '').replace('-', '')}.com.br",
                "passwordHash": hash_password(DEFAULT_PASSWORD),
                "fullName": f"User {i + 1} - {role}",
                "role": role,
                "status": "ACTIVE",
                "companyId": company.id,
                "lastLoginAt": datetime.now() - timedelta(days=random.randint(0, 30)),
            }
        )


async def create_clients(prisma: Prisma, company) -> list:
    """Create clients for a company."""
    clients = []

    for i in range(SCALE["clients_per_company"]):
        state = random.choice(STATES)
        city = random.choice(CITIES_BY_STATE[state])

        client = await prisma.client.create(
            data={
                "companyId": company.id,
                "name": f"Cliente {i + 1:03d} - {company.name}",
                "tradeName": f"Cliente {i + 1:03d}",
                "cnpj": random_cnpj(),
                "stateReg": f"{random.randint(100000000, 999999999)}",
                "email": f"financeiro@cliente{i + 1:03d}.com.br",
                "phone": f"(11) {random.randint(2000, 9999)}-{random.randint(1000, 9999)}",
                "address": {
                    "street": f"Av. {random.randint(1, 999)}",
                    "number": str(random.randint(1, 9999)),
                    "neighborhood": "Comercial",
                    "city": city,
                    "state": state,
                    "zipCode": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                    "country": "Brasil",
                },
                "contactPerson": f"Contato {i + 1}",
                "contactEmail": f"contato@cliente{i + 1:03d}.com.br",
                "contactPhone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "isActive": True,
                "settings": {
                    "paymentTerms": random.randint(15, 60),
                    "preferredCarrier": None,
                },
            }
        )
        clients.append(client)

    return clients


async def create_carriers(prisma: Prisma, company) -> list:
    """Create carriers for a company."""
    carriers = []

    carrier_names = [
        "Transportes Rápidos Ltda",
        "Logística Express S.A.",
        "Cargas & Cia Transportes",
        "Rodovias do Brasil Ltda",
        "Frete Fácil Transportes",
        "Estrada Livre Logística",
        "Caminho Certo Transportes",
        "Via Rápida Cargas",
        "Transporte Total S.A.",
        "Carga Viva Logística",
        "Rota Segura Transportes",
        "Entrega Certa Ltda",
    ]

    for i in range(SCALE["carriers_per_company"]):
        state = random.choice(STATES)
        city = random.choice(CITIES_BY_STATE[state])
        name = random.choice(carrier_names)

        carrier = await prisma.carrier.create(
            data={
                "companyId": company.id,
                "name": f"{name} {i + 1}",
                "tradeName": f"{name} {i + 1}",
                "cnpj": random_cnpj(),
                "stateReg": f"{random.randint(100000000, 999999999)}",
                "address": {
                    "street": f"Rodovia {random.randint(1, 999)}",
                    "number": str(random.randint(1, 9999)),
                    "neighborhood": "Industrial",
                    "city": city,
                    "state": state,
                    "zipCode": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                    "country": "Brasil",
                },
                "contactPerson": f"Gerente {i + 1}",
                "contactEmail": f"contato@carrier{i + 1:03d}.com.br",
                "contactPhone": f"(11) {random.randint(2000, 9999)}-{random.randint(1000, 9999)}",
                "bankInfo": {
                    "bank": random.choice(["001", "237", "341", "104", "033"]),
                    "agency": f"{random.randint(1000, 9999)}",
                    "account": f"{random.randint(10000, 99999)}-{random.randint(0, 9)}",
                    "pix": f"carrier{i + 1:03d}@carrier.com.br",
                },
                "settings": {
                    "fleetSize": random.randint(10, 200),
                    "coverageStates": random.sample(STATES, random.randint(3, 10)),
                    "specializations": random.sample(
                        ["Carga Seca", "Carga Fria", "Carga Perigosa", "Granéis", "Containers"],
                        random.randint(1, 3),
                    ),
                },
                "isActive": True,
            }
        )
        carriers.append(carrier)

    return carriers


async def create_branches(prisma: Prisma, company, clients) -> list:
    """Create branches for a company."""
    branches = []

    for client in clients:
        for _i in range(SCALE["branches_per_client"]):
            state = random.choice(STATES)
            city = random.choice(CITIES_BY_STATE[state])

            branch = await prisma.branch.create(
                data={
                    "companyId": company.id,
                    "clientId": client.id,
                    "name": f"Filial {client.name} - {city}",
                    "code": f"FL{random.randint(100, 999)}",
                    "cnpj": random_cnpj() if random.random() > 0.3 else None,
                    "address": {
                        "street": f"Rua {random.randint(1, 999)}",
                        "number": str(random.randint(1, 9999)),
                        "neighborhood": random.choice(
                            ["Centro", "Comercial", "Industrial", "Residencial"]
                        ),
                        "city": city,
                        "state": state,
                        "zipCode": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                        "country": "Brasil",
                    },
                    "isActive": True,
                }
            )
            branches.append(branch)

    return branches


async def create_contracts(prisma: Prisma, company, clients, carriers) -> list:
    """Create contracts for a company."""
    contracts = []

    for client in clients:
        for i in range(SCALE["contracts_per_client"]):
            carrier = random.choice(carriers)
            start_date = datetime.now() - timedelta(days=random.randint(0, 365))
            end_date = start_date + timedelta(days=random.randint(180, 730))

            contract = await prisma.contract.create(
                data={
                    "companyId": company.id,
                    "clientId": client.id,
                    "carrierId": carrier.id,
                    "number": f"CTR-{company.id[:8]}-{client.id[:8]}-{i + 1:03d}",
                    "description": f"Contrato de transporte {client.name} x {carrier.name}",
                    "status": random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "PENDING", "EXPIRED"]),
                    "startDate": start_date,
                    "endDate": end_date if random.random() > 0.2 else None,
                    "successFeePct": round(random.uniform(15.0, 30.0), 2),
                    "minRecovery": round(random.uniform(100.0, 10000.0), 2)
                    if random.random() > 0.5
                    else None,
                    "currency": "BRL",
                    "terms": {
                        "paymentTerms": random.randint(15, 60),
                        "slaDays": random.randint(1, 5),
                        "penaltyPct": round(random.uniform(0.5, 2.0), 2),
                    },
                    "pricingModel": random.choice(["FIXED", "PROGRESSIVE"]),
                    "progressiveStartDate": start_date if random.random() > 0.7 else None,
                    "progressiveMonth1Pct": round(random.uniform(5.0, 15.0), 2)
                    if random.random() > 0.7
                    else None,
                    "progressiveMonth2Pct": round(random.uniform(10.0, 25.0), 2)
                    if random.random() > 0.7
                    else None,
                }
            )
            contracts.append(contract)

            # Create freight tables for this contract
            await create_freight_tables(prisma, contract)

    return contracts


async def create_freight_tables(prisma: Prisma, contract):
    """Create freight tables for a contract."""
    num_tables = random.randint(1, 3)

    for i in range(num_tables):
        effective_from = contract.startDate + timedelta(days=random.randint(0, 30))

        await prisma.freight_table.create(
            data={
                "contractId": contract.id,
                "name": f"Tabela {i + 1} - {contract.number}",
                "version": f"v{i + 1}.0",
                "effectiveFrom": effective_from,
                "effectiveTo": contract.endDate,
                "description": f"Tabela de frete para contrato {contract.number}",
                "rules": {
                    "baseRate": round(random.uniform(1.5, 5.0), 2),
                    "perKm": round(random.uniform(0.5, 2.0), 2),
                    "perKg": round(random.uniform(0.05, 0.50), 2),
                    "minCharge": round(random.uniform(50.0, 200.0), 2),
                    "icmsIncluded": random.choice([True, False]),
                    "tollsIncluded": random.choice([True, False]),
                },
                "isActive": True,
            }
        )


async def create_documents_and_discrepancies(
    prisma: Prisma, company, clients, carriers, contracts, branches
):
    """Create documents with discrepancies."""
    for client in clients:
        client_contracts = [c for c in contracts if c.clientId == client.id]
        client_branches = [b for b in branches if b.clientId == client.id]
        client_carriers = carriers  # All carriers can serve this client

        for _ in range(SCALE["documents_per_client"]):
            contract = random.choice(client_contracts) if client_contracts else None
            carrier = random.choice(client_carriers)
            branch = random.choice(client_branches) if client_branches else None

            doc_type = random.choice(DOCUMENT_TYPES)
            status = random.choices(DOCUMENT_STATUSES, weights=[5, 10, 10, 60, 10, 5])[0]

            issue_date = datetime.now() - timedelta(days=random.randint(0, 365))
            created_at = issue_date + timedelta(days=random.randint(0, 5))

            total_value = round(random.uniform(1000.0, 100000.0), 2)
            freight_value = round(total_value * random.uniform(0.05, 0.25), 2)
            icms_value = round(total_value * random.uniform(0.12, 0.18), 2)

            document = await prisma.document.create(
                data={
                    "companyId": company.id,
                    "clientId": client.id,
                    "branchId": branch.id if branch else None,
                    "carrierId": carrier.id,
                    "contractId": contract.id if contract else None,
                    "type": doc_type,
                    "status": status,
                    "originalName": f"{doc_type}_{client.name}_{issue_date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}.xml",
                    "storedName": f"docs/{company.id}/{client.id}/{doc_type.lower()}_{issue_date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}.xml",
                    "s3Key": f"docs/{company.id}/{client.id}/{doc_type.lower()}_{issue_date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}.xml",
                    "s3Bucket": "averta-documents",
                    "mimeType": "application/xml",
                    "fileSize": random.randint(10000, 5000000),
                    "accessKey": random_nfe_key()
                    if doc_type in ["NFE", "NFE_COMPLEMENTAR"]
                    else random_cte_key(),
                    "issueDate": issue_date,
                    "totalValue": total_value,
                    "freightValue": freight_value,
                    "icmsValue": icms_value,
                    "weight": round(random.uniform(100.0, 50000.0), 2),
                    "volume": round(random.uniform(1.0, 100.0), 2),
                    "createdAt": created_at,
                    "processedAt": created_at + timedelta(hours=random.randint(1, 24))
                    if status == "COMPLETED"
                    else None,
                    "processingTime": random.randint(1000, 60000)
                    if status == "COMPLETED"
                    else None,
                }
            )

            # Create discrepancies for this document
            if status in ["COMPLETED", "PROCESSING"]:
                num_discrepancies = random.randint(0, SCALE["discrepancies_per_document"])
                for _ in range(num_discrepancies):
                    await create_discrepancy(
                        prisma, document, company, client, carrier, contract, branch
                    )


async def create_discrepancy(prisma: Prisma, document, company, client, carrier, contract, branch):
    """Create a discrepancy for a document."""
    disc_type = random.choice(DISCREPANCY_TYPES)
    status = random.choices(DISCREPANCY_STATUSES, weights=[10, 20, 15, 15, 15, 10, 10, 5])[0]

    expected = round(random.uniform(100.0, 50000.0), 2)
    actual = round(expected * random.uniform(0.7, 1.3), 2)
    difference = round(actual - expected, 2)
    difference_pct = round((difference / expected) * 100, 2) if expected > 0 else 0

    (
        "CRITICAL"
        if abs(difference_pct) > 20
        else "HIGH"
        if abs(difference_pct) > 10
        else "MEDIUM"
        if abs(difference_pct) > 5
        else "LOW"
    )

    # Get a rule code for this type
    rule_codes = {
        "ICMS_DIFFERENTIAL": "NFE-001",
        "ICMS_FCP": "NFE-002",
        "ICMS_ST": "NFE-003",
        "FREIGHT_WEIGHT_VALUE": "CTE-001",
        "FREIGHT_CUBAGE": "CTE-002",
        "REDESPACHO": "CTE-003",
        "TOLL_PLAZA": "CTE-004",
        "AD_VALOREM": "CTE-005",
        "GRIS": "CTE-006",
        "SICOBAN_TABLE": "CTE-007",
        "COMPLEMENTARY_CTE": "CTE-008",
        "PESO_REAL_VS_FATURADO": "CTE-009",
        "VALOR_MINIMO_FRETE": "CTE-010",
    }

    await prisma.discrepancy.create(
        data={
            "companyId": company.id,
            "clientId": client.id,
            "branchId": branch.id if branch else None,
            "carrierId": carrier.id,
            "contractId": contract.id if contract else None,
            "documentId": document.id,
            "type": disc_type,
            "status": status,
            "ruleCode": rule_codes.get(disc_type, "NFE-999"),
            "ruleVersion": 1,
            "ruleDescription": f"Regra de validação para {disc_type.replace('_', ' ').title()}",
            "expectedValue": expected,
            "actualValue": actual,
            "difference": difference,
            "differencePct": difference_pct,
            "currency": "BRL",
            "details": {
                "calculationMethod": "Automated",
                "referenceTable": f"Tabela {random.randint(1, 5)}",
                "notes": "Gerado automaticamente pelo seed",
            },
            "evidence": {
                "xmlFields": ["vBC", "vICMS", "vFrete"],
                "comparison": "Sistema vs Documento",
            },
            "notes": f"Discrepância detectada automaticamente - {disc_type}",
            "createdAt": document.createdAt + timedelta(hours=random.randint(1, 48)),
        }
    )


async def create_contests(prisma: Prisma, company, clients, carriers, contracts):
    """Create contests for a company."""
    for client in clients:
        client_discrepancies = await prisma.discrepancy.find_many(
            where={"clientId": client.id, "status": {"in": ["DETECTED", "OPEN", "IN_REVIEW"]}},
            take=SCALE["contests_per_client"] * SCALE["contest_items_per_contest"],
        )

        if not client_discrepancies:
            continue

        for _ in range(SCALE["contests_per_client"]):
            carrier = random.choice(carriers)
            client_contracts = [
                c for c in contracts if c.clientId == client.id and c.carrierId == carrier.id
            ]
            contract = random.choice(client_contracts) if client_contracts else None

            # Select discrepancies for this contest
            available_discs = [d for d in client_discrepancies if d.carrierId == carrier.id]
            if not available_discs:
                continue

            num_items = min(SCALE["contest_items_per_contest"], len(available_discs))
            selected_discs = random.sample(available_discs, num_items)

            total_expected = sum(d.expectedValue for d in selected_discs)
            success_fee_pct = contract.successFeePct if contract else 20.0

            contest = await prisma.contest.create(
                data={
                    "companyId": company.id,
                    "clientId": client.id,
                    "carrierId": carrier.id,
                    "contractId": contract.id if contract else None,
                    "number": f"CON-{company.id[:8]}-{client.id[:8]}-{random.randint(1000, 9999)}",
                    "status": random.choice(CONTEST_STATUSES),
                    "totalExpected": total_expected,
                    "totalRecovered": 0,
                    "successFeePct": success_fee_pct,
                    "successFeeValue": round(total_expected * success_fee_pct / 100, 2),
                    "netRecovery": round(total_expected * (1 - success_fee_pct / 100), 2),
                    "notes": f"Contestação automática para {client.name} vs {carrier.name}",
                    "metadata": {
                        "createdBy": "seed",
                        "priority": random.choice(["NORMAL", "HIGH", "URGENT"]),
                    },
                    "createdAt": datetime.now() - timedelta(days=random.randint(0, 90)),
                }
            )

            # Create contest items
            for disc in selected_discs:
                await prisma.contest_item.create(
                    data={
                        "contestId": contest.id,
                        "discrepancyId": disc.id,
                        "expectedValue": disc.expectedValue,
                        "contestedValue": round(disc.expectedValue * random.uniform(0.8, 1.2), 2),
                        "recoveredValue": 0,
                        "status": contest.status,
                        "notes": f"Item de contestação para discrepância {disc.ruleCode}",
                    }
                )

            # Create communications
            await create_communications(prisma, contest)

            # Create payments if resolved
            if contest.status in ["ACCEPTED", "PARTIAL", "PAID"]:
                await create_payments(prisma, contest)


async def create_communications(prisma: Prisma, contest):
    """Create communications for a contest."""
    comm_types = ["EMAIL", "LETTER", "PHONE", "MEETING", "WHATSAPP"]
    directions = ["SENT", "RECEIVED"]

    num_comms = random.randint(1, 5)
    for i in range(num_comms):
        await prisma.communication.create(
            data={
                "contestId": contest.id,
                "type": random.choice(comm_types),
                "direction": random.choice(directions),
                "subject": f"Comunicação {i + 1} - Contestação {contest.number}",
                "content": f"Conteúdo da comunicação {i + 1} referente à contestação {contest.number}. "
                f"Status atual: {contest.status}.",
                "attachments": [f"doc_{i + 1}.pdf"] if random.random() > 0.5 else [],
                "sentById": None,
                "sentAt": contest.createdAt + timedelta(days=random.randint(1, 30)),
                "readAt": contest.createdAt + timedelta(days=random.randint(1, 30))
                if random.random() > 0.3
                else None,
            }
        )


async def create_payments(prisma: Prisma, contest):
    """Create payments for a contest."""
    items = await prisma.contest_item.find_many(where={"contestId": contest.id})

    if contest.status == "ACCEPTED":
        # Full payment
        await prisma.payment.create(
            data={
                "contestId": contest.id,
                "type": "RECOVERY",
                "amount": contest.netRecovery,
                "currency": "BRL",
                "status": "CONFIRMED",
                "reference": f"PIX-{random.randint(100000, 999999)}",
                "paidAt": contest.resolvedAt
                or (contest.createdAt + timedelta(days=random.randint(30, 60))),
                "confirmedAt": contest.resolvedAt
                or (contest.createdAt + timedelta(days=random.randint(30, 60))),
                "metadata": {"paymentMethod": "PIX", "items": [i.id for i in items]},
            }
        )

        # Update items
        for item in items:
            await prisma.contest_item.update(
                where={"id": item.id},
                data={"recoveredValue": item.contestedValue, "status": "ACCEPTED"},
            )

    elif contest.status == "PARTIAL":
        # Partial payment
        partial_amount = round(contest.netRecovery * random.uniform(0.3, 0.8), 2)
        await prisma.payment.create(
            data={
                "contestId": contest.id,
                "type": "RECOVERY",
                "amount": partial_amount,
                "currency": "BRL",
                "status": "CONFIRMED",
                "reference": f"TED-{random.randint(100000, 999999)}",
                "paidAt": contest.respondedAt
                or (contest.createdAt + timedelta(days=random.randint(15, 45))),
                "confirmedAt": contest.respondedAt
                or (contest.createdAt + timedelta(days=random.randint(15, 45))),
                "metadata": {"paymentMethod": "TED", "partial": True},
            }
        )


async def create_notifications(prisma: Prisma, company, clients):
    """Create notifications for clients."""
    for client in clients:
        users = await prisma.user.find_many(where={"companyId": company.id})
        client_users = [u for u in users if u.clientId == client.id]

        for _ in range(random.randint(5, 20)):
            notif_type = random.choice(NOTIFICATION_TYPES)

            await prisma.notification.create(
                data={
                    "clientId": client.id,
                    "userId": random.choice(client_users).id if client_users else None,
                    "type": notif_type,
                    "title": f"{notif_type.replace('_', ' ').title()}",
                    "message": f"Notificação de {notif_type.lower()} para {client.name}",
                    "data": {"referenceId": f"ref_{random.randint(1000, 9999)}"},
                    "readAt": datetime.now() - timedelta(days=random.randint(0, 30))
                    if random.random() > 0.4
                    else None,
                    "sentAt": datetime.now() - timedelta(days=random.randint(0, 60)),
                    "channels": random.sample(
                        ["EMAIL", "PUSH", "SMS", "IN_APP"], random.randint(1, 3)
                    ),
                }
            )


async def create_audit_logs(prisma: Prisma, company, admin_user):
    """Create audit logs."""
    actions = ["CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "EXPORT", "IMPORT"]
    entities = ["Document", "Discrepancy", "Contest", "Contract", "Client", "Carrier", "User"]

    for _ in range(random.randint(50, 200)):
        await prisma.audit_log.create(
            data={
                "companyId": company.id,
                "userId": admin_user.id if random.random() > 0.5 else None,
                "action": random.choice(actions),
                "entityType": random.choice(entities),
                "entityId": f"ent_{random.randint(1000, 9999)}",
                "oldData": {"field": "old_value"} if random.random() > 0.5 else None,
                "newData": {"field": "new_value"} if random.random() > 0.5 else None,
                "ipAddress": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "createdAt": datetime.now() - timedelta(days=random.randint(0, 90)),
            }
        )


async def create_rules(prisma: Prisma):
    """Create rules for the rules engine."""
    rules_data = [
        # CTe Rules
        {
            "code": "CTE-001",
            "name": "Peso Real vs Faturado",
            "type": "FREIGHT_WEIGHT_VALUE",
            "severity": "HIGH",
            "description": "Valida se o peso real informado no CTe confere com o peso faturado",
            "configJson": {"tolerancePct": 5, "minWeight": 100},
        },
        {
            "code": "CTE-002",
            "name": "Cubagem vs Peso",
            "type": "FREIGHT_CUBAGE",
            "severity": "MEDIUM",
            "description": "Valida a relação entre cubagem e peso do frete",
            "configJson": {"minDensity": 167, "maxDensity": 500},
        },
        {
            "code": "CTE-003",
            "name": "Redespacho",
            "type": "REDESPACHO",
            "severity": "HIGH",
            "description": "Identifica redespachos não informados ou com valores incorretos",
            "configJson": {"checkIntermediateCarriers": True},
        },
        {
            "code": "CTE-004",
            "name": "Pedágio",
            "type": "TOLL_PLAZA",
            "severity": "MEDIUM",
            "description": "Valida valores de pedágio informados no CTe",
            "configJson": {"validateAgainstTable": True},
        },
        {
            "code": "CTE-005",
            "name": "Ad Valorem",
            "type": "AD_VALOREM",
            "severity": "HIGH",
            "description": "Calcula e valida o seguro Ad Valorem",
            "configJson": {"rate": 0.0015, "minValue": 50},
        },
        {
            "code": "CTE-006",
            "name": "GRIS",
            "type": "GRIS",
            "severity": "MEDIUM",
            "description": "Valida o Gerenciamento de Risco e Seguro",
            "configJson": {"rate": 0.0005, "minValue": 10},
        },
        {
            "code": "CTE-007",
            "name": "Tabela SICOBAN",
            "type": "SICOBAN_TABLE",
            "severity": "HIGH",
            "description": "Valida frete contra tabela SICOBAN",
            "configJson": {"tableVersion": "2024.1"},
        },
        {
            "code": "CTE-008",
            "name": "CTe Complementar",
            "type": "COMPLEMENTARY_CTE",
            "severity": "LOW",
            "description": "Valida CTe complementares vinculados",
            "configJson": {"requireOriginalCTe": True},
        },
        {
            "code": "CTE-009",
            "name": "Peso Real vs Faturado",
            "type": "PESO_REAL_VS_FATURADO",
            "severity": "HIGH",
            "description": "Compara peso real medido com peso faturado",
            "configJson": {"toleranceKg": 50},
        },
        {
            "code": "CTE-010",
            "name": "Valor Mínimo de Frete",
            "type": "VALOR_MINIMO_FRETE",
            "severity": "CRITICAL",
            "description": "Valida se o frete atende ao valor mínimo por eixo (RNTRC)",
            "configJson": {"table": "ANTT_2024"},
        },
        {
            "code": "CTE-011",
            "name": "ICMS Diferencial",
            "type": "ICMS_DIFFERENTIAL",
            "severity": "HIGH",
            "description": "Valida cálculo do ICMS diferencial de alíquota",
            "configJson": {"interstateRate": 0.12, "intrastateRate": 0.18},
        },
        {
            "code": "CTE-012",
            "name": "ICMS FCP",
            "type": "ICMS_FCP",
            "severity": "MEDIUM",
            "description": "Valida Fundo de Combate à Pobreza",
            "configJson": {"fcpRate": 0.02},
        },
        {
            "code": "CTE-013",
            "name": "ICMS ST",
            "type": "ICMS_ST",
            "severity": "HIGH",
            "description": "Valida Substituição Tributária do ICMS",
            "configJson": {"mvaTable": "2024"},
        },
        # NFe Rules
        {
            "code": "NFE-001",
            "name": "CFOP Inválido",
            "type": "OTHER",
            "severity": "CRITICAL",
            "description": "Valida se o CFOP é compatível com a operação",
            "configJson": {"validCFOPs": ["5102", "5405", "6102", "6405"]},
        },
        {
            "code": "NFE-002",
            "name": "NCM/CEST",
            "type": "OTHER",
            "severity": "HIGH",
            "description": "Valida NCM e CEST dos produtos",
            "configJson": {"validateAgainstTable": True},
        },
        {
            "code": "NFE-003",
            "name": "Destinatário",
            "type": "OTHER",
            "severity": "MEDIUM",
            "description": "Valida dados do destinatário (CNPJ, IE, endereço)",
            "configJson": {"validateCNPJ": True, "validateIE": True},
        },
        {
            "code": "NFE-004",
            "name": "Transportadora",
            "type": "OTHER",
            "severity": "MEDIUM",
            "description": "Valida dados da transportadora no CTe/NFe",
            "configJson": {"requireRNTRC": True},
        },
        {
            "code": "NFE-005",
            "name": "Valores Totais",
            "type": "OTHER",
            "severity": "CRITICAL",
            "description": "Valida consistência dos valores totais da NFe",
            "configJson": {"tolerance": 0.01},
        },
        {
            "code": "NFE-006",
            "name": "Regime Especial",
            "type": "OTHER",
            "severity": "LOW",
            "description": "Valida regimes especiais de tributação",
            "configJson": {},
        },
        {
            "code": "NFE-007",
            "name": "Cancelamento/Inutilização",
            "type": "OTHER",
            "severity": "LOW",
            "description": "Valida numeração de NFe canceladas/inutilizadas",
            "configJson": {},
        },
    ]

    created_rules = []
    for rule_data in rules_data:
        tags = []
        if "CTE" in rule_data["code"]:
            tags.append("cte")
        if "NFE" in rule_data["code"]:
            tags.append("nfe")
        if rule_data["severity"] in ["HIGH", "CRITICAL"]:
            tags.append("critical")

        rule = await prisma.rule.create(
            data={
                "code": rule_data["code"],
                "name": rule_data["name"],
                "type": rule_data["type"],
                "severity": rule_data["severity"],
                "configJson": rule_data["configJson"],
                "version": 1,
                "isActive": True,
                "description": rule_data["description"],
                "tags": tags,
            }
        )
        created_rules.append(rule)

    return created_rules


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    asyncio.run(seed_database())
