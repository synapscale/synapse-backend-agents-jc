# Documentação do Schema do Banco de Dados

**Gerado em:** 2025-07-07 19:24:45

## Índice

- [Schema Banco_De_Dados](#schema-Banco-De-Dados)
- [Schema airbyte_internal](#schema-airbyte-internal)
- [Schema banco_de_dados](#schema-banco-de-dados)
- [Schema banco_de_dados_jc](#schema-banco-de-dados-jc)
- [Schema joaocastanheira_bancodedados](#schema-joaocastanheira-bancodedados)
- [Schema modelo_saas_inicial](#schema-modelo-saas-inicial)
- [Schema public](#schema-public)
- [Schema synapscale_db](#schema-synapscale-db)
- [Relacionamentos](#relacionamentos)

## Schema Banco_De_Dados

**Resumo:**
- 📋 Total de tabelas: 0
- 📊 Total de registros: 0

## Schema airbyte_internal

**Resumo:**
- 📋 Total de tabelas: 0
- 📊 Total de registros: 0

## Schema banco_de_dados

**Resumo:**
- 📋 Total de tabelas: 57
- 📊 Total de registros: 17

### Tabela: `platform_commission`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `participant_id` | bigint | ❌ | - | - |
| `platform_id` | character varying | ❌ | - | 255 |
| `name` | character varying | ❌ | - | 150 |
| `price` | numeric | ❌ | - | - |
| `producer_paid_value` | numeric | ❌ | - | - |
| `original_value` | numeric | ❌ | - | - |
| `original_paid_value` | numeric | ❌ | - | - |
| `producer_value` | numeric | ❌ | - | - |
| `currency` | character varying | ❌ | - | 10 |
| `conversion_rate` | numeric | ✅ | - | - |
| `type` | character varying | ❌ | - | 50 |
| `email` | character varying | ✅ | - | 255 |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_commission_participants`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_id` | character varying | ❌ | - | 100 |
| `email` | character varying | ✅ | - | 255 |
| `name` | character varying | ✅ | - | 255 |
| `trader_name` | character varying | ✅ | - | 255 |
| `telephone` | character varying | ✅ | - | 50 |
| `document` | character varying | ✅ | - | 100 |
| `locale` | character varying | ✅ | - | 10 |
| `client_address_id` | bigint | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_commission_participants_doc`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `value` | character varying | ❌ | - | 50 |
| `type` | character varying | ❌ | - | 10 |
| `commission_participant_id` | bigint | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_sale`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `id_transaction` | character varying | ❌ | - | 255 |
| `client_id` | bigint | ❌ | - | - |
| `platform` | character varying | ❌ | - | 100 |
| `is_subscription` | boolean | ❌ | false | - |
| `warranty_expire_date` | timestamp with time zone | ✅ | - | - |
| `order_date` | timestamp with time zone | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_sale_client`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `email` | character varying | ❌ | - | 255 |
| `name` | character varying | ❌ | - | 150 |
| `phone` | character varying | ✅ | - | 20 |
| `document` | character varying | ✅ | - | 20 |
| `profile_id` | bigint | ❌ | - | - |
| `client_address_id` | bigint | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_sale_client_address`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `address` | character varying | ❌ | - | 255 |
| `neighborhood` | character varying | ✅ | - | 100 |
| `country` | character varying | ✅ | - | 100 |
| `city` | character varying | ✅ | - | 100 |
| `zip_code` | character varying | ✅ | - | 20 |
| `complement` | character varying | ✅ | - | 255 |
| `number` | character varying | ✅ | - | 20 |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `ip` | inet | ✅ | - | - |

### Tabela: `platform_sale_client_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_sale_client_id` | bigint | ❌ | - | - |
| `field_name` | character varying | ❌ | - | 100 |
| `old_value` | character varying | ✅ | - | 255 |
| `new_value` | character varying | ✅ | - | 255 |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_sale_client_platform_id`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_id` | character varying | ❌ | - | 255 |
| `sale_client_id` | bigint | ❌ | - | - |
| `platform` | character varying | ❌ | - | 100 |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_sale_offer_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `code` | character varying | ❌ | - | 100 |
| `id_offer` | character varying | ❌ | - | 255 |
| `offer_name` | character varying | ❌ | - | 255 |
| `description` | character varying | ✅ | - | 500 |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_software_invoice_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `invoice_status` | USER-DEFINED | ❌ | - | - |
| `invoice_value` | numeric | ❌ | - | - |
| `invoice_software` | character varying | ❌ | - | 100 |
| `invoice_created_at` | timestamp with time zone | ❌ | - | - |

### Tabela: `platform_status`

**Registros:** 10

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `status` | character varying | ❌ | - | 50 |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_subscription`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `subscription_id` | bigint | ❌ | - | - |
| `subscriber_id` | bigint | ❌ | - | - |
| `id_transaction` | character varying | ❌ | - | 255 |
| `subscriber_code` | character varying | ✅ | - | 100 |
| `purchase` | boolean | ❌ | false | - |
| `platform` | character varying | ❌ | - | 100 |
| `billing_type` | character varying | ❌ | - | 50 |
| `lifetime` | integer | ✅ | - | - |
| `max_cycles` | integer | ✅ | - | - |
| `last_update` | timestamp with time zone | ✅ | - | - |
| `subscription_start` | timestamp with time zone | ❌ | - | - |
| `subscription_end` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_subscription__recurrency_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_subscription_id` | bigint | ❌ | - | - |
| `id_transaction` | character varying | ❌ | - | 255 |
| `status` | character varying | ❌ | - | 50 |
| `type` | character varying | ❌ | - | 50 |
| `transaction_type` | character varying | ❌ | - | 50 |
| `under_warranty` | boolean | ❌ | false | - |
| `is_trial` | boolean | ❌ | false | - |
| `current_purchase` | boolean | ❌ | false | - |
| `is_paid_anticipation` | boolean | ❌ | false | - |
| `payment_delay` | integer | ✅ | - | - |
| `trial_period` | integer | ✅ | - | - |
| `trial_end` | timestamp with time zone | ✅ | - | - |
| `sequence` | integer | ✅ | - | - |
| `last_recurrency` | integer | ✅ | - | - |
| `recurrency` | integer | ✅ | - | - |
| `recurrency_period` | integer | ✅ | - | - |
| `retry_schedule` | timestamp with time zone | ✅ | - | - |
| `last_recurrency_status` | character varying | ✅ | - | 50 |
| `transaction_quantity` | integer | ✅ | - | - |
| `request_date` | timestamp with time zone | ✅ | - | - |
| `cancellation_date` | timestamp with time zone | ✅ | - | - |
| `charge_date` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_commission`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_subscription_id` | bigint | ✅ | - | - |
| `platform_sale_id` | bigint | ✅ | - | - |
| `platform_commission_id` | bigint | ❌ | - | - |
| `type` | USER-DEFINED | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_fee`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_sale_id` | bigint | ✅ | - | - |
| `platform_subscription_id` | bigint | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_fee_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `base_value` | numeric | ❌ | - | - |
| `fee_amount` | numeric | ❌ | - | - |
| `fee_currency_code` | character varying | ❌ | - | 10 |
| `fee_percentage` | numeric | ✅ | - | - |
| `tax_amount` | numeric | ❌ | - | - |
| `tax_currency_code` | character varying | ❌ | - | 10 |
| `tax_percentage` | numeric | ✅ | - | - |
| `coupon_value` | numeric | ✅ | - | - |
| `coupon_name` | character varying | ✅ | - | 100 |
| `conversion_rate` | numeric | ✅ | - | - |
| `fixed_value` | numeric | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_invoice`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_subscription_id` | bigint | ✅ | - | - |
| `platform_sale_id` | bigint | ✅ | - | - |
| `software_invoice_id` | bigint | ❌ | - | - |
| `type` | USER-DEFINED | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_offer`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_sale_id` | bigint | ✅ | - | - |
| `platform_subscription_id` | bigint | ✅ | - | - |
| `platform_offer_history_id` | bigint | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_payment`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_sale_id` | bigint | ✅ | - | - |
| `platform_subscription_id` | bigint | ✅ | - | - |
| `payment_history_id` | bigint | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_payment_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `type` | character varying | ❌ | - | 50 |
| `installments` | integer | ✅ | - | - |
| `installment_type` | character varying | ✅ | - | 50 |
| `card_last_digits` | character varying | ✅ | - | 4 |
| `card_change` | boolean | ❌ | false | - |
| `card_flag` | character varying | ✅ | - | 20 |
| `refusal_message` | character varying | ✅ | - | 255 |
| `current_installment` | integer | ✅ | - | - |
| `base_value` | integer | ❌ | - | - |
| `gross_value` | integer | ❌ | - | - |
| `net_value` | integer | ❌ | - | - |
| `currency` | integer | ❌ | - | - |
| `payment_gateway` | character varying | ✅ | - | 50 |
| `billet_expiration` | timestamp with time zone | ✅ | - | - |
| `billet_recovery` | character varying | ✅ | - | 50 |
| `billet_reprint_code` | character varying | ✅ | - | 100 |
| `chargeback_date` | timestamp with time zone | ✅ | - | - |
| `pix_expiration_date` | timestamp with time zone | ✅ | - | - |
| `approved_date` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_plan`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_sale_id` | bigint | ✅ | - | - |
| `platform_subscription_id` | bigint | ✅ | - | - |
| `plan_history_id` | bigint | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_plan_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `plan_name` | character varying | ❌ | - | 255 |
| `plan_id` | character varying | ❌ | - | 255 |
| `price` | numeric | ❌ | - | - |
| `recurrency_period` | character varying | ✅ | - | 50 |
| `coupon_code` | character varying | ✅ | - | 100 |
| `charge_cycles` | integer | ✅ | - | - |
| `recurrency_type` | USER-DEFINED | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_product`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_subscription_id` | bigint | ✅ | - | - |
| `platform_sale_id` | bigint | ✅ | - | - |
| `product_id` | character varying | ❌ | - | 255 |
| `ucode` | character varying | ❌ | - | 100 |
| `name` | character varying | ❌ | - | 255 |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_status`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_sale_id` | bigint | ✅ | - | - |
| `platform_status_id` | bigint | ❌ | - | - |
| `platform_subscription_id` | bigint | ✅ | - | - |
| `reason` | character varying | ✅ | - | 255 |
| `type` | USER-DEFINED | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_utm`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `platform_sale_id` | bigint | ✅ | - | - |
| `platform_subscription_id` | bigint | ✅ | - | - |
| `platform_utm_id` | bigint | ❌ | - | - |
| `type` | USER-DEFINED | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_utm_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ❌ | - | - |
| `utm_source` | character varying | ✅ | - | 100 |
| `utm_src` | character varying | ✅ | - | 100 |
| `utm_sck` | character varying | ✅ | - | 100 |
| `utm_medium` | character varying | ✅ | - | 100 |
| `utm_campaign` | character varying | ✅ | - | 255 |
| `utm_term` | character varying | ✅ | - | 255 |
| `external_code` | character varying | ✅ | - | 255 |
| `fbp` | character varying | ✅ | - | 255 |
| `fbc` | character varying | ✅ | - | 255 |
| `gclid` | character varying | ✅ | - | 255 |
| `utm_content` | character varying | ✅ | - | 255 |
| `created_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ❌ | CURRENT_TIMESTAMP | - |

### Tabela: `vw_assinaturas_ativas_por_plataforma`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `platform` | character varying | ✅ | - | 100 |
| `assinaturas_ativas` | bigint | ✅ | - | - |

### Tabela: `vw_assinaturas_novas_vs_canceladas`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `mes` | timestamp with time zone | ✅ | - | - |
| `novas_assinaturas` | bigint | ✅ | - | - |
| `cancelamentos` | bigint | ✅ | - | - |

### Tabela: `vw_churn_rate_30_dias`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `churn_percentual` | numeric | ✅ | - | - |

### Tabela: `vw_clientes_inativos_90_dias`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ✅ | - | - |
| `email` | character varying | ✅ | - | 255 |

### Tabela: `vw_clientes_novos_por_mes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `mes` | timestamp with time zone | ✅ | - | - |
| `novos_clientes` | bigint | ✅ | - | - |

### Tabela: `vw_clientes_por_cidade`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `city` | character varying | ✅ | - | 100 |
| `total` | bigint | ✅ | - | - |

### Tabela: `vw_clientes_por_completude_de_cadastro`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `perc_documento` | numeric | ✅ | - | - |
| `perc_telefone` | numeric | ✅ | - | - |
| `perc_endereco` | numeric | ✅ | - | - |

### Tabela: `vw_clientes_recorrentes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `client_id` | bigint | ✅ | - | - |
| `total_compras` | bigint | ✅ | - | - |

### Tabela: `vw_clientes_top_10_por_ticket`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | bigint | ✅ | - | - |
| `email` | character varying | ✅ | - | 255 |
| `id_transaction` | character varying | ✅ | - | 255 |
| `valor` | integer | ✅ | - | - |

### Tabela: `vw_comissoes_por_tipo_participante`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `type` | character varying | ✅ | - | 50 |
| `qtd` | bigint | ✅ | - | - |
| `total_pago` | numeric | ✅ | - | - |

### Tabela: `vw_comissoes_totais_por_participante`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `name` | character varying | ✅ | - | 150 |
| `comissao_total` | numeric | ✅ | - | - |

### Tabela: `vw_cupons_mais_utilizados`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `coupon_name` | character varying | ✅ | - | 100 |
| `uso` | bigint | ✅ | - | - |

### Tabela: `vw_evolucao_faturamento`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `mes` | timestamp with time zone | ✅ | - | - |
| `faturamento_liquido` | bigint | ✅ | - | - |
| `mes_anterior` | bigint | ✅ | - | - |
| `variacao_percentual` | numeric | ✅ | - | - |

### Tabela: `vw_faturamento_por_mes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `mes` | timestamp with time zone | ✅ | - | - |
| `faturamento_liquido` | bigint | ✅ | - | - |

### Tabela: `vw_faturamento_resumido`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `faturamento_bruto` | bigint | ✅ | - | - |
| `valor_bruto_recebido` | bigint | ✅ | - | - |
| `faturamento_liquido` | bigint | ✅ | - | - |
| `total_em_taxas` | bigint | ✅ | - | - |

### Tabela: `vw_mrr_arr_por_billing_type`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `billing_type` | character varying | ✅ | - | 50 |
| `assinaturas_ativas` | bigint | ✅ | - | - |
| `receita_mensal_estimativa` | numeric | ✅ | - | - |
| `receita_anual_estimativa` | numeric | ✅ | - | - |

### Tabela: `vw_participantes_com_mais_transacoes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `name` | character varying | ✅ | - | 150 |
| `qtd_transacoes` | bigint | ✅ | - | - |

### Tabela: `vw_planos_mais_adquiridos`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `plan_name` | character varying | ✅ | - | 255 |
| `qtd` | bigint | ✅ | - | - |

### Tabela: `vw_produtos_mais_vendidos`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `name` | character varying | ✅ | - | 255 |
| `qtd` | bigint | ✅ | - | - |

### Tabela: `vw_receita_por_utm_campaign`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `utm_campaign` | character varying | ✅ | - | 255 |
| `receita_liquida` | bigint | ✅ | - | - |

### Tabela: `vw_receita_por_utm_source`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `utm_source` | character varying | ✅ | - | 100 |
| `receita_liquida` | bigint | ✅ | - | - |

### Tabela: `vw_receita_por_utm_term`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `utm_term` | character varying | ✅ | - | 255 |
| `qtd` | bigint | ✅ | - | - |
| `receita` | bigint | ✅ | - | - |

### Tabela: `vw_receita_total_por_produto`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `name` | character varying | ✅ | - | 255 |
| `receita_total` | bigint | ✅ | - | - |

### Tabela: `vw_roi_liquido_empresa`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `faturamento_liquido` | bigint | ✅ | - | - |
| `total_comissoes` | numeric | ✅ | - | - |
| `lucro_liquido_aproximado` | numeric | ✅ | - | - |

### Tabela: `vw_taxa_chargeback`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `taxa_chargeback_percentual` | double precision | ✅ | - | - |

### Tabela: `vw_tempo_medio_aprovacao_pagamentos`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `tempo_medio_aprovacao_min` | numeric | ✅ | - | - |

### Tabela: `vw_tempo_medio_de_vida_assinatura`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `media_dias` | numeric | ✅ | - | - |

### Tabela: `vw_tentativas_com_retry_agendado`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id_transaction` | character varying | ✅ | - | 255 |
| `retry_schedule` | timestamp with time zone | ✅ | - | - |

### Tabela: `vw_ticket_medio_por_tipo`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `tipo_transacao` | USER-DEFINED | ✅ | - | - |
| `total_transacoes` | bigint | ✅ | - | - |
| `ticket_medio` | numeric | ✅ | - | - |

### Tabela: `vw_vendas_com_problemas`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id_transaction` | character varying | ✅ | - | 255 |
| `status` | character varying | ✅ | - | 50 |

### Tabela: `vw_vendas_por_utm_content`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `utm_content` | character varying | ✅ | - | 255 |
| `total_vendas` | bigint | ✅ | - | - |

## Schema banco_de_dados_jc

**Resumo:**
- 📋 Total de tabelas: 18
- 📊 Total de registros: 1,412,137

### Tabela: `comissoes_vendas_na_hotmart`

**Registros:** 14,388

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `numero_da_comissao` | integer | ❌ | nextval('banco_de_dados_jc.comissoes_vendas_hotmart_numero_da_comissao_seq'::regclass) | - |
| `id_transacao` | character varying | ❌ | - | 20 |
| `id_produto` | integer | ❌ | - | - |
| `nome_produto` | character varying | ❌ | - | 255 |
| `taxa_cambio_pagamento` | numeric | ✅ | - | - |
| `id_usuario_produtor` | uuid | ✅ | - | - |
| `nome_usuario_produtor` | character varying | ✅ | - | 255 |
| `valor_comissao_produtor` | numeric | ✅ | - | - |
| `moeda_comissao_produtor` | character varying | ✅ | - | 10 |
| `id_usuario_coprodutor` | uuid | ✅ | - | - |
| `nome_usuario_coprodutor` | character varying | ✅ | - | 255 |
| `valor_comissao_coprodutor` | numeric | ✅ | - | - |
| `moeda_comissao_coprodutor` | character varying | ✅ | - | 10 |
| `id_usuario_addon` | uuid | ✅ | - | - |
| `nome_usuario_addon` | character varying | ✅ | - | 255 |
| `valor_comissao_addon` | numeric | ✅ | - | - |
| `moeda_comissao_addon` | character varying | ✅ | - | 10 |
| `id_usuario_afiliado` | uuid | ✅ | - | - |
| `nome_usuario_afiliado` | character varying | ✅ | - | 255 |
| `valor_comissao_afiliado` | numeric | ✅ | - | - |
| `moeda_comissao_afiliado` | character varying | ✅ | - | 10 |
| `data_criacao` | text | ✅ | - | - |

### Tabela: `contatos_activecampaign`

**Registros:** 351,851

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id_tabeladimcliente` | integer | ✅ | - | - |
| `contact_id` | character varying | ❌ | - | 255 |
| `email` | character varying | ✅ | - | 255 |
| `nome` | character varying | ✅ | - | 255 |
| `sobrenome` | character varying | ✅ | - | 255 |
| `telefone` | character varying | ✅ | - | 255 |
| `endereco_ip` | character varying | ✅ | - | 255 |
| `agente_usuario` | text | ✅ | - | - |
| `documento` | character varying | ✅ | - | 255 |

### Tabela: `detalhes_precos_vendas_na_hotmart`

**Registros:** 14,388

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id_transacao` | text | ❌ | - | - |
| `numero_da_venda` | integer | ✅ | - | - |
| `data_criacao` | text | ✅ | - | - |
| `id_produto` | integer | ❌ | - | - |
| `nome_produto` | character varying | ❌ | - | 255 |
| `valor_base_produto` | numeric | ❌ | - | - |
| `moeda_base_produto` | character varying | ❌ | - | 10 |
| `valor_total` | numeric | ❌ | - | - |
| `moeda_total` | character varying | ❌ | - | 10 |
| `valor_imposto` | numeric | ✅ | - | - |
| `moeda_imposto` | character varying | ✅ | - | 10 |
| `valor_taxa` | numeric | ✅ | - | - |
| `moeda_taxa` | character varying | ✅ | - | 10 |
| `codigo_cupom` | character varying | ✅ | - | 50 |
| `valor_cupom` | numeric | ✅ | - | - |
| `taxa_conversao_real` | numeric | ✅ | - | - |

### Tabela: `dim_cliente`

**Registros:** 351,851

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `cliente_id` | integer | ❌ | nextval('banco_de_dados_jc.dim_cliente_cliente_id_seq'::regclass) | - |
| `email` | character varying | ❌ | - | 255 |
| `nome` | character varying | ✅ | - | 255 |
| `sobrenome` | character varying | ✅ | - | 255 |
| `documento` | character varying | ✅ | - | 50 |
| `telefone` | character varying | ✅ | - | 50 |
| `endereco` | character varying | ✅ | - | 255 |
| `bairro` | character varying | ✅ | - | 100 |
| `cidade` | character varying | ✅ | - | 100 |
| `estado` | character varying | ✅ | - | 100 |
| `cep` | character varying | ✅ | - | 20 |
| `pais` | character varying | ✅ | - | 100 |
| `active_campaign` | boolean | ✅ | - | - |
| `active_quantidade_emails_recebidos` | integer | ✅ | - | - |
| `active_quantidade_emails_abertos` | integer | ✅ | - | - |
| `active_quantidade_emails_clicados` | integer | ✅ | - | - |
| `active_ultimo_email_aberto` | timestamp without time zone | ✅ | - | - |
| `active_ultimo_email_clicado` | timestamp without time zone | ✅ | - | - |
| `lead_score` | integer | ✅ | - | - |
| `status_lead` | character varying | ✅ | - | 50 |
| `data_criacao_lead` | timestamp without time zone | ✅ | - | - |
| `data_conversao_cliente` | timestamp without time zone | ✅ | - | - |
| `data_ultimo_cadastro` | timestamp without time zone | ✅ | - | - |
| `quantidade_recadastros` | integer | ✅ | - | - |
| `utm_source_captura` | character varying | ✅ | - | 200 |
| `utm_medium_captura` | character varying | ✅ | - | 200 |
| `utm_campaign_captura` | character varying | ✅ | - | 200 |
| `utm_term_captura` | character varying | ✅ | - | 200 |
| `utm_content_captura` | character varying | ✅ | - | 200 |
| `tags` | ARRAY | ✅ | - | - |
| `endereco_ip` | character varying | ✅ | - | 50 |
| `latitude` | numeric | ✅ | - | - |
| `longitude` | numeric | ✅ | - | - |
| `observacoes` | text | ✅ | - | - |
| `ac_contact_id` | character varying | ✅ | nextval('banco_de_dados_jc.contatos_activecampaign'::regclass) | 255 |

### Tabela: `dim_produto`

**Registros:** 7

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `produto_id` | integer | ❌ | nextval('banco_de_dados_jc.dim_produto_produto_id_seq'::regclass) | - |
| `nome_raiz` | character varying | ❌ | - | 255 |
| `nome_variacao` | character varying | ✅ | - | 255 |
| `sku` | character varying | ❌ | - | 100 |
| `categoria` | character varying | ✅ | - | 100 |
| `subcategoria` | character varying | ✅ | - | 100 |
| `plataforma_padrao` | character varying | ✅ | - | 50 |
| `data_criacao_produto` | timestamp without time zone | ✅ | - | - |
| `preco_sugerido` | numeric | ✅ | - | - |
| `taxa_sugerida` | numeric | ✅ | - | - |
| `moeda_padrao` | character varying | ✅ | - | 10 |
| `campanha` | character varying | ✅ | - | 255 |
| `descricao` | text | ✅ | - | - |

### Tabela: `fact_acessos_cademi`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `acesso_id` | bigint | ❌ | nextval('banco_de_dados_jc.fact_acessos_cademi_acesso_id_seq'::regclass) | - |
| `cliente_id` | integer | ✅ | - | - |
| `produto_id` | integer | ❌ | - | - |
| `data_acesso` | timestamp without time zone | ✅ | - | - |
| `tipo_acesso` | character varying | ✅ | - | 50 |
| `duracao_min` | integer | ✅ | - | - |
| `modulo_curso` | character varying | ✅ | - | 50 |

### Tabela: `fact_pesquisas`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `pesquisa_id` | bigint | ❌ | nextval('banco_de_dados_jc.fact_pesquisas_pesquisa_id_seq'::regclass) | - |
| `cliente_id` | integer | ❌ | - | - |
| `data_resposta` | timestamp without time zone | ✅ | - | - |
| `tipo_pesquisa` | character varying | ✅ | - | 50 |
| `pergunta_1` | character varying | ✅ | - | 255 |
| `resposta_1` | character varying | ✅ | - | 255 |
| `pergunta_2` | character varying | ✅ | - | 255 |
| `resposta_2` | character varying | ✅ | - | 255 |
| `nota_nps` | integer | ✅ | - | - |
| `obs_pesquisa` | text | ✅ | - | - |

### Tabela: `fact_vendas`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `venda_id` | bigint | ❌ | nextval('banco_de_dados_jc.fact_vendas_venda_id_seq'::regclass) | - |
| `cliente_id` | integer | ❌ | - | - |
| `produto_id` | integer | ❌ | - | - |
| `codigo_payt` | character varying | ✅ | - | 50 |
| `id_venda_kiwify` | character varying | ✅ | - | 50 |
| `codigo_transacao_hotmart` | character varying | ✅ | - | 50 |
| `plataforma` | character varying | ✅ | - | 50 |
| `data_venda` | timestamp without time zone | ✅ | - | - |
| `data_atualizacao` | timestamp without time zone | ✅ | - | - |
| `valor_bruto` | numeric | ✅ | - | - |
| `valor_liquido` | numeric | ✅ | - | - |
| `valor_imposto` | numeric | ✅ | - | - |
| `taxa_plataforma` | numeric | ✅ | - | - |
| `comissao_afiliado` | numeric | ✅ | - | - |
| `comissao_coprodutor` | numeric | ✅ | - | - |
| `forma_pagamento` | character varying | ✅ | - | 50 |
| `quantidade_parcelas` | integer | ✅ | - | - |
| `status_venda` | character varying | ✅ | - | 50 |
| `utm_source_compra` | character varying | ✅ | - | 200 |
| `utm_medium_compra` | character varying | ✅ | - | 200 |
| `utm_campaign_compra` | character varying | ✅ | - | 200 |
| `utm_term_compra` | character varying | ✅ | - | 200 |
| `utm_content_compra` | character varying | ✅ | - | 200 |
| `obs_venda` | text | ✅ | - | - |
| `email_comprador` | character varying | ✅ | - | 255 |
| `sku` | ARRAY | ✅ | - | - |
| `codigovenda_no_gateway` | character varying | ❌ | - | 50 |
| `documento_comprador` | character varying | ❌ | - | 50 |
| `produto` | character varying | ✅ | - | 255 |

### Tabela: `map_produtos`

**Registros:** 146

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `map_produto_id` | integer | ❌ | nextval('banco_de_dados_jc.map_produtos_map_produto_id_seq'::regclass) | - |
| `plataforma` | character varying | ❌ | - | 50 |
| `produto_limpo` | character varying | ❌ | - | 255 |
| `plano_variacao` | character varying | ✅ | - | 255 |
| `codigos_produto` | ARRAY | ❌ | '{}'::text[] | - |

### Tabela: `mapa_produtos`

**Registros:** 154

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `map_produto_id` | integer | ❌ | nextval('banco_de_dados_jc.mapa_produtos_map_produto_id_seq'::regclass) | - |
| `plataforma` | character varying | ❌ | - | 50 |
| `produto` | character varying | ❌ | - | 255 |
| `sufixo_produto` | ARRAY | ✅ | - | - |
| `codigos_produto` | ARRAY | ❌ | '{}'::text[] | - |

### Tabela: `sufixos`

**Registros:** 34

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('banco_de_dados_jc.sufixos_id_seq'::regclass) | - |
| `produto` | character varying | ❌ | - | 255 |
| `plataforma` | character varying | ❌ | - | 50 |
| `sufixo` | character varying | ❌ | - | 255 |

### Tabela: `tmp_consolidado_produtos`

**Registros:** 15,405

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `origem` | USER-DEFINED | ❌ | - | - |
| `produto_original` | character varying | ❌ | - | 1000 |
| `codigo_produto` | character varying | ❌ | - | 255 |
| `nome_preco` | character varying | ✅ | - | 255 |
| `codigo_preco` | character varying | ✅ | - | 50 |
| `preco_sem_impostos` | numeric | ✅ | - | - |
| `preco_com_taxas` | numeric | ✅ | - | - |
| `campanha` | character varying | ✅ | - | 255 |
| `utm_campaign` | character varying | ✅ | - | 255 |
| `created_at` | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `vendas_hotmart`

**Registros:** 113,852

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `codigo_transacao` | character varying | ❌ | - | 50 |
| `status_transacao` | character varying | ✅ | - | 100 |
| `data_transacao` | timestamp without time zone | ✅ | - | - |
| `confirmacao_pagamento` | character varying | ✅ | - | 100 |
| `produtor` | character varying | ✅ | - | 100 |
| `codigo_produto` | integer | ✅ | - | - |
| `produto` | character varying | ✅ | - | 255 |
| `codigo_preco` | character varying | ✅ | - | 50 |
| `nome_preco` | character varying | ✅ | - | 255 |
| `taxa_conversao_compra` | numeric | ✅ | - | - |
| `moeda_compra` | character varying | ✅ | - | 10 |
| `valor_compra_impostos` | numeric | ✅ | - | - |
| `impostos_locais_compra` | numeric | ✅ | - | - |
| `valor_compra_sem_impostos` | numeric | ✅ | - | - |
| `taxa_conversao_comissao` | numeric | ✅ | - | - |
| `moeda_comissao` | character varying | ✅ | - | 10 |
| `comissao_bruta` | numeric | ✅ | - | - |
| `minha_comissao` | numeric | ✅ | - | - |
| `venda_feita_como` | character varying | ✅ | - | 50 |
| `comissao_produtor` | numeric | ✅ | - | - |
| `comissao_afiliado` | numeric | ✅ | - | - |
| `comissao_coprodutor` | numeric | ✅ | - | - |
| `moeda_taxas` | character varying | ✅ | - | 10 |
| `taxa_processamento` | numeric | ✅ | - | - |
| `taxa_streaming` | numeric | ✅ | - | - |
| `outras_taxas` | numeric | ✅ | - | - |
| `nome_afiliado` | character varying | ✅ | - | 100 |
| `canal_venda` | character varying | ✅ | - | 100 |
| `codigo_src` | character varying | ✅ | - | 50 |
| `codigo_sck` | character varying | ✅ | - | 50 |
| `metodo_pagamento` | character varying | ✅ | - | 100 |
| `tipo_cobranca` | character varying | ✅ | - | 100 |
| `total_parcelas` | integer | ✅ | - | - |
| `quantidade_cobrancas` | integer | ✅ | - | - |
| `data_vencimento_vouchers` | timestamp without time zone | ✅ | - | - |
| `codigo_cupom` | character varying | ✅ | - | 50 |
| `periodo_gratuito_trial` | character varying | ✅ | - | 50 |
| `quantidade_itens` | integer | ✅ | - | - |
| `comprador` | character varying | ✅ | - | 100 |
| `email_comprador` | character varying | ✅ | - | 255 |
| `pais` | character varying | ✅ | - | 50 |
| `telefone` | character varying | ✅ | - | 50 |
| `documento` | character varying | ✅ | - | 50 |
| `codigo_postal` | character varying | ✅ | - | 20 |
| `cidade` | character varying | ✅ | - | 100 |
| `estado_provincia` | character varying | ✅ | - | 100 |
| `endereco` | character varying | ✅ | - | 255 |
| `bairro` | character varying | ✅ | - | 100 |
| `numero` | character varying | ✅ | - | 20 |
| `complemento` | character varying | ✅ | - | 100 |
| `instagram` | character varying | ✅ | - | 100 |
| `codigo_assinante` | character varying | ✅ | - | 50 |
| `tax_solutions` | character varying | ✅ | - | 100 |
| `tax_collected` | numeric | ✅ | - | - |
| `tax_jurisdiction` | character varying | ✅ | - | 100 |
| `tipo_order_bump` | character varying | ✅ | - | 100 |
| `transacao_order_bump` | character varying | ✅ | - | 100 |
| `tipo_antecipacao_assinatura` | character varying | ✅ | - | 100 |
| `motivo_recusa_cartao` | character varying | ✅ | - | 255 |
| `imposto_servico_hotmart` | numeric | ✅ | - | - |
| `impostos_locais` | numeric | ✅ | - | - |
| `juros_parcelamento` | numeric | ✅ | - | - |
| `valor_frete_bruto` | numeric | ✅ | - | - |

### Tabela: `vendas_kiwify`

**Registros:** 15,287

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id_venda` | character varying | ❌ | - | 50 |
| `status` | character varying | ✅ | - | 50 |
| `produto` | character varying | ✅ | - | 1000 |
| `cliente` | character varying | ✅ | - | 1000 |
| `email` | character varying | ✅ | - | 255 |
| `cpf` | character varying | ✅ | - | 20 |
| `celular` | character varying | ✅ | - | 20 |
| `ip` | character varying | ✅ | - | 50 |
| `endereco` | character varying | ✅ | - | 255 |
| `numero` | character varying | ✅ | - | 10 |
| `complemento` | character varying | ✅ | - | 255 |
| `bairro` | character varying | ✅ | - | 100 |
| `cidade` | character varying | ✅ | - | 100 |
| `estado` | character varying | ✅ | - | 50 |
| `cep` | character varying | ✅ | - | 20 |
| `pais` | character varying | ✅ | - | 50 |
| `status_recebimento` | character varying | ✅ | - | 50 |
| `data_liberacao_estimada` | date | ✅ | - | - |
| `data_deposito` | date | ✅ | - | - |
| `parcelas` | integer | ✅ | - | - |
| `ultimos_digitos_cartao` | character varying | ✅ | - | 10 |
| `tipo_pagamento` | character varying | ✅ | - | 50 |
| `moeda` | character varying | ✅ | - | 10 |
| `valor_liquido` | numeric | ✅ | - | - |
| `taxas` | numeric | ✅ | - | - |
| `preco_base_produto` | numeric | ✅ | - | - |
| `total_com_acrescimo` | numeric | ✅ | - | - |
| `oferta` | character varying | ✅ | - | 1000 |
| `metodo_pagamento` | character varying | ✅ | - | 50 |
| `motivo_recusa` | character varying | ✅ | - | 1000 |
| `tracking_src` | character varying | ✅ | - | 1000 |
| `tracking_sck` | character varying | ✅ | - | 1000 |
| `tracking_utm_source` | character varying | ✅ | - | 1000 |
| `tracking_utm_medium` | character varying | ✅ | - | 255 |
| `tracking_utm_campaign` | character varying | ✅ | - | 1000 |
| `tracking_utm_content` | character varying | ✅ | - | 1000 |
| `tracking_utm_term` | character varying | ✅ | - | 255 |
| `data_criacao` | timestamp without time zone | ✅ | - | - |
| `data_atualizacao` | timestamp without time zone | ✅ | - | - |
| `id_nota_fiscal` | character varying | ✅ | - | 50 |
| `status_nota_fiscal` | character varying | ✅ | - | 50 |
| `nota_fiscal_emitida_por` | character varying | ✅ | - | 255 |
| `software_nota_fiscal` | character varying | ✅ | - | 255 |
| `valor_nota_fiscal` | numeric | ✅ | - | - |
| `kiwify_network` | character varying | ✅ | - | 255 |
| `provedor_one_click` | character varying | ✅ | - | 255 |
| `coupon_code` | character varying | ✅ | - | 50 |
| `discount_percentage` | numeric | ✅ | - | - |
| `numero_da_venda` | integer | ✅ | - | - |

### Tabela: `vendas_na_hotmart`

**Registros:** 116,456

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `codigo_transacao` | text | ❌ | - | - |
| `status_transacao` | text | ✅ | - | - |
| `data_transacao` | text | ✅ | - | - |
| `confirmacao_pagamento` | character varying | ✅ | - | 1000 |
| `nome_produtor` | text | ✅ | - | - |
| `id_produto` | integer | ✅ | - | - |
| `nome_produto` | text | ✅ | - | - |
| `codigo_preco` | text | ✅ | - | - |
| `nome_preco` | text | ✅ | - | - |
| `moeda_compra` | text | ✅ | - | - |
| `valor_total_cobrado` | numeric | ✅ | - | - |
| `valor_base_da_compra` | numeric | ✅ | - | - |
| `moeda_recebimento` | text | ✅ | - | - |
| `valor_comissao_liquida` | numeric | ✅ | - | - |
| `venda_feita_como` | text | ✅ | - | - |
| `valor_comissao_produtor` | character varying | ✅ | - | 50 |
| `comissao_afiliado` | numeric | ✅ | - | - |
| `valor_comissao_coprodutor` | character varying | ✅ | - | 50 |
| `moeda_taxas` | text | ✅ | - | - |
| `taxa_processamento_porcentagem` | numeric | ✅ | - | - |
| `taxa_streaming` | numeric | ✅ | - | - |
| `taxa_valor_total` | numeric | ✅ | - | - |
| `nome_afiliado` | text | ✅ | - | - |
| `canal_venda` | text | ✅ | - | - |
| `codigo_src` | text | ✅ | - | - |
| `codigo_sck` | text | ✅ | - | - |
| `metodo_pagamento` | text | ✅ | - | - |
| `tipo_cobranca` | text | ✅ | - | - |
| `total_parcelas` | integer | ✅ | - | - |
| `quantidade_cobrancas` | integer | ✅ | - | - |
| `data_vencimento_voucher` | text | ✅ | - | - |
| `codigo_cupom` | text | ✅ | - | - |
| `periodo_gratuito_trial` | text | ✅ | - | - |
| `quantidade_itens` | integer | ✅ | - | - |
| `nome_comprador` | text | ✅ | - | - |
| `email_comprador` | text | ✅ | - | - |
| `pais_comprador` | text | ✅ | - | - |
| `telefone_comprador` | text | ✅ | - | - |
| `documento_comprador` | text | ✅ | - | - |
| `cep_comprador` | text | ✅ | - | - |
| `cidade_comprador` | text | ✅ | - | - |
| `estado_comprador` | text | ✅ | - | - |
| `endereco_comprador` | text | ✅ | - | - |
| `bairro_comprador` | text | ✅ | - | - |
| `numero_endereco_comprador` | text | ✅ | - | - |
| `complemento_endereco_comprador` | text | ✅ | - | - |
| `instagram_comprador` | text | ✅ | - | - |
| `codigo_assinante` | text | ✅ | - | - |
| `tipo_order_bump` | text | ✅ | - | - |
| `transacao_order_bump` | text | ✅ | - | - |
| `tipo_antecipacao_assinatura` | text | ✅ | - | - |
| `motivo_recusa_cartao` | text | ✅ | - | - |
| `taxa_parcelamento` | numeric | ✅ | - | - |
| `valor_frete_bruto` | numeric | ✅ | - | - |
| `numero_da_venda` | integer | ✅ | - | - |
| `data_vencimento_garantia` | timestamp without time zone | ✅ | - | - |
| `taxa_fixa_por_venda` | character varying | ✅ | - | 50 |
| `assinatura_simounao` | text | ✅ | - | - |
| `utm_source` | character varying | ✅ | - | 50 |
| `utm_medium` | character varying | ✅ | - | 50 |
| `utm_campaign` | character varying | ✅ | - | 50 |
| `utm_term` | character varying | ✅ | - | 50 |
| `utm_content` | character varying | ✅ | - | 50 |

### Tabela: `vendas_na_kiwify`

**Registros:** 58,056

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id_venda` | character varying | ❌ | - | 50 |
| `numero_da_venda` | integer | ✅ | - | - |
| `referencia_venda` | character varying | ✅ | - | 50 |
| `tipo_produto` | character varying | ✅ | - | 50 |
| `data_criacao` | timestamp without time zone | ✅ | - | - |
| `data_atualizacao` | timestamp without time zone | ✅ | - | - |
| `produto_id` | character varying | ✅ | - | 50 |
| `produto_nome` | character varying | ✅ | - | 255 |
| `produto_oferta_id` | character varying | ✅ | - | 50 |
| `produto_oferta_nome` | character varying | ✅ | - | 255 |
| `produto_plano_id` | character varying | ✅ | - | 50 |
| `produto_plano_nome` | character varying | ✅ | - | 255 |
| `envio_json` | text | ✅ | - | - |
| `envio_codigo_rastreamento` | character varying | ✅ | - | 255 |
| `status` | character varying | ✅ | - | 50 |
| `status_recebimento` | character varying | ✅ | - | 50 |
| `metodo_pagamento` | character varying | ✅ | - | 50 |
| `tipo_pagamento` | character varying | ✅ | - | 50 |
| `data_aprovacao` | timestamp without time zone | ✅ | - | - |
| `data_reembolso` | timestamp without time zone | ✅ | - | - |
| `pagamento_um_clique` | boolean | ✅ | - | - |
| `provedor_one_click` | character varying | ✅ | - | 255 |
| `parcelas` | integer | ✅ | - | - |
| `ultimos_digitos_cartao` | character varying | ✅ | - | 10 |
| `motivo_recusa` | character varying | ✅ | - | 1000 |
| `motivo_rejeicao_cartao` | text | ✅ | - | - |
| `tipo_cartao` | character varying | ✅ | - | 50 |
| `pagamento_dois_cartoes` | boolean | ✅ | - | - |
| `moeda` | character varying | ✅ | - | 10 |
| `valor_total_cobrado` | character varying | ✅ | - | 20 |
| `valor_do_acrescimo_dos_juros` | character varying | ✅ | - | 20 |
| `preco_base_produto` | character varying | ✅ | - | 20 |
| `valor_taxa_plataforma` | character varying | ✅ | - | 20 |
| `valor_comissao_afiliado` | character varying | ✅ | - | 20 |
| `valor_comissao_coprodutor` | character varying | ✅ | - | 20 |
| `valor_comissao_liquida` | character varying | ✅ | - | 20 |
| `url_boleto` | text | ✅ | - | - |
| `data_liberacao_estimada` | date | ✅ | - | - |
| `data_deposito` | date | ✅ | - | - |
| `tipo_venda` | character varying | ✅ | - | 50 |
| `id_pedido_pai` | character varying | ✅ | - | 50 |
| `cliente` | character varying | ✅ | - | 1000 |
| `cliente_id` | character varying | ✅ | - | 50 |
| `cliente_nome` | character varying | ✅ | - | 255 |
| `email` | character varying | ✅ | - | 255 |
| `cpf` | character varying | ✅ | - | 20 |
| `celular` | character varying | ✅ | - | 20 |
| `cliente_instagram` | character varying | ✅ | - | 255 |
| `pais` | character varying | ✅ | - | 50 |
| `endereco` | character varying | ✅ | - | 255 |
| `numero` | character varying | ✅ | - | 10 |
| `complemento` | character varying | ✅ | - | 255 |
| `bairro` | character varying | ✅ | - | 100 |
| `cidade` | character varying | ✅ | - | 100 |
| `estado` | character varying | ✅ | - | 50 |
| `cep` | character varying | ✅ | - | 20 |
| `ip` | character varying | ✅ | - | 50 |
| `tracking_sck` | character varying | ✅ | - | 1000 |
| `tracking_src` | character varying | ✅ | - | 1000 |
| `tracking_utm_source` | character varying | ✅ | - | 1000 |
| `tracking_utm_medium` | character varying | ✅ | - | 255 |
| `tracking_utm_campaign` | character varying | ✅ | - | 1000 |
| `tracking_utm_content` | character varying | ✅ | - | 1000 |
| `tracking_utm_term` | character varying | ✅ | - | 255 |
| `comissao_afiliado_valor` | character varying | ✅ | - | 20 |
| `comissao_afiliado_nome` | character varying | ✅ | - | 255 |
| `comissao_afiliado_email` | character varying | ✅ | - | 255 |
| `comissao_afiliado_documento` | character varying | ✅ | - | 1000 |
| `parceiros_receita` | text | ✅ | - | - |
| `desconto_codigo` | character varying | ✅ | - | 50 |
| `desconto_percentual` | character varying | ✅ | - | 20 |
| `kiwify_network` | character varying | ✅ | - | 255 |
| `id_nota_fiscal` | character varying | ✅ | - | 50 |
| `status_nota_fiscal` | character varying | ✅ | - | 50 |
| `nota_fiscal_emitida_por` | character varying | ✅ | - | 255 |
| `software_nota_fiscal` | character varying | ✅ | - | 255 |
| `valor_nota_fiscal` | character varying | ✅ | - | 20 |

### Tabela: `vendas_payt`

**Registros:** 8,411

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `codigo` | character varying | ❌ | - | 50 |
| `tags` | text | ✅ | - | - |
| `cliente` | character varying | ✅ | - | 255 |
| `tipo_venda` | character varying | ✅ | - | 100 |
| `sku` | character varying | ✅ | - | 100 |
| `produto` | character varying | ✅ | - | 255 |
| `quantidade_produtos` | integer | ✅ | - | - |
| `codigo_checkout` | character varying | ✅ | - | 50 |
| `nome_checkout` | character varying | ✅ | - | 255 |
| `source_venda_manual` | character varying | ✅ | - | 100 |
| `status_compra` | character varying | ✅ | - | 50 |
| `status_pagamento` | character varying | ✅ | - | 50 |
| `preco_produto` | numeric | ✅ | - | - |
| `valor_venda` | numeric | ✅ | - | - |
| `rede_afiliado` | character varying | ✅ | - | 255 |
| `afiliado` | character varying | ✅ | - | 255 |
| `custo_afiliado` | numeric | ✅ | - | - |
| `taxa_callcenter` | numeric | ✅ | - | - |
| `frete` | numeric | ✅ | - | - |
| `saldo_venda` | numeric | ✅ | - | - |
| `custo_coproducao` | numeric | ✅ | - | - |
| `custo_fornecedor` | numeric | ✅ | - | - |
| `voce_recebe` | numeric | ✅ | - | - |
| `saldo_disponivel_em` | date | ✅ | - | - |
| `parcelas` | integer | ✅ | - | - |
| `forma_pagamento` | character varying | ✅ | - | 100 |
| `codigo_cupom` | character varying | ✅ | - | 50 |
| `data` | timestamp without time zone | ✅ | - | - |
| `email` | character varying | ✅ | - | 255 |
| `documento` | character varying | ✅ | - | 50 |
| `cidade` | character varying | ✅ | - | 100 |
| `complemento` | character varying | ✅ | - | 255 |
| `bairro` | character varying | ✅ | - | 100 |
| `estado` | character varying | ✅ | - | 50 |
| `rua` | character varying | ✅ | - | 255 |
| `numero` | character varying | ✅ | - | 20 |
| `cep` | character varying | ✅ | - | 20 |
| `telefone` | character varying | ✅ | - | 20 |
| `codigo_rastreio` | character varying | ✅ | - | 100 |
| `url_acompanhamento` | text | ✅ | - | - |

### Tabela: `vw_central_joaocastanheira`

**Registros:** 351,851

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `cliente_id` | integer | ✅ | - | - |
| `email` | character varying | ✅ | - | 255 |
| `nome` | character varying | ✅ | - | 255 |
| `sobrenome` | character varying | ✅ | - | 255 |
| `documento` | character varying | ✅ | - | 50 |
| `telefone` | character varying | ✅ | - | 50 |
| `total_de_compras` | bigint | ✅ | - | - |
| `soma_valor_compras` | numeric | ✅ | - | - |
| `data_ultima_compra` | timestamp without time zone | ✅ | - | - |
| `lista_produtos_raiz` | ARRAY | ✅ | - | - |
| `lista_produtos_variacao` | ARRAY | ✅ | - | - |

## Schema joaocastanheira_bancodedados

**Resumo:**
- 📋 Total de tabelas: 24
- 📊 Total de registros: 162

### Tabela: `addresses`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.addresses_id_seq'::regclass) | - |
| `address` | character varying | ✅ | - | 255 |
| `neighborhood` | character varying | ✅ | - | 100 |
| `country` | character varying | ✅ | - | 100 |
| `city` | character varying | ✅ | - | 100 |
| `zip_code` | character varying | ✅ | - | 20 |
| `complement` | character varying | ✅ | - | 255 |
| `number` | character varying | ✅ | - | 20 |
| `ip` | character varying | ✅ | - | 45 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `state` | character varying | ✅ | - | 100 |

### Tabela: `api_field_mapping`

**Registros:** 145

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.api_field_mapping_id_seq'::regclass) | - |
| `platform_origin` | character varying | ❌ | - | 100 |
| `source_api_field` | character varying | ❌ | - | 255 |
| `destination_table` | character varying | ❌ | - | 100 |
| `destination_column` | character varying | ❌ | - | 100 |
| `mapping_notes` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `commission_participants`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.commission_participants_id_seq'::regclass) | - |
| `platform_id` | character varying | ❌ | - | 255 |
| `platform_origin` | character varying | ❌ | - | 100 |
| `email` | character varying | ✅ | - | 255 |
| `name` | character varying | ✅ | - | 255 |
| `trade_name` | character varying | ✅ | - | 255 |
| `locale` | character varying | ✅ | - | 20 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `phone_local_code` | character varying | ✅ | - | 10 |
| `phone_number` | character varying | ✅ | - | 20 |
| `document_type` | character varying | ✅ | - | 10 |
| `document_number` | character varying | ✅ | - | 50 |

### Tabela: `customer_external_ids`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.customer_external_ids_id_seq'::regclass) | - |
| `customer_id` | integer | ❌ | - | - |
| `platform_origin` | character varying | ❌ | - | 100 |
| `external_id` | character varying | ❌ | - | 255 |
| `match_type` | character varying | ✅ | 'EMAIL_MATCH'::character varying | 50 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `first_seen_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `last_seen_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `metadata` | jsonb | ✅ | - | - |

### Tabela: `customer_logs`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.customer_logs_id_seq'::regclass) | - |
| `customer_id` | integer | ❌ | - | - |
| `field_name` | character varying | ❌ | - | 100 |
| `old_value` | text | ✅ | - | - |
| `new_value` | text | ✅ | - | - |
| `changed_by` | character varying | ✅ | 'SYSTEM'::character varying | 100 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `customers`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.customers_id_seq'::regclass) | - |
| `email` | character varying | ✅ | - | 255 |
| `name` | character varying | ✅ | - | 255 |
| `address_id` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `phone_local_code` | character varying | ✅ | - | 10 |
| `phone_number` | character varying | ✅ | - | 20 |
| `document_type` | character varying | ✅ | - | 10 |
| `document_number` | character varying | ✅ | - | 50 |

### Tabela: `offers`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.offers_id_seq'::regclass) | - |
| `offer_id` | character varying | ❌ | - | 100 |
| `platform_origin` | character varying | ❌ | - | 100 |
| `name` | character varying | ✅ | - | 255 |
| `description` | text | ✅ | - | - |
| `plan_id` | integer | ✅ | - | - |
| `product_id` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `payment_mode` | character varying | ✅ | - | 50 |
| `price` | numeric | ✅ | - | - |
| `currency_code` | character varying | ✅ | - | 3 |

### Tabela: `participant_addresses`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.participant_addresses_id_seq'::regclass) | - |
| `participant_id` | integer | ❌ | - | - |
| `address` | character varying | ✅ | - | 255 |
| `neighborhood` | character varying | ✅ | - | 100 |
| `country` | character varying | ✅ | - | 100 |
| `city` | character varying | ✅ | - | 100 |
| `zip_code` | character varying | ✅ | - | 20 |
| `complement` | character varying | ✅ | - | 255 |
| `number` | character varying | ✅ | - | 20 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `state` | character varying | ✅ | - | 100 |

### Tabela: `plans`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.plans_id_seq'::regclass) | - |
| `plan_id` | character varying | ❌ | - | 100 |
| `platform_origin` | character varying | ❌ | - | 100 |
| `name` | character varying | ✅ | - | 255 |
| `description` | text | ✅ | - | - |
| `product_id` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `price` | numeric | ✅ | - | - |
| `currency_code` | character varying | ✅ | - | 3 |
| `recurrency_period` | integer | ✅ | - | - |
| `recurrency_type` | integer | ✅ | - | - |
| `trial_period` | integer | ✅ | - | - |
| `max_cycles` | integer | ✅ | - | - |
| `trial` | boolean | ❌ | false | - |
| `trial_end` | timestamp without time zone | ✅ | - | - |

### Tabela: `platform_commission`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.platform_commission_id_seq'::regclass) | - |
| `transaction_id` | integer | ❌ | - | - |
| `participant_id` | integer | ❌ | - | - |
| `amount` | numeric | ❌ | - | - |
| `currency_code` | character varying | ❌ | - | 3 |
| `commission_as` | character varying | ✅ | - | 100 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `exchange_rate` | character varying | ✅ | - | - |

### Tabela: `platform_sale_offer_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.platform_sale_offer_history_id_seq'::regclass) | - |
| `transaction_id` | integer | ✅ | - | - |
| `code` | character varying | ✅ | - | 100 |
| `offer_id` | character varying | ✅ | - | 100 |
| `offer_name` | character varying | ✅ | - | 255 |
| `description` | character varying | ✅ | - | 500 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_software_invoice_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.platform_software_invoice_history_id_seq'::regclass) | - |
| `transaction_id` | integer | ❌ | - | - |
| `invoice_number` | character varying | ✅ | - | 100 |
| `invoice_series` | character varying | ✅ | - | 20 |
| `invoice_key` | character varying | ✅ | - | 255 |
| `issue_date` | timestamp with time zone | ✅ | - | - |
| `status` | character varying | ✅ | - | 50 |
| `xml_url` | text | ✅ | - | - |
| `pdf_url` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_transaction_payment_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.platform_transaction_payment_history_id_seq'::regclass) | - |
| `transaction_id` | integer | ❌ | - | - |
| `payment_method` | USER-DEFINED | ✅ | - | - |
| `payment_type` | USER-DEFINED | ✅ | - | - |
| `installments` | integer | ✅ | - | - |
| `value` | numeric | ✅ | - | - |
| `payment_date` | timestamp with time zone | ✅ | - | - |
| `card_brand` | character varying | ✅ | - | 50 |
| `card_last_digits` | character varying | ✅ | - | 4 |
| `bank_slip_barcode` | text | ✅ | - | - |
| `pix_code` | text | ✅ | - | - |
| `metadata` | jsonb | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `platform_utm_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.platform_utm_history_id_seq'::regclass) | - |
| `transaction_id` | integer | ❌ | - | - |
| `utm_source` | character varying | ✅ | - | 255 |
| `utm_medium` | character varying | ✅ | - | 255 |
| `utm_campaign` | character varying | ✅ | - | 255 |
| `utm_term` | character varying | ✅ | - | 255 |
| `utm_content` | character varying | ✅ | - | 255 |
| `capture_date` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `src` | character varying | ✅ | - | 50 |
| `sck` | character varying | ✅ | - | 50 |

### Tabela: `products`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.products_id_seq'::regclass) | - |
| `product_id` | character varying | ❌ | - | 100 |
| `platform_origin` | character varying | ❌ | - | 100 |
| `name` | character varying | ✅ | - | 255 |
| `description` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `subscription_status_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.subscription_status_history_id_seq'::regclass) | - |
| `subscription_id` | integer | ❌ | - | - |
| `status_id` | integer | ❌ | - | - |
| `change_date` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `reason` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `subscriptions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.subscriptions_id_seq'::regclass) | - |
| `subscription_id` | character varying | ❌ | - | 100 |
| `subscriber_id` | character varying | ✅ | - | 100 |
| `last_transaction_id` | character varying | ✅ | - | 100 |
| `customer_id` | integer | ✅ | - | - |
| `plan_id` | integer | ✅ | - | - |
| `payment_gateway` | character varying | ❌ | - | 100 |
| `billing_cycle` | character varying | ✅ | - | 50 |
| `total_recurrences` | integer | ✅ | - | - |
| `max_cycles` | integer | ✅ | - | - |
| `last_update` | timestamp with time zone | ✅ | - | - |
| `start_date` | timestamp with time zone | ✅ | - | - |
| `end_date` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status_id` | integer | ✅ | - | - |
| `request_billet` | boolean | ✅ | false | - |
| `next_billing_date` | timestamp with time zone | ✅ | - | - |
| `cancellation_date` | timestamp with time zone | ✅ | - | - |
| `last_recurrency_number` | integer | ✅ | - | - |
| `has_credit_card_change` | boolean | ✅ | - | - |
| `has_unpaid_recurrency` | boolean | ✅ | - | - |
| `billing_type` | text | ✅ | - | - |
| `is_paid_anticipation` | boolean | ✅ | - | - |
| `is_paid_negotiation` | boolean | ✅ | - | - |
| `coupon_code` | character varying | ✅ | - | 255 |
| `last_recurrency_start_date` | bigint | ✅ | - | - |
| `payment_delays_days` | integer | ✅ | - | - |
| `transaction_type` | text | ✅ | - | - |
| `is_current_purchase` | boolean | ✅ | - | - |
| `has_retry` | boolean | ✅ | - | - |

### Tabela: `subscriptions_summary`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.subscriptions_summary_id_seq'::regclass) | - |
| `platform_origin` | character varying | ❌ | - | 100 |
| `subscription_origin_id` | integer | ❌ | - | - |
| `customer_id` | integer | ❌ | - | - |
| `plan_id` | integer | ✅ | - | - |
| `product_id` | integer | ✅ | - | - |
| `offer_id` | integer | ✅ | - | - |
| `status_id` | integer | ✅ | - | - |
| `platform_subscription_id` | character varying | ❌ | - | 255 |
| `platform_subscriber_code` | character varying | ✅ | - | 255 |
| `platform_subscriber_id` | character varying | ✅ | - | 255 |
| `platform_product_id` | character varying | ✅ | - | 100 |
| `platform_offer_code` | character varying | ✅ | - | 100 |
| `platform_last_transaction_id` | character varying | ✅ | - | 255 |
| `lifetime` | integer | ✅ | - | - |
| `accession_date` | timestamp with time zone | ✅ | - | - |
| `end_accession_date` | timestamp with time zone | ✅ | - | - |
| `trial` | boolean | ✅ | - | - |
| `plan_name` | character varying | ✅ | - | 255 |
| `product_name` | character varying | ✅ | - | 255 |
| `subscriber_name` | character varying | ✅ | - | 255 |
| `subscriber_email` | character varying | ✅ | - | 255 |
| `last_recurrency_number` | integer | ✅ | - | - |
| `last_recurrency_request_date` | timestamp with time zone | ✅ | - | - |
| `last_recurrency_status` | character varying | ✅ | - | 50 |
| `last_recurrency_billing_type` | character varying | ✅ | - | 50 |
| `unpaid_recurrency_number` | integer | ✅ | - | - |
| `unpaid_recurrency_charge_date` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `plan_recurrency_period` | integer | ✅ | - | - |
| `last_recurrency_transaction_number` | integer | ✅ | - | - |

### Tabela: `transaction_fees`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.transaction_fees_id_seq'::regclass) | - |
| `transaction_id` | integer | ❌ | - | - |
| `fee_type` | character varying | ❌ | - | 100 |
| `total_amount` | numeric | ❌ | - | - |
| `fee_currency_code` | character varying | ❌ | - | 3 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `base_amount` | numeric | ✅ | - | - |
| `fixed_amount` | numeric | ✅ | - | - |
| `percentage` | numeric | ✅ | - | - |

### Tabela: `transaction_items`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.transaction_items_id_seq'::regclass) | - |
| `transaction_id` | integer | ❌ | - | - |
| `offer_id` | integer | ✅ | - | - |
| `product_id` | integer | ❌ | - | - |
| `plan_id` | integer | ✅ | - | - |
| `quantity` | integer | ✅ | 1 | - |
| `unit_price` | numeric | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `transaction_status_history`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.transaction_status_history_id_seq'::regclass) | - |
| `transaction_id` | integer | ❌ | - | - |
| `status_id` | integer | ❌ | - | - |
| `change_date` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `reason` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `transaction_statuses`

**Registros:** 17

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.transaction_statuses_id_seq'::regclass) | - |
| `status` | character varying | ❌ | - | 50 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `transactions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('joaocastanheira_bancodedados.transactions_id_seq'::regclass) | - |
| `transaction_id` | character varying | ❌ | - | 100 |
| `customer_id` | integer | ✅ | - | - |
| `payment_gateway` | character varying | ❌ | - | 100 |
| `status_id` | integer | ✅ | - | - |
| `payment_type` | USER-DEFINED | ✅ | - | - |
| `payment_method` | USER-DEFINED | ✅ | - | - |
| `payment_engine` | character varying | ✅ | - | 100 |
| `installments_number` | integer | ✅ | - | - |
| `card_brand` | character varying | ✅ | - | 50 |
| `card_last_digits` | character varying | ✅ | - | 4 |
| `billet_url` | text | ✅ | - | - |
| `billet_barcode` | character varying | ✅ | - | 100 |
| `currency_code` | character varying | ❌ | 'BRL'::character varying | 3 |
| `base_price` | numeric | ✅ | - | - |
| `offer_price` | numeric | ❌ | - | - |
| `customer_paid_amount` | numeric | ✅ | - | - |
| `platform_fee_amount` | numeric | ✅ | 0 | - |
| `distributable_amount` | numeric | ✅ | - | - |
| `partner_commission_amount` | numeric | ✅ | 0 | - |
| `producer_net_amount` | numeric | ✅ | - | - |
| `is_subscription` | boolean | ✅ | false | - |
| `subscription_id` | integer | ✅ | - | - |
| `platform_subscription_id` | character varying | ✅ | - | 100 |
| `recurrency_number` | integer | ✅ | - | - |
| `tracking_source` | character varying | ✅ | - | 100 |
| `tracking_sck` | character varying | ✅ | - | 100 |
| `under_warranty` | boolean | ✅ | false | - |
| `warranty_expire_date` | timestamp with time zone | ✅ | - | - |
| `order_date` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `commission_as` | character varying | ✅ | - | 50 |
| `approved_date` | bigint | ✅ | - | - |
| `status` | text | ✅ | - | - |
| `installments_type` | text | ✅ | - | - |
| `payment_refusal_message` | text | ✅ | - | - |
| `refund_chargeback_date` | bigint | ✅ | - | - |
| `payment_billet_expiration_date` | bigint | ✅ | - | - |
| `payment_billet_recovery_type` | text | ✅ | - | - |
| `payment_pix_expiration_date` | bigint | ✅ | - | - |
| `payment_billet_reprint_code` | text | ✅ | - | - |
| `conversion_rate` | numeric | ✅ | - | - |

### Tabela: `vw_customers_with_platform_ids`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ✅ | - | - |
| `email` | character varying | ✅ | - | 255 |
| `name` | character varying | ✅ | - | 255 |
| `address_id` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | - | - |
| `phone_local_code` | character varying | ✅ | - | 10 |
| `phone_number` | character varying | ✅ | - | 20 |
| `document_type` | character varying | ✅ | - | 10 |
| `document_number` | character varying | ✅ | - | 50 |
| `platform_ids` | jsonb | ✅ | - | - |

## Schema modelo_saas_inicial

**Resumo:**
- 📋 Total de tabelas: 31
- 📊 Total de registros: 31

### Tabela: `campaign_contacts`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.campaign_contacts_id_seq'::regclass) | - |
| `campaign_id` | integer | ✅ | - | - |
| `contact_id` | integer | ✅ | - | - |
| `status` | character varying | ✅ | - | 30 |
| `last_interaction_at` | timestamp with time zone | ✅ | - | - |

### Tabela: `campaigns`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.campaigns_id_seq'::regclass) | - |
| `name` | character varying | ✅ | - | 100 |
| `campaign_type` | character varying | ✅ | - | 50 |
| `channel` | character varying | ✅ | - | 50 |
| `status` | character varying | ✅ | - | 30 |
| `start_date` | date | ✅ | - | - |
| `end_date` | date | ✅ | - | - |
| `created_by` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `contact_events`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.contact_events_id_seq'::regclass) | - |
| `contact_id` | integer | ✅ | - | - |
| `event_type` | character varying | ✅ | - | 100 |
| `event_data` | jsonb | ✅ | - | - |
| `page_url` | text | ✅ | - | - |
| `referrer` | text | ✅ | - | - |
| `occurred_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `contact_interactions`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.contact_interactions_id_seq'::regclass) | - |
| `contact_id` | integer | ✅ | - | - |
| `interaction_type` | character varying | ✅ | - | 50 |
| `channel` | character varying | ✅ | - | 50 |
| `provider` | character varying | ✅ | - | 100 |
| `content` | text | ✅ | - | - |
| `metadata` | jsonb | ✅ | - | - |
| `occurred_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `contact_list_memberships`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.contact_list_memberships_id_seq'::regclass) | - |
| `contact_id` | integer | ✅ | - | - |
| `contact_list_id` | integer | ✅ | - | - |
| `added_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `contact_lists`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.contact_lists_id_seq'::regclass) | - |
| `name` | character varying | ✅ | - | 100 |
| `description` | text | ✅ | - | - |
| `is_dynamic` | boolean | ✅ | false | - |
| `created_by` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `contact_notes`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.contact_notes_id_seq'::regclass) | - |
| `contact_id` | integer | ✅ | - | - |
| `note` | text | ✅ | - | - |
| `created_by` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `contact_sources`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.contact_sources_id_seq'::regclass) | - |
| `name` | character varying | ✅ | - | 100 |
| `description` | text | ✅ | - | - |
| `integration_type` | character varying | ✅ | - | 50 |
| `external_reference` | text | ✅ | - | - |

### Tabela: `contact_tags`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.contact_tags_id_seq'::regclass) | - |
| `contact_id` | integer | ✅ | - | - |
| `tag` | character varying | ✅ | - | 100 |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `contacts`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.contacts_id_seq'::regclass) | - |
| `email` | character varying | ✅ | - | 255 |
| `name` | character varying | ✅ | - | 255 |
| `phone` | character varying | ✅ | - | 30 |
| `status` | character varying | ✅ | 'lead'::character varying | 30 |
| `source` | character varying | ✅ | - | 100 |
| `utm_source` | character varying | ✅ | - | 100 |
| `utm_medium` | character varying | ✅ | - | 100 |
| `utm_campaign` | character varying | ✅ | - | 100 |
| `utm_content` | character varying | ✅ | - | 100 |
| `utm_term` | character varying | ✅ | - | 100 |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `converted_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | integer | ✅ | - | - |

### Tabela: `conversion_journeys`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.conversion_journeys_id_seq'::regclass) | - |
| `contact_id` | integer | ✅ | - | - |
| `started_at` | timestamp with time zone | ✅ | - | - |
| `converted_at` | timestamp with time zone | ✅ | - | - |
| `converted_to_tenant_id` | integer | ✅ | - | - |
| `funnel_stage` | character varying | ✅ | - | 100 |
| `source` | character varying | ✅ | - | 100 |

### Tabela: `coupons`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.coupons_id_seq'::regclass) | - |
| `code` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `discount_type` | character varying | ✅ | - | 20 |
| `discount_value` | numeric | ✅ | - | - |
| `currency` | character varying | ✅ | - | 10 |
| `duration` | character varying | ✅ | - | 20 |
| `months_duration` | integer | ✅ | - | - |
| `end_validity` | timestamp with time zone | ✅ | - | - |
| `usage_limit` | integer | ✅ | - | - |
| `usage_count` | integer | ✅ | 0 | - |
| `active` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `features`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.features_id_seq'::regclass) | - |
| `key` | character varying | ❌ | - | 100 |
| `name` | character varying | ❌ | - | 255 |

### Tabela: `invoices`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.invoices_id_seq'::regclass) | - |
| `tenant_id` | integer | ✅ | - | - |
| `subscription_id` | integer | ✅ | - | - |
| `provider_id` | integer | ✅ | - | - |
| `external_invoice_id` | character varying | ✅ | - | 255 |
| `external_charge_id` | character varying | ✅ | - | 255 |
| `amount` | numeric | ✅ | - | - |
| `currency` | character varying | ✅ | - | 10 |
| `description` | text | ✅ | - | - |
| `period_start` | timestamp with time zone | ✅ | - | - |
| `period_end` | timestamp with time zone | ✅ | - | - |
| `status` | character varying | ✅ | - | 30 |
| `issued_at` | timestamp with time zone | ✅ | now() | - |
| `due_at` | timestamp with time zone | ✅ | - | - |
| `paid_at` | timestamp with time zone | ✅ | - | - |
| `payment_method_id` | integer | ✅ | - | - |
| `attempts` | integer | ✅ | 0 | - |
| `coupon_id` | integer | ✅ | - | - |

### Tabela: `payment_customers`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.payment_customers_id_seq'::regclass) | - |
| `tenant_id` | integer | ✅ | - | - |
| `provider_id` | integer | ✅ | - | - |
| `external_customer_id` | character varying | ❌ | - | 255 |

### Tabela: `payment_methods`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.payment_methods_id_seq'::regclass) | - |
| `tenant_id` | integer | ✅ | - | - |
| `provider_id` | integer | ✅ | - | - |
| `external_method_id` | character varying | ❌ | - | 255 |
| `type` | character varying | ✅ | - | 50 |
| `details` | jsonb | ✅ | - | - |
| `is_default` | boolean | ✅ | false | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `payment_providers`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.payment_providers_id_seq'::regclass) | - |
| `name` | character varying | ❌ | - | 100 |
| `details_config` | jsonb | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `permissions`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.permissions_id_seq'::regclass) | - |
| `key` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |

### Tabela: `plan_entitlements`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.plan_entitlements_id_seq'::regclass) | - |
| `plan_id` | integer | ✅ | - | - |
| `key` | character varying | ✅ | - | 100 |
| `value` | character varying | ✅ | - | 255 |

### Tabela: `plan_features`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.plan_features_id_seq'::regclass) | - |
| `plan_id` | integer | ✅ | - | - |
| `feature_id` | integer | ✅ | - | - |
| `enabled` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `plan_provider_mappings`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.plan_provider_mappings_id_seq'::regclass) | - |
| `plan_id` | integer | ✅ | - | - |
| `provider_id` | integer | ✅ | - | - |
| `external_plan_id` | character varying | ✅ | - | 255 |
| `external_product_id` | character varying | ✅ | - | 255 |

### Tabela: `plans`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.plans_id_seq'::regclass) | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `price` | numeric | ✅ | - | - |
| `currency` | character varying | ✅ | 'USD'::character varying | 10 |
| `billing_interval` | character varying | ✅ | - | 20 |
| `trial_duration` | integer | ✅ | - | - |
| `is_active` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `role_permissions`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.role_permissions_id_seq'::regclass) | - |
| `role_id` | integer | ✅ | - | - |
| `permission_id` | integer | ✅ | - | - |
| `feature_id` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `roles`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.roles_id_seq'::regclass) | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |

### Tabela: `subscriptions`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.subscriptions_id_seq'::regclass) | - |
| `tenant_id` | integer | ✅ | - | - |
| `plan_id` | integer | ✅ | - | - |
| `provider_id` | integer | ✅ | - | - |
| `external_subscription_id` | character varying | ✅ | - | 255 |
| `status` | character varying | ✅ | - | 30 |
| `start_at` | timestamp with time zone | ✅ | - | - |
| `end_at` | timestamp with time zone | ✅ | - | - |
| `auto_renew` | boolean | ✅ | true | - |
| `trial_start` | timestamp with time zone | ✅ | - | - |
| `trial_end` | timestamp with time zone | ✅ | - | - |
| `next_charge_at` | timestamp with time zone | ✅ | - | - |
| `payment_method_id` | integer | ✅ | - | - |
| `coupon_id` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `tenants`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.tenants_id_seq'::regclass) | - |
| `name` | character varying | ❌ | - | 255 |
| `plan_id` | integer | ✅ | - | - |
| `status` | character varying | ✅ | 'active'::character varying | 30 |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `users`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.users_id_seq'::regclass) | - |
| `email` | character varying | ❌ | - | 255 |
| `name` | character varying | ✅ | - | 255 |
| `is_system_admin` | boolean | ✅ | false | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `webhook_logs`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.webhook_logs_id_seq'::regclass) | - |
| `provider_id` | integer | ✅ | - | - |
| `event_type` | character varying | ✅ | - | 100 |
| `payload` | jsonb | ✅ | - | - |
| `received_at` | timestamp with time zone | ✅ | now() | - |
| `processed_at` | timestamp with time zone | ✅ | - | - |
| `processing_status` | character varying | ✅ | 'pending'::character varying | 30 |

### Tabela: `workspace_features`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.workspace_features_id_seq'::regclass) | - |
| `workspace_id` | integer | ✅ | - | - |
| `feature_id` | integer | ✅ | - | - |
| `enabled` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `workspace_members`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.workspace_members_id_seq'::regclass) | - |
| `workspace_id` | integer | ✅ | - | - |
| `user_id` | integer | ✅ | - | - |
| `role_id` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `workspaces`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('modelo_saas_inicial.workspaces_id_seq'::regclass) | - |
| `tenant_id` | integer | ✅ | - | - |
| `name` | character varying | ✅ | - | 255 |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |

## Schema public

**Resumo:**
- 📋 Total de tabelas: 91
- 📊 Total de registros: 101

### Tabela: `agents`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `provider` | character varying | ❌ | - | 100 |
| `model` | character varying | ❌ | - | 100 |
| `system_prompt` | text | ✅ | - | - |
| `temperature` | numeric | ✅ | 0.7 | - |
| `max_tokens` | integer | ✅ | 1000 | - |
| `is_active` | boolean | ❌ | true | - |
| `user_id` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `personality` | text | ✅ | - | - |
| `instructions` | text | ✅ | - | - |
| `agent_type` | text | ✅ | - | - |
| `model_provider` | character varying | ✅ | - | 50 |
| `top_p` | double precision | ✅ | - | - |
| `frequency_penalty` | double precision | ✅ | - | - |
| `presence_penalty` | double precision | ✅ | - | - |
| `tools` | json | ✅ | - | - |
| `knowledge_base` | json | ✅ | - | - |
| `capabilities` | json | ✅ | - | - |
| `status` | text | ✅ | - | - |
| `avatar_url` | character varying | ✅ | - | 500 |
| `configuration` | json | ✅ | - | - |
| `conversation_count` | integer | ✅ | - | - |
| `message_count` | integer | ✅ | - | - |
| `total_tokens_used` | integer | ✅ | - | - |
| `average_response_time` | double precision | ✅ | - | - |
| `rating_average` | double precision | ✅ | - | - |
| `rating_count` | integer | ✅ | - | - |
| `last_active_at` | timestamp with time zone | ✅ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `priority` | integer | ✅ | 1 | - |
| `version` | character varying | ✅ | '1.0.0'::character varying | 20 |
| `environment` | character varying | ✅ | 'development'::character varying | 20 |

### Tabela: `alembic_version`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `version_num` | character varying | ❌ | - | 32 |

### Tabela: `analytics_alerts`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `condition` | jsonb | ❌ | - | - |
| `notification_config` | jsonb | ❌ | - | - |
| `is_active` | boolean | ❌ | true | - |
| `owner_id` | uuid | ❌ | - | - |
| `last_triggered_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |

### Tabela: `analytics_dashboards`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `icon` | character varying | ✅ | - | 50 |
| `color` | character varying | ✅ | - | 7 |
| `user_id` | uuid | ❌ | - | - |
| `layout` | json | ❌ | - | - |
| `widgets` | json | ❌ | - | - |
| `filters` | json | ✅ | - | - |
| `auto_refresh` | boolean | ❌ | - | - |
| `refresh_interval` | integer | ✅ | - | - |
| `is_public` | boolean | ❌ | false | - |
| `shared_with` | json | ✅ | - | - |
| `is_default` | boolean | ❌ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `last_viewed_at` | timestamp without time zone | ✅ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |

### Tabela: `analytics_events`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `event_id` | character varying | ❌ | - | 36 |
| `event_type` | character varying | ❌ | - | 100 |
| `category` | character varying | ❌ | - | 50 |
| `action` | character varying | ❌ | - | 100 |
| `label` | character varying | ✅ | - | 200 |
| `user_id` | uuid | ✅ | - | - |
| `session_id` | character varying | ✅ | - | 255 |
| `anonymous_id` | character varying | ✅ | - | 100 |
| `ip_address` | text | ✅ | - | - |
| `user_agent` | text | ✅ | - | - |
| `referrer` | character varying | ✅ | - | 1000 |
| `page_url` | character varying | ✅ | - | 1000 |
| `properties` | jsonb | ❌ | '{}'::jsonb | - |
| `value` | double precision | ✅ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `project_id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ✅ | - | - |
| `country` | character varying | ✅ | - | 2 |
| `region` | character varying | ✅ | - | 100 |
| `city` | character varying | ✅ | - | 100 |
| `timezone` | character varying | ✅ | - | 50 |
| `device_type` | character varying | ✅ | - | 20 |
| `os` | character varying | ✅ | - | 50 |
| `browser` | character varying | ✅ | - | 50 |
| `screen_resolution` | character varying | ✅ | - | 20 |
| `timestamp` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `analytics_exports`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `export_type` | character varying | ❌ | - | 50 |
| `query` | jsonb | ❌ | - | - |
| `file_path` | character varying | ✅ | - | 500 |
| `status` | character varying | ❌ | 'pending'::character varying | 20 |
| `owner_id` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |

### Tabela: `analytics_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `metric_name` | character varying | ❌ | - | 100 |
| `metric_value` | numeric | ❌ | - | - |
| `dimensions` | jsonb | ❌ | '{}'::jsonb | - |
| `timestamp` | timestamp with time zone | ❌ | now() | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `analytics_reports`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `query` | jsonb | ❌ | - | - |
| `schedule` | character varying | ✅ | - | 50 |
| `owner_id` | uuid | ❌ | - | - |
| `is_active` | boolean | ❌ | true | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `billing_events`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `user_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `event_type` | character varying | ❌ | - | 50 |
| `amount_usd` | double precision | ❌ | - | - |
| `description` | text | ✅ | - | - |
| `related_usage_log_id` | uuid | ✅ | - | - |
| `related_message_id` | uuid | ✅ | - | - |
| `invoice_id` | character varying | ✅ | - | 100 |
| `payment_provider` | character varying | ✅ | - | 50 |
| `payment_transaction_id` | character varying | ✅ | - | 100 |
| `billing_metadata` | json | ✅ | - | - |
| `status` | character varying | ✅ | 'pending'::character varying | 20 |
| `processed_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `business_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `date` | timestamp without time zone | ❌ | - | - |
| `period_type` | character varying | ❌ | - | 20 |
| `total_users` | integer | ❌ | - | - |
| `new_users` | integer | ❌ | - | - |
| `active_users` | integer | ❌ | - | - |
| `churned_users` | integer | ❌ | - | - |
| `total_sessions` | integer | ❌ | - | - |
| `avg_session_duration` | double precision | ❌ | - | - |
| `total_page_views` | integer | ❌ | - | - |
| `bounce_rate` | double precision | ❌ | - | - |
| `workflows_created` | integer | ❌ | - | - |
| `workflows_executed` | integer | ❌ | - | - |
| `components_published` | integer | ❌ | - | - |
| `components_downloaded` | integer | ❌ | - | - |
| `workspaces_created` | integer | ❌ | - | - |
| `teams_formed` | integer | ❌ | - | - |
| `collaborative_sessions` | integer | ❌ | - | - |
| `total_revenue` | double precision | ❌ | - | - |
| `recurring_revenue` | double precision | ❌ | - | - |
| `marketplace_revenue` | double precision | ❌ | - | - |
| `avg_revenue_per_user` | double precision | ❌ | - | - |
| `error_rate` | double precision | ❌ | - | - |
| `avg_response_time` | double precision | ❌ | - | - |
| `uptime_percentage` | double precision | ❌ | - | - |
| `customer_satisfaction` | double precision | ❌ | - | - |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `updated_at` | timestamp without time zone | ❌ | - | - |

### Tabela: `campaign_contacts`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `campaign_id` | uuid | ❌ | - | - |
| `contact_id` | uuid | ❌ | - | - |
| `status` | character varying | ✅ | 'pending'::character varying | 50 |
| `sent_at` | timestamp with time zone | ✅ | - | - |
| `opened_at` | timestamp with time zone | ✅ | - | - |
| `clicked_at` | timestamp with time zone | ✅ | - | - |
| `bounced_at` | timestamp with time zone | ✅ | - | - |
| `unsubscribed_at` | timestamp with time zone | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `campaigns`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `type` | character varying | ❌ | - | 50 |
| `status` | character varying | ✅ | 'draft'::character varying | 50 |
| `subject` | character varying | ✅ | - | 255 |
| `content` | text | ✅ | - | - |
| `template_id` | uuid | ✅ | - | - |
| `scheduled_at` | timestamp with time zone | ✅ | - | - |
| `sent_at` | timestamp with time zone | ✅ | - | - |
| `stats` | jsonb | ✅ | '{}'::jsonb | - |
| `settings` | jsonb | ✅ | '{}'::jsonb | - |
| `created_by` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `component_downloads`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `component_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `version` | character varying | ❌ | - | 20 |
| `download_type` | character varying | ❌ | - | 20 |
| `ip_address` | character varying | ✅ | - | 45 |
| `user_agent` | character varying | ✅ | - | 500 |
| `referrer` | character varying | ✅ | - | 500 |
| `status` | character varying | ❌ | - | 20 |
| `file_size` | integer | ✅ | - | - |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `completed_at` | timestamp without time zone | ✅ | - | - |

### Tabela: `component_purchases`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `component_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `amount` | double precision | ❌ | - | - |
| `currency` | character varying | ❌ | - | 3 |
| `payment_method` | character varying | ✅ | - | 50 |
| `transaction_id` | character varying | ❌ | - | 100 |
| `payment_provider` | character varying | ✅ | - | 50 |
| `provider_transaction_id` | character varying | ✅ | - | 100 |
| `status` | character varying | ❌ | - | 20 |
| `license_key` | character varying | ✅ | - | 100 |
| `license_expires_at` | timestamp without time zone | ✅ | - | - |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `completed_at` | timestamp without time zone | ✅ | - | - |
| `refunded_at` | timestamp without time zone | ✅ | - | - |

### Tabela: `component_ratings`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `component_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `rating` | integer | ❌ | - | - |
| `title` | character varying | ✅ | - | 200 |
| `review` | text | ✅ | - | - |
| `ease_of_use` | integer | ✅ | - | - |
| `documentation_quality` | integer | ✅ | - | - |
| `performance` | integer | ✅ | - | - |
| `reliability` | integer | ✅ | - | - |
| `support_quality` | integer | ✅ | - | - |
| `version_used` | character varying | ✅ | - | 20 |
| `use_case` | character varying | ✅ | - | 100 |
| `experience_level` | character varying | ✅ | - | 20 |
| `helpful_count` | integer | ❌ | - | - |
| `reported_count` | integer | ❌ | - | - |
| `is_verified_purchase` | boolean | ❌ | - | - |
| `is_featured` | boolean | ❌ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `updated_at` | timestamp without time zone | ❌ | - | - |

### Tabela: `component_versions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `component_id` | uuid | ❌ | - | - |
| `version` | character varying | ❌ | - | 20 |
| `is_latest` | boolean | ❌ | - | - |
| `is_stable` | boolean | ❌ | - | - |
| `changelog` | text | ✅ | - | - |
| `breaking_changes` | text | ✅ | - | - |
| `migration_guide` | text | ✅ | - | - |
| `component_data` | json | ❌ | - | - |
| `file_size` | integer | ✅ | - | - |
| `min_platform_version` | character varying | ✅ | - | 20 |
| `max_platform_version` | character varying | ✅ | - | 20 |
| `dependencies` | json | ✅ | - | - |
| `download_count` | integer | ❌ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `deprecated_at` | timestamp without time zone | ✅ | - | - |

### Tabela: `contact_events`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `contact_id` | uuid | ❌ | - | - |
| `event_type` | character varying | ❌ | - | 100 |
| `event_data` | jsonb | ✅ | '{}'::jsonb | - |
| `occurred_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `contact_interactions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `contact_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ✅ | - | - |
| `type` | character varying | ❌ | - | 50 |
| `channel` | character varying | ✅ | - | 50 |
| `subject` | character varying | ✅ | - | 255 |
| `content` | text | ✅ | - | - |
| `direction` | character varying | ✅ | 'outbound'::character varying | 20 |
| `status` | character varying | ✅ | 'completed'::character varying | 50 |
| `scheduled_at` | timestamp with time zone | ✅ | - | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `contact_list_memberships`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `list_id` | uuid | ❌ | - | - |
| `contact_id` | uuid | ❌ | - | - |
| `added_by` | uuid | ✅ | - | - |
| `added_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 50 |

### Tabela: `contact_lists`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `type` | character varying | ✅ | 'static'::character varying | 50 |
| `filters` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `contact_notes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `contact_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `content` | text | ❌ | - | - |
| `type` | character varying | ✅ | 'note'::character varying | 50 |
| `is_private` | boolean | ✅ | false | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `contact_sources`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `integration_type` | character varying | ✅ | - | 50 |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `is_active` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `contact_tags`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `color` | character varying | ✅ | '#6B7280'::character varying | 7 |
| `description` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `contacts`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `email` | character varying | ❌ | - | 255 |
| `first_name` | character varying | ✅ | - | 100 |
| `last_name` | character varying | ✅ | - | 100 |
| `phone` | character varying | ✅ | - | 50 |
| `company` | character varying | ✅ | - | 255 |
| `job_title` | character varying | ✅ | - | 255 |
| `status` | character varying | ✅ | 'active'::character varying | 50 |
| `lead_score` | integer | ✅ | 0 | - |
| `source_id` | uuid | ✅ | - | - |
| `custom_fields` | jsonb | ✅ | '{}'::jsonb | - |
| `tags` | ARRAY | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `conversion_journeys`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `contact_id` | uuid | ❌ | - | - |
| `tenant_id` | uuid | ❌ | - | - |
| `journey_name` | character varying | ✅ | - | 255 |
| `current_stage` | character varying | ✅ | - | 100 |
| `stages_completed` | jsonb | ✅ | '[]'::jsonb | - |
| `conversion_probability` | numeric | ✅ | - | - |
| `last_interaction_at` | timestamp with time zone | ✅ | - | - |
| `converted_at` | timestamp with time zone | ✅ | - | - |
| `conversion_value` | numeric | ✅ | - | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `coupons`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `code` | character varying | ❌ | - | 100 |
| `name` | character varying | ✅ | - | 255 |
| `description` | text | ✅ | - | - |
| `type` | character varying | ❌ | 'percentage'::character varying | 50 |
| `value` | numeric | ❌ | - | - |
| `currency` | character varying | ✅ | 'USD'::character varying | 3 |
| `max_uses` | integer | ✅ | - | - |
| `used_count` | integer | ✅ | 0 | - |
| `min_amount` | numeric | ✅ | - | - |
| `max_discount` | numeric | ✅ | - | - |
| `valid_from` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `valid_until` | timestamp with time zone | ✅ | - | - |
| `is_active` | boolean | ✅ | true | - |
| `is_stackable` | boolean | ✅ | false | - |
| `applicable_plans` | jsonb | ✅ | '[]'::jsonb | - |
| `restrictions` | jsonb | ✅ | '{}'::jsonb | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_by` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `custom_reports`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `name` | character varying | ❌ | - | 200 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ✅ | - | 50 |
| `query_config` | json | ❌ | - | - |
| `visualization_config` | json | ✅ | - | - |
| `filters` | json | ✅ | - | - |
| `is_scheduled` | boolean | ❌ | - | - |
| `schedule_config` | json | ✅ | - | - |
| `last_run_at` | timestamp without time zone | ✅ | - | - |
| `next_run_at` | timestamp without time zone | ✅ | - | - |
| `is_public` | boolean | ❌ | - | - |
| `shared_with` | json | ✅ | - | - |
| `cached_data` | json | ✅ | - | - |
| `cache_expires_at` | timestamp without time zone | ✅ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `updated_at` | timestamp without time zone | ❌ | - | - |

### Tabela: `email_verification_tokens`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `token` | character varying | ❌ | - | 500 |
| `user_id` | uuid | ❌ | - | - |
| `expires_at` | timestamp with time zone | ❌ | - | - |
| `is_used` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `features`

**Registros:** 15

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `key` | character varying | ❌ | - | 100 |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ✅ | - | 100 |
| `is_active` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `version` | character varying | ✅ | '1.0.0'::character varying | 20 |
| `release_date` | date | ✅ | CURRENT_DATE | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `configuration` | jsonb | ✅ | '{}'::jsonb | - |

### Tabela: `files`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `filename` | character varying | ❌ | - | 255 |
| `original_name` | character varying | ❌ | - | 255 |
| `file_path` | character varying | ❌ | - | 500 |
| `file_size` | integer | ❌ | - | - |
| `mime_type` | character varying | ❌ | - | 100 |
| `category` | character varying | ❌ | - | 50 |
| `is_public` | boolean | ❌ | false | - |
| `user_id` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tags` | json | ✅ | - | - |
| `description` | text | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `scan_status` | character varying | ✅ | 'pending'::character varying | 20 |
| `access_count` | integer | ✅ | 0 | - |
| `last_accessed_at` | timestamp with time zone | ✅ | - | - |

### Tabela: `invoices`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `subscription_id` | uuid | ✅ | - | - |
| `invoice_number` | character varying | ❌ | - | 100 |
| `status` | character varying | ❌ | 'draft'::character varying | 50 |
| `currency` | character varying | ❌ | 'USD'::character varying | 3 |
| `subtotal` | numeric | ❌ | 0 | - |
| `tax_amount` | numeric | ❌ | 0 | - |
| `discount_amount` | numeric | ❌ | 0 | - |
| `total_amount` | numeric | ❌ | 0 | - |
| `due_date` | date | ✅ | - | - |
| `paid_at` | timestamp with time zone | ✅ | - | - |
| `items` | jsonb | ✅ | '[]'::jsonb | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `llms`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `name` | character varying | ❌ | - | 100 |
| `provider` | character varying | ❌ | - | 50 |
| `model_version` | character varying | ✅ | - | 50 |
| `cost_per_token_input` | double precision | ❌ | 0.0 | - |
| `cost_per_token_output` | double precision | ❌ | 0.0 | - |
| `max_tokens_supported` | integer | ✅ | - | - |
| `supports_function_calling` | boolean | ✅ | false | - |
| `supports_vision` | boolean | ✅ | false | - |
| `supports_streaming` | boolean | ✅ | true | - |
| `context_window` | integer | ✅ | - | - |
| `is_active` | boolean | ✅ | true | - |
| `llm_metadata` | json | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `health_status` | character varying | ✅ | 'unknown'::character varying | 20 |
| `response_time_avg_ms` | integer | ✅ | 0 | - |
| `availability_percentage` | numeric | ✅ | 99.9 | - |

### Tabela: `llms_conversations`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `agent_id` | uuid | ✅ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `title` | character varying | ✅ | - | 255 |
| `status` | character varying | ✅ | - | 50 |
| `message_count` | integer | ✅ | - | - |
| `total_tokens_used` | integer | ✅ | - | - |
| `context` | json | ✅ | - | - |
| `settings` | json | ✅ | - | - |
| `last_message_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `llms_conversations_turns`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `conversation_id` | uuid | ❌ | - | - |
| `llm_id` | uuid | ❌ | - | - |
| `first_used_at` | timestamp with time zone | ❌ | now() | - |
| `last_used_at` | timestamp with time zone | ❌ | now() | - |
| `message_count` | integer | ✅ | 0 | - |
| `total_input_tokens` | integer | ✅ | 0 | - |
| `total_output_tokens` | integer | ✅ | 0 | - |
| `total_cost_usd` | double precision | ✅ | 0.0 | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `llms_message_feedbacks`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `message_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `rating_type` | character varying | ❌ | - | 20 |
| `rating_value` | integer | ✅ | - | - |
| `feedback_text` | text | ✅ | - | - |
| `feedback_category` | character varying | ✅ | - | 50 |
| `improvement_suggestions` | text | ✅ | - | - |
| `is_public` | boolean | ✅ | false | - |
| `feedback_metadata` | json | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `llms_messages`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `conversation_id` | uuid | ❌ | - | - |
| `role` | character varying | ❌ | - | 20 |
| `content` | text | ❌ | - | - |
| `attachments` | json | ✅ | - | - |
| `model_used` | character varying | ✅ | - | 100 |
| `model_provider` | character varying | ✅ | - | 50 |
| `tokens_used` | integer | ✅ | - | - |
| `processing_time_ms` | integer | ✅ | - | - |
| `temperature` | double precision | ✅ | - | - |
| `max_tokens` | integer | ✅ | - | - |
| `status` | character varying | ✅ | - | 50 |
| `error_message` | text | ✅ | - | - |
| `rating` | integer | ✅ | - | - |
| `feedback` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `llms_usage_logs`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `message_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `conversation_id` | uuid | ❌ | - | - |
| `llm_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `input_tokens` | integer | ❌ | 0 | - |
| `output_tokens` | integer | ❌ | 0 | - |
| `total_tokens` | integer | ❌ | 0 | - |
| `cost_usd` | double precision | ❌ | 0.0 | - |
| `latency_ms` | integer | ✅ | - | - |
| `api_status_code` | integer | ✅ | - | - |
| `api_request_payload` | json | ✅ | - | - |
| `api_response_metadata` | json | ✅ | - | - |
| `user_api_key_used` | boolean | ✅ | false | - |
| `model_settings` | json | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `status` | character varying | ✅ | 'success'::character varying | 20 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `marketplace_components`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ❌ | - | 100 |
| `component_type` | character varying | ❌ | - | 50 |
| `tags` | text | ✅ | - | - |
| `price` | numeric | ❌ | 0.00 | - |
| `is_free` | boolean | ❌ | true | - |
| `author_id` | uuid | ❌ | - | - |
| `version` | character varying | ❌ | '1.0.0'::character varying | 50 |
| `content` | text | ✅ | - | - |
| `component_metadata` | text | ✅ | - | - |
| `downloads_count` | integer | ❌ | 0 | - |
| `rating_average` | double precision | ❌ | - | - |
| `rating_count` | integer | ❌ | - | - |
| `is_featured` | boolean | ❌ | false | - |
| `is_approved` | boolean | ❌ | false | - |
| `status` | character varying | ❌ | 'pending'::character varying | 20 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `title` | character varying | ❌ | - | 200 |
| `short_description` | character varying | ✅ | - | 500 |
| `subcategory` | character varying | ✅ | - | 50 |
| `author_name` | character varying | ❌ | - | 100 |
| `organization` | character varying | ✅ | - | 100 |
| `configuration_schema` | json | ✅ | - | - |
| `dependencies` | json | ✅ | - | - |
| `compatibility` | json | ✅ | - | - |
| `documentation` | text | ✅ | - | - |
| `readme` | text | ✅ | - | - |
| `changelog` | text | ✅ | - | - |
| `examples` | json | ✅ | - | - |
| `icon_url` | character varying | ✅ | - | 500 |
| `screenshots` | json | ✅ | - | - |
| `demo_url` | character varying | ✅ | - | 500 |
| `video_url` | character varying | ✅ | - | 500 |
| `currency` | character varying | ✅ | - | 3 |
| `license_type` | character varying | ✅ | - | 50 |
| `install_count` | integer | ❌ | - | - |
| `view_count` | integer | ❌ | - | - |
| `like_count` | integer | ❌ | - | - |
| `is_verified` | boolean | ❌ | - | - |
| `moderation_notes` | text | ✅ | - | - |
| `keywords` | json | ✅ | - | - |
| `search_vector` | text | ✅ | - | - |
| `popularity_score` | double precision | ❌ | - | - |
| `published_at` | timestamp without time zone | ✅ | - | - |
| `last_download_at` | timestamp without time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `node_categories`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `icon` | character varying | ✅ | - | 10 |
| `color` | character varying | ✅ | - | 7 |
| `parent_id` | uuid | ✅ | - | - |
| `sort_order` | integer | ✅ | - | - |
| `is_active` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `node_executions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `execution_id` | character varying | ✅ | - | 36 |
| `workflow_execution_id` | uuid | ❌ | - | - |
| `node_id` | uuid | ❌ | - | - |
| `node_key` | character varying | ❌ | - | 255 |
| `node_type` | character varying | ❌ | - | 100 |
| `node_name` | character varying | ✅ | - | 255 |
| `status` | text | ✅ | - | - |
| `execution_order` | integer | ❌ | - | - |
| `input_data` | json | ✅ | - | - |
| `output_data` | json | ✅ | - | - |
| `config_data` | json | ✅ | - | - |
| `started_at` | timestamp with time zone | ✅ | - | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `timeout_at` | timestamp with time zone | ✅ | - | - |
| `duration_ms` | integer | ✅ | - | - |
| `execution_log` | text | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `error_details` | json | ✅ | - | - |
| `debug_info` | json | ✅ | - | - |
| `retry_count` | integer | ✅ | - | - |
| `max_retries` | integer | ✅ | - | - |
| `retry_delay` | integer | ✅ | - | - |
| `dependencies` | json | ✅ | - | - |
| `dependents` | json | ✅ | - | - |
| `meta_data` | json | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `priority` | integer | ✅ | 1 | - |

### Tabela: `node_ratings`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `node_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `rating` | integer | ❌ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `node_templates`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 200 |
| `description` | text | ✅ | - | - |
| `type` | text | ❌ | 'operation'::text | - |
| `category` | character varying | ✅ | - | 100 |
| `code_template` | text | ❌ | - | - |
| `input_schema` | json | ❌ | - | - |
| `output_schema` | json | ❌ | - | - |
| `parameters_schema` | json | ✅ | - | - |
| `icon` | character varying | ✅ | - | 10 |
| `color` | character varying | ✅ | - | 7 |
| `documentation` | text | ✅ | - | - |
| `examples` | json | ✅ | - | - |
| `is_system` | boolean | ✅ | - | - |
| `is_active` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `nodes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `category` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `version` | character varying | ❌ | '1.0.0'::character varying | 50 |
| `definition` | jsonb | ❌ | - | - |
| `is_public` | boolean | ❌ | false | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `code_template` | text | ❌ | - | - |
| `input_schema` | json | ❌ | - | - |
| `output_schema` | json | ❌ | - | - |
| `parameters_schema` | json | ✅ | - | - |
| `icon` | character varying | ✅ | - | 10 |
| `color` | character varying | ✅ | - | 7 |
| `documentation` | text | ✅ | - | - |
| `examples` | json | ✅ | - | - |
| `downloads_count` | integer | ✅ | - | - |
| `usage_count` | integer | ✅ | - | - |
| `rating_average` | integer | ✅ | - | - |
| `rating_count` | integer | ✅ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `type` | text | ❌ | 'operation'::text | - |
| `status` | text | ❌ | 'draft'::text | - |
| `timeout_seconds` | integer | ✅ | 300 | - |
| `retry_count` | integer | ✅ | 3 | - |

### Tabela: `password_reset_tokens`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `token` | character varying | ❌ | - | 500 |
| `user_id` | uuid | ❌ | - | - |
| `expires_at` | timestamp with time zone | ❌ | - | - |
| `is_used` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `payment_customers`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `provider_id` | uuid | ❌ | - | - |
| `external_customer_id` | character varying | ❌ | - | 255 |
| `customer_data` | jsonb | ✅ | '{}'::jsonb | - |
| `is_active` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `payment_methods`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `customer_id` | uuid | ❌ | - | - |
| `external_method_id` | character varying | ❌ | - | 255 |
| `type` | character varying | ❌ | - | 50 |
| `last4` | character varying | ✅ | - | 4 |
| `brand` | character varying | ✅ | - | 50 |
| `exp_month` | integer | ✅ | - | - |
| `exp_year` | integer | ✅ | - | - |
| `is_default` | boolean | ✅ | false | - |
| `is_active` | boolean | ✅ | true | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `payment_providers`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `name` | character varying | ❌ | - | 100 |
| `display_name` | character varying | ❌ | - | 255 |
| `is_active` | boolean | ✅ | true | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `webhook_secret` | character varying | ✅ | - | 255 |
| `api_version` | character varying | ✅ | - | 50 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `performance_metrics`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `metric_type` | text | ✅ | - | - |
| `daily_active_users` | bigint | ✅ | - | - |
| `weekly_active_users` | bigint | ✅ | - | - |
| `monthly_active_users` | bigint | ✅ | - | - |
| `avg_login_count` | numeric | ✅ | - | - |

### Tabela: `plan_entitlements`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `plan_id` | uuid | ❌ | - | - |
| `feature_id` | uuid | ❌ | - | - |
| `limit_value` | integer | ✅ | - | - |
| `is_unlimited` | boolean | ✅ | false | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `plan_features`

**Registros:** 60

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `plan_id` | uuid | ❌ | - | - |
| `feature_id` | uuid | ❌ | - | - |
| `is_enabled` | boolean | ✅ | true | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `plan_provider_mappings`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `plan_id` | uuid | ❌ | - | - |
| `provider_id` | uuid | ❌ | - | - |
| `external_plan_id` | character varying | ❌ | - | 255 |
| `external_price_id` | character varying | ✅ | - | 255 |
| `is_active` | boolean | ✅ | true | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `plans`

**Registros:** 4

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `slug` | character varying | ❌ | - | 50 |
| `type` | text | ❌ | - | - |
| `description` | text | ✅ | - | - |
| `price_monthly` | double precision | ❌ | 0.0 | - |
| `price_yearly` | double precision | ❌ | 0.0 | - |
| `max_workspaces` | integer | ❌ | 1 | - |
| `max_members_per_workspace` | integer | ❌ | 1 | - |
| `max_projects_per_workspace` | integer | ❌ | 10 | - |
| `max_storage_mb` | integer | ❌ | 100 | - |
| `max_executions_per_month` | integer | ❌ | 100 | - |
| `allow_collaborative_workspaces` | boolean | ❌ | false | - |
| `allow_custom_domains` | boolean | ❌ | false | - |
| `allow_api_access` | boolean | ❌ | false | - |
| `allow_advanced_analytics` | boolean | ❌ | false | - |
| `allow_priority_support` | boolean | ❌ | false | - |
| `features` | json | ✅ | - | - |
| `restrictions` | json | ✅ | - | - |
| `is_active` | boolean | ❌ | true | - |
| `is_public` | boolean | ❌ | true | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `version` | character varying | ✅ | '1.0.0'::character varying | 20 |
| `sort_order` | integer | ✅ | 0 | - |

### Tabela: `project_collaborators`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `project_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `can_edit` | boolean | ❌ | - | - |
| `can_comment` | boolean | ❌ | - | - |
| `can_share` | boolean | ❌ | - | - |
| `can_delete` | boolean | ❌ | - | - |
| `is_online` | boolean | ❌ | - | - |
| `current_cursor_position` | json | ✅ | - | - |
| `last_edit_at` | timestamp without time zone | ✅ | - | - |
| `added_at` | timestamp without time zone | ❌ | - | - |
| `last_seen_at` | timestamp without time zone | ❌ | - | - |

### Tabela: `project_comments`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `project_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `parent_id` | uuid | ✅ | - | - |
| `content` | text | ❌ | - | - |
| `content_type` | character varying | ❌ | - | 20 |
| `node_id` | character varying | ✅ | - | 36 |
| `position_x` | double precision | ✅ | - | - |
| `position_y` | double precision | ✅ | - | - |
| `is_resolved` | boolean | ❌ | - | - |
| `is_edited` | boolean | ❌ | - | - |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `updated_at` | timestamp without time zone | ❌ | - | - |
| `resolved_at` | timestamp without time zone | ✅ | - | - |

### Tabela: `project_versions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `project_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `version_number` | integer | ❌ | - | - |
| `version_name` | character varying | ✅ | - | 100 |
| `description` | text | ✅ | - | - |
| `workflow_data` | json | ❌ | - | - |
| `changes_summary` | json | ✅ | - | - |
| `file_size` | integer | ✅ | - | - |
| `checksum` | character varying | ✅ | - | 64 |
| `is_major` | boolean | ❌ | - | - |
| `is_auto_save` | boolean | ❌ | - | - |
| `created_at` | timestamp without time zone | ❌ | - | - |

### Tabela: `rbac_permissions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `key` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ✅ | - | 100 |
| `resource` | character varying | ✅ | - | 100 |
| `action` | character varying | ✅ | - | 100 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `rbac_role_permissions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `role_id` | uuid | ❌ | - | - |
| `permission_id` | uuid | ❌ | - | - |
| `granted` | boolean | ✅ | true | - |
| `conditions` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `rbac_roles`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `is_system` | boolean | ✅ | false | - |
| `permissions` | jsonb | ✅ | '[]'::jsonb | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `refresh_tokens`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `token` | character varying | ❌ | - | 500 |
| `user_id` | uuid | ❌ | - | - |
| `expires_at` | timestamp with time zone | ❌ | - | - |
| `is_revoked` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `report_executions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `report_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ✅ | - | - |
| `execution_type` | character varying | ❌ | - | 20 |
| `parameters` | json | ✅ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `result_data` | json | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `execution_time_ms` | integer | ✅ | - | - |
| `rows_processed` | integer | ✅ | - | - |
| `data_size_bytes` | integer | ✅ | - | - |
| `started_at` | timestamp without time zone | ❌ | - | - |
| `completed_at` | timestamp without time zone | ✅ | - | - |

### Tabela: `subscriptions`

**Registros:** 4

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `plan_id` | uuid | ❌ | - | - |
| `provider_id` | uuid | ✅ | - | - |
| `external_subscription_id` | character varying | ✅ | - | 255 |
| `status` | character varying | ❌ | 'active'::character varying | 50 |
| `current_period_start` | timestamp with time zone | ✅ | - | - |
| `current_period_end` | timestamp with time zone | ✅ | - | - |
| `trial_start` | timestamp with time zone | ✅ | - | - |
| `trial_end` | timestamp with time zone | ✅ | - | - |
| `cancel_at_period_end` | boolean | ✅ | false | - |
| `canceled_at` | timestamp with time zone | ✅ | - | - |
| `ended_at` | timestamp with time zone | ✅ | - | - |
| `payment_method_id` | uuid | ✅ | - | - |
| `coupon_id` | uuid | ✅ | - | - |
| `quantity` | integer | ✅ | 1 | - |
| `discount_amount` | numeric | ✅ | 0 | - |
| `tax_percent` | numeric | ✅ | 0 | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `system_health_overview`

**Registros:** 4

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `component` | text | ✅ | - | - |
| `total` | bigint | ✅ | - | - |
| `active` | bigint | ✅ | - | - |
| `inactive` | bigint | ✅ | - | - |
| `errors` | bigint | ✅ | - | - |

### Tabela: `system_performance_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `metric_name` | character varying | ❌ | - | 100 |
| `metric_type` | character varying | ❌ | - | 20 |
| `service` | character varying | ❌ | - | 50 |
| `environment` | character varying | ❌ | - | 20 |
| `value` | double precision | ❌ | - | - |
| `unit` | character varying | ✅ | - | 20 |
| `tags` | json | ✅ | - | - |
| `timestamp` | timestamp without time zone | ❌ | - | - |

### Tabela: `tags`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `target_type` | character varying | ❌ | - | 50 |
| `target_id` | uuid | ❌ | - | - |
| `tag_name` | character varying | ❌ | - | 100 |
| `tag_value` | text | ✅ | - | - |
| `tag_category` | character varying | ✅ | - | 50 |
| `is_system_tag` | boolean | ✅ | false | - |
| `created_by_user_id` | uuid | ✅ | - | - |
| `auto_generated` | boolean | ✅ | false | - |
| `confidence_score` | double precision | ✅ | - | - |
| `tag_metadata` | json | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `template_collections`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `collection_id` | character varying | ✅ | - | 36 |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `creator_id` | uuid | ❌ | - | - |
| `is_public` | boolean | ✅ | - | - |
| `is_featured` | boolean | ✅ | - | - |
| `template_ids` | json | ❌ | - | - |
| `tags` | json | ✅ | - | - |
| `thumbnail_url` | character varying | ✅ | - | 500 |
| `view_count` | integer | ✅ | - | - |
| `follow_count` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `template_downloads`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `template_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `download_type` | character varying | ✅ | - | 20 |
| `ip_address` | character varying | ✅ | - | 45 |
| `user_agent` | character varying | ✅ | - | 500 |
| `template_version` | character varying | ✅ | - | 20 |
| `downloaded_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `template_favorites`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `template_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `notes` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `template_reviews`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `template_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `rating` | integer | ❌ | - | - |
| `title` | character varying | ✅ | - | 255 |
| `comment` | text | ✅ | - | - |
| `ease_of_use` | integer | ✅ | - | - |
| `documentation_quality` | integer | ✅ | - | - |
| `performance` | integer | ✅ | - | - |
| `value_for_money` | integer | ✅ | - | - |
| `is_verified_purchase` | boolean | ✅ | - | - |
| `is_helpful_count` | integer | ✅ | - | - |
| `is_reported` | boolean | ✅ | - | - |
| `version_reviewed` | character varying | ✅ | - | 20 |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `template_usage`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `template_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ✅ | - | - |
| `usage_type` | character varying | ❌ | - | 20 |
| `success` | boolean | ✅ | - | - |
| `template_version` | character varying | ✅ | - | 20 |
| `modifications_made` | json | ✅ | - | - |
| `execution_time` | integer | ✅ | - | - |
| `ip_address` | character varying | ✅ | - | 45 |
| `user_agent` | character varying | ✅ | - | 500 |
| `used_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `tenant_features`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `feature_id` | uuid | ❌ | - | - |
| `is_enabled` | boolean | ✅ | true | - |
| `usage_count` | integer | ✅ | 0 | - |
| `limit_value` | integer | ✅ | - | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `expires_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `tenants`

**Registros:** 4

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `name` | character varying | ❌ | - | 255 |
| `slug` | character varying | ❌ | - | 100 |
| `domain` | character varying | ✅ | - | 255 |
| `status` | character varying | ❌ | 'active'::character varying | 50 |
| `settings` | jsonb | ✅ | '{}'::jsonb | - |
| `extra_metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `user_behavior_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `date` | timestamp without time zone | ❌ | - | - |
| `period_type` | character varying | ❌ | - | 20 |
| `session_count` | integer | ❌ | - | - |
| `total_session_duration` | integer | ❌ | - | - |
| `avg_session_duration` | double precision | ❌ | - | - |
| `page_views` | integer | ❌ | - | - |
| `unique_pages_visited` | integer | ❌ | - | - |
| `workflows_created` | integer | ❌ | - | - |
| `workflows_executed` | integer | ❌ | - | - |
| `components_used` | integer | ❌ | - | - |
| `collaborations_initiated` | integer | ❌ | - | - |
| `marketplace_purchases` | integer | ❌ | - | - |
| `revenue_generated` | double precision | ❌ | - | - |
| `components_published` | integer | ❌ | - | - |
| `error_count` | integer | ❌ | - | - |
| `support_tickets` | integer | ❌ | - | - |
| `feature_requests` | integer | ❌ | - | - |
| `engagement_score` | double precision | ❌ | - | - |
| `satisfaction_score` | double precision | ❌ | - | - |
| `value_score` | double precision | ❌ | - | - |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `updated_at` | timestamp without time zone | ❌ | - | - |

### Tabela: `user_insights`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `insight_type` | character varying | ❌ | - | 50 |
| `category` | character varying | ❌ | - | 50 |
| `priority` | character varying | ❌ | - | 20 |
| `title` | character varying | ❌ | - | 200 |
| `description` | text | ❌ | - | - |
| `recommendation` | text | ✅ | - | - |
| `supporting_data` | json | ✅ | - | - |
| `confidence_score` | double precision | ❌ | - | - |
| `suggested_action` | character varying | ✅ | - | 100 |
| `action_url` | character varying | ✅ | - | 500 |
| `action_data` | json | ✅ | - | - |
| `is_read` | boolean | ❌ | - | - |
| `is_dismissed` | boolean | ❌ | - | - |
| `is_acted_upon` | boolean | ❌ | - | - |
| `user_feedback` | character varying | ✅ | - | 20 |
| `expires_at` | timestamp without time zone | ✅ | - | - |
| `is_evergreen` | boolean | ❌ | - | - |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `read_at` | timestamp without time zone | ✅ | - | - |
| `acted_at` | timestamp without time zone | ✅ | - | - |

### Tabela: `user_subscriptions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `plan_id` | uuid | ❌ | - | - |
| `status` | text | ❌ | 'active'::text | - |
| `started_at` | timestamp with time zone | ❌ | now() | - |
| `expires_at` | timestamp with time zone | ✅ | - | - |
| `cancelled_at` | timestamp with time zone | ✅ | - | - |
| `payment_method` | character varying | ✅ | - | 50 |
| `payment_provider` | character varying | ✅ | - | 50 |
| `external_subscription_id` | character varying | ✅ | - | 255 |
| `billing_cycle` | character varying | ✅ | 'monthly'::character varying | 20 |
| `current_period_start` | timestamp with time zone | ✅ | - | - |
| `current_period_end` | timestamp with time zone | ✅ | - | - |
| `current_workspaces` | integer | ❌ | 0 | - |
| `current_storage_mb` | double precision | ❌ | 0.0 | - |
| `current_executions_this_month` | integer | ❌ | 0 | - |
| `subscription_metadata` | json | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `user_tenant_roles`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `user_id` | uuid | ❌ | - | - |
| `tenant_id` | uuid | ❌ | - | - |
| `role_id` | uuid | ❌ | - | - |
| `granted_by` | uuid | ✅ | - | - |
| `granted_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `expires_at` | timestamp with time zone | ✅ | - | - |
| `is_active` | boolean | ✅ | true | - |
| `conditions` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `user_variables`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `key` | character varying | ❌ | - | 255 |
| `value` | text | ❌ | - | - |
| `is_secret` | boolean | ❌ | false | - |
| `user_id` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `category` | character varying | ✅ | - | 100 |
| `description` | text | ✅ | - | - |
| `is_encrypted` | boolean | ❌ | false | - |
| `is_active` | boolean | ❌ | true | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `users`

**Registros:** 4

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `email` | character varying | ❌ | - | 255 |
| `username` | character varying | ❌ | - | 255 |
| `hashed_password` | character varying | ❌ | - | 255 |
| `full_name` | character varying | ❌ | - | 200 |
| `is_active` | boolean | ✅ | - | - |
| `is_verified` | boolean | ✅ | - | - |
| `is_superuser` | boolean | ✅ | - | - |
| `profile_image_url` | character varying | ✅ | - | 500 |
| `bio` | character varying | ✅ | - | 1000 |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `last_login_at` | timestamp with time zone | ✅ | - | - |
| `login_count` | integer | ✅ | 0 | - |
| `failed_login_attempts` | integer | ✅ | 0 | - |
| `account_locked_until` | timestamp with time zone | ✅ | - | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `preferences` | jsonb | ✅ | '{}'::jsonb | - |
| `settings` | jsonb | ✅ | '{}'::jsonb | - |

### Tabela: `webhook_logs`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `provider_id` | uuid | ❌ | - | - |
| `event_type` | character varying | ❌ | - | 100 |
| `event_id` | character varying | ✅ | - | 255 |
| `payload` | jsonb | ❌ | - | - |
| `headers` | jsonb | ✅ | '{}'::jsonb | - |
| `status` | character varying | ✅ | 'pending'::character varying | 50 |
| `processed_at` | timestamp with time zone | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `retry_count` | integer | ✅ | 0 | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `workflow_connections`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ❌ | - | - |
| `source_node_id` | uuid | ❌ | - | - |
| `target_node_id` | uuid | ❌ | - | - |
| `source_port` | character varying | ✅ | - | 100 |
| `target_port` | character varying | ✅ | - | 100 |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |

### Tabela: `workflow_execution_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `workflow_execution_id` | uuid | ❌ | - | - |
| `node_execution_id` | integer | ✅ | - | - |
| `metric_type` | character varying | ❌ | - | 100 |
| `metric_name` | character varying | ❌ | - | 255 |
| `value_numeric` | integer | ✅ | - | - |
| `value_float` | character varying | ✅ | - | 50 |
| `value_text` | text | ✅ | - | - |
| `value_json` | json | ✅ | - | - |
| `context` | character varying | ✅ | - | 255 |
| `tags` | json | ✅ | - | - |
| `measured_at` | timestamp with time zone | ✅ | now() | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `workflow_execution_queue`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `queue_id` | character varying | ✅ | - | 36 |
| `workflow_execution_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `priority` | integer | ✅ | - | - |
| `scheduled_at` | timestamp with time zone | ✅ | - | - |
| `started_at` | timestamp with time zone | ✅ | - | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `status` | character varying | ✅ | - | 50 |
| `worker_id` | character varying | ✅ | - | 100 |
| `max_execution_time` | integer | ✅ | - | - |
| `retry_count` | integer | ✅ | - | - |
| `max_retries` | integer | ✅ | - | - |
| `meta_data` | json | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `workflow_executions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `execution_id` | character varying | ✅ | - | 36 |
| `workflow_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `status` | character varying | ❌ | 'pending'::character varying | 20 |
| `priority` | integer | ✅ | - | - |
| `input_data` | jsonb | ✅ | - | - |
| `output_data` | jsonb | ✅ | - | - |
| `context_data` | json | ✅ | - | - |
| `variables` | json | ✅ | - | - |
| `total_nodes` | integer | ✅ | - | - |
| `completed_nodes` | integer | ✅ | - | - |
| `failed_nodes` | integer | ✅ | - | - |
| `progress_percentage` | integer | ✅ | - | - |
| `started_at` | timestamp with time zone | ❌ | now() | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `timeout_at` | timestamp with time zone | ✅ | - | - |
| `estimated_duration` | integer | ✅ | - | - |
| `actual_duration` | integer | ✅ | - | - |
| `execution_log` | text | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `error_details` | json | ✅ | - | - |
| `debug_info` | json | ✅ | - | - |
| `retry_count` | integer | ✅ | - | - |
| `max_retries` | integer | ✅ | - | - |
| `auto_retry` | boolean | ✅ | - | - |
| `notify_on_completion` | boolean | ✅ | - | - |
| `notify_on_failure` | boolean | ✅ | - | - |
| `tags` | json | ✅ | - | - |
| `meta_data` | json | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `workflow_nodes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ❌ | - | - |
| `node_id` | uuid | ❌ | - | - |
| `instance_name` | character varying | ✅ | - | 200 |
| `position_x` | integer | ❌ | - | - |
| `position_y` | integer | ❌ | - | - |
| `configuration` | json | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |

### Tabela: `workflow_templates`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ❌ | - | 100 |
| `tags` | json | ✅ | - | - |
| `workflow_definition` | jsonb | ❌ | - | - |
| `preview_image` | character varying | ✅ | - | 500 |
| `author_id` | uuid | ❌ | - | - |
| `version` | character varying | ❌ | '1.0.0'::character varying | 50 |
| `is_public` | boolean | ❌ | false | - |
| `is_featured` | boolean | ❌ | false | - |
| `downloads_count` | integer | ❌ | 0 | - |
| `rating_average` | numeric | ❌ | 0.00 | - |
| `rating_count` | integer | ❌ | 0 | - |
| `price` | numeric | ❌ | 0.00 | - |
| `is_free` | boolean | ❌ | true | - |
| `license` | character varying | ❌ | 'MIT'::character varying | 50 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `title` | character varying | ❌ | - | 255 |
| `short_description` | character varying | ✅ | - | 500 |
| `original_workflow_id` | uuid | ✅ | - | - |
| `status` | character varying | ✅ | - | 20 |
| `is_verified` | boolean | ✅ | - | - |
| `license_type` | character varying | ✅ | - | 20 |
| `workflow_data` | json | ❌ | - | - |
| `nodes_data` | json | ❌ | - | - |
| `connections_data` | json | ✅ | - | - |
| `required_variables` | json | ✅ | - | - |
| `optional_variables` | json | ✅ | - | - |
| `default_config` | json | ✅ | - | - |
| `compatibility_version` | character varying | ✅ | - | 20 |
| `estimated_duration` | integer | ✅ | - | - |
| `complexity_level` | integer | ✅ | - | - |
| `download_count` | integer | ✅ | - | - |
| `usage_count` | integer | ✅ | - | - |
| `view_count` | integer | ✅ | - | - |
| `keywords` | json | ✅ | - | - |
| `use_cases` | json | ✅ | - | - |
| `industries` | json | ✅ | - | - |
| `thumbnail_url` | character varying | ✅ | - | 500 |
| `preview_images` | json | ✅ | - | - |
| `demo_video_url` | character varying | ✅ | - | 500 |
| `documentation` | text | ✅ | - | - |
| `setup_instructions` | text | ✅ | - | - |
| `changelog` | json | ✅ | - | - |
| `support_email` | character varying | ✅ | - | 255 |
| `repository_url` | character varying | ✅ | - | 500 |
| `documentation_url` | character varying | ✅ | - | 500 |
| `published_at` | timestamp with time zone | ✅ | - | - |
| `last_used_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `workflows`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `definition` | jsonb | ❌ | - | - |
| `is_active` | boolean | ❌ | true | - |
| `user_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `is_public` | boolean | ✅ | - | - |
| `category` | character varying | ✅ | - | 100 |
| `tags` | json | ✅ | - | - |
| `version` | character varying | ✅ | - | 20 |
| `status` | text | ✅ | - | - |
| `thumbnail_url` | character varying | ✅ | - | 500 |
| `downloads_count` | integer | ✅ | - | - |
| `rating_average` | integer | ✅ | - | - |
| `rating_count` | integer | ✅ | - | - |
| `execution_count` | integer | ✅ | - | - |
| `last_executed_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `priority` | integer | ✅ | 1 | - |
| `timeout_seconds` | integer | ✅ | 3600 | - |
| `retry_count` | integer | ✅ | 3 | - |

### Tabela: `workspace_activities`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `action` | character varying | ❌ | - | 50 |
| `resource_type` | character varying | ❌ | - | 50 |
| `resource_id` | character varying | ✅ | - | 255 |
| `description` | character varying | ❌ | - | 500 |
| `meta_data` | json | ✅ | - | - |
| `ip_address` | character varying | ✅ | - | 45 |
| `user_agent` | character varying | ✅ | - | 500 |
| `created_at` | timestamp without time zone | ❌ | - | - |

### Tabela: `workspace_features`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `workspace_id` | uuid | ❌ | - | - |
| `feature_id` | uuid | ❌ | - | - |
| `is_enabled` | boolean | ✅ | true | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `usage_count` | integer | ✅ | 0 | - |
| `limit_value` | integer | ✅ | - | - |
| `expires_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `workspace_invitations`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ❌ | - | - |
| `inviter_id` | uuid | ❌ | - | - |
| `invited_user_id` | uuid | ✅ | - | - |
| `email` | character varying | ❌ | - | 255 |
| `role` | text | ❌ | - | - |
| `message` | text | ✅ | - | - |
| `token` | character varying | ❌ | - | 100 |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `expires_at` | timestamp without time zone | ❌ | - | - |
| `responded_at` | timestamp without time zone | ✅ | - | - |

### Tabela: `workspace_members`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | - | - |
| `workspace_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `role` | text | ❌ | - | - |
| `custom_permissions` | json | ✅ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `is_favorite` | boolean | ❌ | - | - |
| `notification_preferences` | json | ✅ | - | - |
| `last_seen_at` | timestamp without time zone | ❌ | - | - |
| `joined_at` | timestamp without time zone | ❌ | - | - |
| `left_at` | timestamp without time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `workspace_projects`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `color` | character varying | ✅ | - | 7 |
| `allow_concurrent_editing` | boolean | ❌ | - | - |
| `auto_save_interval` | integer | ✅ | - | - |
| `version_control_enabled` | boolean | ❌ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `is_template` | boolean | ❌ | - | - |
| `is_public` | boolean | ❌ | - | - |
| `collaborator_count` | integer | ❌ | - | - |
| `edit_count` | integer | ❌ | - | - |
| `comment_count` | integer | ❌ | - | - |
| `created_at` | timestamp without time zone | ❌ | - | - |
| `updated_at` | timestamp without time zone | ❌ | - | - |
| `last_edited_at` | timestamp without time zone | ❌ | - | - |

### Tabela: `workspaces`

**Registros:** 4

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `slug` | character varying | ❌ | - | 120 |
| `description` | text | ✅ | - | - |
| `avatar_url` | character varying | ✅ | - | 500 |
| `color` | character varying | ✅ | - | 7 |
| `owner_id` | uuid | ❌ | - | - |
| `is_public` | boolean | ❌ | false | - |
| `is_template` | boolean | ❌ | - | - |
| `allow_guest_access` | boolean | ❌ | - | - |
| `require_approval` | boolean | ❌ | - | - |
| `max_members` | integer | ✅ | - | - |
| `max_projects` | integer | ✅ | - | - |
| `max_storage_mb` | integer | ✅ | - | - |
| `enable_real_time_editing` | boolean | ❌ | - | - |
| `enable_comments` | boolean | ❌ | - | - |
| `enable_chat` | boolean | ❌ | - | - |
| `enable_video_calls` | boolean | ❌ | - | - |
| `notification_settings` | json | ✅ | - | - |
| `member_count` | integer | ❌ | - | - |
| `project_count` | integer | ❌ | - | - |
| `activity_count` | integer | ❌ | - | - |
| `storage_used_mb` | double precision | ❌ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `last_activity_at` | timestamp without time zone | ❌ | - | - |
| `type` | text | ❌ | 'INDIVIDUAL'::text | - |
| `plan_id` | uuid | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `configuration` | jsonb | ✅ | '{}'::jsonb | - |

## Schema synapscale_db

**Resumo:**
- 📋 Total de tabelas: 103
- 📊 Total de registros: 357

### Tabela: `agent_acl`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `agent_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `can_read` | boolean | ❌ | true | - |
| `can_write` | boolean | ❌ | false | - |

### Tabela: `agent_configurations`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `config_id` | uuid | ❌ | gen_random_uuid() | - |
| `agent_id` | uuid | ❌ | - | - |
| `version_num` | integer | ❌ | - | - |
| `params` | jsonb | ❌ | - | - |
| `created_by` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `agent_error_logs`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `error_id` | uuid | ❌ | gen_random_uuid() | - |
| `agent_id` | uuid | ❌ | - | - |
| `occurred_at` | timestamp with time zone | ❌ | now() | - |
| `error_code` | text | ✅ | - | - |
| `payload` | jsonb | ✅ | - | - |

### Tabela: `agent_hierarchy`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `ancestor` | uuid | ❌ | - | - |
| `descendant` | uuid | ❌ | - | - |
| `depth` | integer | ❌ | - | - |

### Tabela: `agent_kbs`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `agent_id` | uuid | ❌ | - | - |
| `kb_id` | uuid | ❌ | - | - |
| `config` | jsonb | ❌ | '{}'::jsonb | - |

### Tabela: `agent_models`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `agent_id` | uuid | ❌ | - | - |
| `llm_id` | uuid | ❌ | - | - |
| `override` | jsonb | ❌ | '{}'::jsonb | - |

### Tabela: `agent_quotas`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `quota_id` | uuid | ❌ | gen_random_uuid() | - |
| `agent_id` | uuid | ❌ | - | - |
| `tenant_id` | uuid | ❌ | - | - |
| `max_calls` | bigint | ❌ | - | - |
| `max_tokens` | bigint | ❌ | - | - |
| `period` | interval | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `agent_tools`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `agent_id` | uuid | ❌ | - | - |
| `tool_id` | uuid | ❌ | - | - |
| `config` | jsonb | ❌ | '{}'::jsonb | - |

### Tabela: `agent_triggers`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `trigger_id` | uuid | ❌ | gen_random_uuid() | - |
| `agent_id` | uuid | ❌ | - | - |
| `trigger_type` | USER-DEFINED | ❌ | - | - |
| `cron_expr` | text | ✅ | - | - |
| `event_name` | text | ✅ | - | - |
| `active` | boolean | ❌ | true | - |
| `last_run_at` | timestamp with time zone | ✅ | - | - |

### Tabela: `agent_usage_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `metric_id` | uuid | ❌ | gen_random_uuid() | - |
| `agent_id` | uuid | ❌ | - | - |
| `period_start` | timestamp with time zone | ❌ | - | - |
| `period_end` | timestamp with time zone | ❌ | - | - |
| `calls_count` | bigint | ❌ | - | - |
| `tokens_used` | bigint | ❌ | - | - |
| `cost_est` | numeric | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `agents`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `is_active` | boolean | ❌ | true | - |
| `user_id` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `workspace_id` | uuid | ✅ | - | - |
| `tenant_id` | uuid | ❌ | - | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `priority` | integer | ✅ | 1 | - |
| `version` | character varying | ✅ | '1.0.0'::character varying | 20 |
| `environment` | character varying | ✅ | 'development'::character varying | 20 |
| `current_config` | uuid | ✅ | - | - |

### Tabela: `alembic_version`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `version_num` | character varying | ❌ | - | 32 |

### Tabela: `analytics_alerts`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `condition` | jsonb | ❌ | - | - |
| `notification_config` | jsonb | ❌ | - | - |
| `is_active` | boolean | ❌ | true | - |
| `owner_id` | uuid | ❌ | - | - |
| `last_triggered_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `analytics_dashboards`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `icon` | character varying | ✅ | - | 50 |
| `color` | character varying | ✅ | - | 7 |
| `user_id` | uuid | ❌ | - | - |
| `layout` | jsonb | ❌ | - | - |
| `widgets` | jsonb | ❌ | - | - |
| `filters` | jsonb | ✅ | - | - |
| `auto_refresh` | boolean | ❌ | - | - |
| `refresh_interval` | integer | ✅ | - | - |
| `is_public` | boolean | ❌ | false | - |
| `shared_with` | jsonb | ✅ | - | - |
| `is_default` | boolean | ❌ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `last_viewed_at` | timestamp with time zone | ✅ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `analytics_events`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `event_id` | character varying | ❌ | - | 36 |
| `event_type` | character varying | ❌ | - | 100 |
| `category` | character varying | ❌ | - | 50 |
| `action` | character varying | ❌ | - | 100 |
| `label` | character varying | ✅ | - | 200 |
| `user_id` | uuid | ✅ | - | - |
| `session_id` | character varying | ✅ | - | 255 |
| `anonymous_id` | character varying | ✅ | - | 100 |
| `ip_address` | text | ✅ | - | - |
| `user_agent` | text | ✅ | - | - |
| `referrer` | character varying | ✅ | - | 1000 |
| `page_url` | character varying | ✅ | - | 1000 |
| `properties` | jsonb | ❌ | '{}'::jsonb | - |
| `value` | double precision | ✅ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `project_id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ✅ | - | - |
| `country` | character varying | ✅ | - | 2 |
| `region` | character varying | ✅ | - | 100 |
| `city` | character varying | ✅ | - | 100 |
| `timezone` | character varying | ✅ | - | 50 |
| `device_type` | character varying | ✅ | - | 20 |
| `os` | character varying | ✅ | - | 50 |
| `browser` | character varying | ✅ | - | 50 |
| `screen_resolution` | character varying | ✅ | - | 20 |
| `timestamp` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `analytics_exports`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `export_type` | character varying | ❌ | - | 50 |
| `query` | jsonb | ❌ | - | - |
| `file_path` | character varying | ✅ | - | 500 |
| `status` | character varying | ❌ | 'pending'::character varying | 20 |
| `owner_id` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `analytics_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `metric_name` | character varying | ❌ | - | 100 |
| `metric_value` | numeric | ❌ | - | - |
| `dimensions` | jsonb | ❌ | '{}'::jsonb | - |
| `timestamp` | timestamp with time zone | ❌ | now() | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `analytics_reports`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `query` | jsonb | ❌ | - | - |
| `schedule` | character varying | ✅ | - | 50 |
| `owner_id` | uuid | ❌ | - | - |
| `is_active` | boolean | ❌ | true | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `audit_log`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `audit_id` | uuid | ❌ | gen_random_uuid() | - |
| `table_name` | text | ❌ | - | - |
| `record_id` | uuid | ❌ | - | - |
| `changed_by` | uuid | ✅ | - | - |
| `changed_at` | timestamp with time zone | ❌ | now() | - |
| `operation` | text | ❌ | - | - |
| `diffs` | jsonb | ✅ | - | - |

### Tabela: `billing_events`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `user_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `event_type` | character varying | ❌ | - | 50 |
| `amount_usd` | double precision | ❌ | - | - |
| `description` | text | ✅ | - | - |
| `related_usage_log_id` | uuid | ✅ | - | - |
| `related_message_id` | uuid | ✅ | - | - |
| `invoice_id` | character varying | ✅ | - | 100 |
| `payment_provider` | character varying | ✅ | - | 50 |
| `payment_transaction_id` | character varying | ✅ | - | 100 |
| `billing_metadata` | jsonb | ✅ | - | - |
| `status` | character varying | ✅ | 'pending'::character varying | 20 |
| `processed_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `business_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.business_metrics_id_seq'::regclass) | - |
| `date` | timestamp with time zone | ❌ | - | - |
| `period_type` | character varying | ❌ | - | 20 |
| `total_users` | integer | ❌ | - | - |
| `new_users` | integer | ❌ | - | - |
| `active_users` | integer | ❌ | - | - |
| `churned_users` | integer | ❌ | - | - |
| `total_sessions` | integer | ❌ | - | - |
| `avg_session_duration` | double precision | ❌ | - | - |
| `total_page_views` | integer | ❌ | - | - |
| `bounce_rate` | double precision | ❌ | - | - |
| `workflows_created` | integer | ❌ | - | - |
| `workflows_executed` | integer | ❌ | - | - |
| `components_published` | integer | ❌ | - | - |
| `components_downloaded` | integer | ❌ | - | - |
| `workspaces_created` | integer | ❌ | - | - |
| `teams_formed` | integer | ❌ | - | - |
| `collaborative_sessions` | integer | ❌ | - | - |
| `total_revenue` | double precision | ❌ | - | - |
| `recurring_revenue` | double precision | ❌ | - | - |
| `marketplace_revenue` | double precision | ❌ | - | - |
| `avg_revenue_per_user` | double precision | ❌ | - | - |
| `error_rate` | double precision | ❌ | - | - |
| `avg_response_time` | double precision | ❌ | - | - |
| `uptime_percentage` | double precision | ❌ | - | - |
| `customer_satisfaction` | double precision | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `updated_at` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `campaign_contacts`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `campaign_id` | uuid | ❌ | - | - |
| `contact_id` | uuid | ❌ | - | - |
| `status` | character varying | ✅ | 'pending'::character varying | 50 |
| `sent_at` | timestamp with time zone | ✅ | - | - |
| `opened_at` | timestamp with time zone | ✅ | - | - |
| `clicked_at` | timestamp with time zone | ✅ | - | - |
| `bounced_at` | timestamp with time zone | ✅ | - | - |
| `unsubscribed_at` | timestamp with time zone | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `campaigns`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `type` | character varying | ❌ | - | 50 |
| `status` | character varying | ✅ | 'draft'::character varying | 50 |
| `subject` | character varying | ✅ | - | 255 |
| `content` | text | ✅ | - | - |
| `template_id` | uuid | ✅ | - | - |
| `scheduled_at` | timestamp with time zone | ✅ | - | - |
| `sent_at` | timestamp with time zone | ✅ | - | - |
| `stats` | jsonb | ✅ | '{}'::jsonb | - |
| `settings` | jsonb | ✅ | '{}'::jsonb | - |
| `created_by` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `component_downloads`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `component_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `version` | character varying | ❌ | - | 20 |
| `download_type` | character varying | ❌ | - | 20 |
| `ip_address` | character varying | ✅ | - | 45 |
| `user_agent` | character varying | ✅ | - | 500 |
| `referrer` | character varying | ✅ | - | 500 |
| `status` | character varying | ❌ | - | 20 |
| `file_size` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `component_purchases`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `component_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `amount` | double precision | ❌ | - | - |
| `currency` | character varying | ❌ | - | 3 |
| `payment_method` | character varying | ✅ | - | 50 |
| `transaction_id` | character varying | ❌ | - | 100 |
| `payment_provider` | character varying | ✅ | - | 50 |
| `provider_transaction_id` | character varying | ✅ | - | 100 |
| `status` | character varying | ❌ | - | 20 |
| `license_key` | character varying | ✅ | - | 100 |
| `license_expires_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `refunded_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `component_ratings`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `component_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `rating` | integer | ❌ | - | - |
| `title` | character varying | ✅ | - | 200 |
| `review` | text | ✅ | - | - |
| `ease_of_use` | integer | ✅ | - | - |
| `documentation_quality` | integer | ✅ | - | - |
| `performance` | integer | ✅ | - | - |
| `reliability` | integer | ✅ | - | - |
| `support_quality` | integer | ✅ | - | - |
| `version_used` | character varying | ✅ | - | 20 |
| `use_case` | character varying | ✅ | - | 100 |
| `experience_level` | character varying | ✅ | - | 20 |
| `helpful_count` | integer | ❌ | - | - |
| `reported_count` | integer | ❌ | - | - |
| `is_verified_purchase` | boolean | ❌ | - | - |
| `is_featured` | boolean | ❌ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `updated_at` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `component_versions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `component_id` | uuid | ❌ | - | - |
| `version` | character varying | ❌ | - | 20 |
| `is_latest` | boolean | ❌ | - | - |
| `is_stable` | boolean | ❌ | - | - |
| `changelog` | text | ✅ | - | - |
| `breaking_changes` | text | ✅ | - | - |
| `migration_guide` | text | ✅ | - | - |
| `component_data` | jsonb | ❌ | - | - |
| `file_size` | integer | ✅ | - | - |
| `min_platform_version` | character varying | ✅ | - | 20 |
| `max_platform_version` | character varying | ✅ | - | 20 |
| `dependencies` | jsonb | ✅ | - | - |
| `download_count` | integer | ❌ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `deprecated_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `contact_events`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `contact_id` | uuid | ❌ | - | - |
| `event_type` | character varying | ❌ | - | 100 |
| `event_data` | jsonb | ✅ | '{}'::jsonb | - |
| `occurred_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `contact_interactions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `contact_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ✅ | - | - |
| `type` | character varying | ❌ | - | 50 |
| `channel` | character varying | ✅ | - | 50 |
| `subject` | character varying | ✅ | - | 255 |
| `content` | text | ✅ | - | - |
| `direction` | character varying | ✅ | 'outbound'::character varying | 20 |
| `status` | character varying | ✅ | 'completed'::character varying | 50 |
| `scheduled_at` | timestamp with time zone | ✅ | - | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `contact_list_memberships`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `list_id` | uuid | ❌ | - | - |
| `contact_id` | uuid | ❌ | - | - |
| `added_by` | uuid | ✅ | - | - |
| `added_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `status` | character varying | ✅ | 'active'::character varying | 50 |
| `tenant_id` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `contact_lists`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `type` | character varying | ✅ | 'static'::character varying | 50 |
| `filters` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `contact_notes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `contact_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `content` | text | ❌ | - | - |
| `type` | character varying | ✅ | 'note'::character varying | 50 |
| `is_private` | boolean | ✅ | false | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `contact_sources`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `integration_type` | character varying | ✅ | - | 50 |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `is_active` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `contact_tags`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `color` | character varying | ✅ | '#6B7280'::character varying | 7 |
| `description` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `contacts`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `email` | character varying | ❌ | - | 255 |
| `first_name` | character varying | ✅ | - | 100 |
| `last_name` | character varying | ✅ | - | 100 |
| `phone` | character varying | ✅ | - | 50 |
| `company` | character varying | ✅ | - | 255 |
| `job_title` | character varying | ✅ | - | 255 |
| `status` | character varying | ✅ | 'active'::character varying | 50 |
| `lead_score` | integer | ✅ | 0 | - |
| `source_id` | uuid | ✅ | - | - |
| `custom_fields` | jsonb | ✅ | '{}'::jsonb | - |
| `tags` | ARRAY | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `conversion_journeys`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `contact_id` | uuid | ❌ | - | - |
| `tenant_id` | uuid | ❌ | - | - |
| `journey_name` | character varying | ✅ | - | 255 |
| `current_stage` | character varying | ✅ | - | 100 |
| `stages_completed` | jsonb | ✅ | '[]'::jsonb | - |
| `conversion_probability` | numeric | ✅ | - | - |
| `last_interaction_at` | timestamp with time zone | ✅ | - | - |
| `converted_at` | timestamp with time zone | ✅ | - | - |
| `conversion_value` | numeric | ✅ | - | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `coupons`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `code` | character varying | ❌ | - | 100 |
| `name` | character varying | ✅ | - | 255 |
| `description` | text | ✅ | - | - |
| `type` | character varying | ❌ | 'percentage'::character varying | 50 |
| `value` | numeric | ❌ | - | - |
| `currency` | character varying | ✅ | 'USD'::character varying | 3 |
| `max_uses` | integer | ✅ | - | - |
| `used_count` | integer | ✅ | 0 | - |
| `min_amount` | numeric | ✅ | - | - |
| `max_discount` | numeric | ✅ | - | - |
| `valid_from` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `valid_until` | timestamp with time zone | ✅ | - | - |
| `is_active` | boolean | ✅ | true | - |
| `is_stackable` | boolean | ✅ | false | - |
| `applicable_plans` | jsonb | ✅ | '[]'::jsonb | - |
| `restrictions` | jsonb | ✅ | '{}'::jsonb | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_by` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `custom_reports`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `name` | character varying | ❌ | - | 200 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ✅ | - | 50 |
| `query_config` | jsonb | ❌ | - | - |
| `visualization_config` | jsonb | ✅ | - | - |
| `filters` | jsonb | ✅ | - | - |
| `is_scheduled` | boolean | ❌ | - | - |
| `schedule_config` | jsonb | ✅ | - | - |
| `last_run_at` | timestamp with time zone | ✅ | - | - |
| `next_run_at` | timestamp with time zone | ✅ | - | - |
| `is_public` | boolean | ❌ | - | - |
| `shared_with` | jsonb | ✅ | - | - |
| `cached_data` | jsonb | ✅ | - | - |
| `cache_expires_at` | timestamp with time zone | ✅ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `updated_at` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `email_verification_tokens`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `token` | character varying | ❌ | - | 500 |
| `user_id` | uuid | ❌ | - | - |
| `expires_at` | timestamp with time zone | ❌ | - | - |
| `is_used` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `features`

**Registros:** 20

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `key` | character varying | ❌ | - | 100 |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ✅ | - | 100 |
| `is_active` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `files`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `filename` | character varying | ❌ | - | 255 |
| `original_name` | character varying | ❌ | - | 255 |
| `file_path` | character varying | ❌ | - | 500 |
| `file_size` | integer | ❌ | - | - |
| `mime_type` | character varying | ❌ | - | 100 |
| `category` | character varying | ❌ | - | 50 |
| `is_public` | boolean | ❌ | false | - |
| `user_id` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tags` | jsonb | ✅ | - | - |
| `description` | text | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `scan_status` | character varying | ✅ | 'pending'::character varying | 20 |
| `access_count` | integer | ✅ | 0 | - |
| `last_accessed_at` | timestamp with time zone | ✅ | - | - |

### Tabela: `invoices`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `subscription_id` | uuid | ✅ | - | - |
| `invoice_number` | character varying | ❌ | - | 100 |
| `status` | character varying | ❌ | 'draft'::character varying | 50 |
| `currency` | character varying | ❌ | 'USD'::character varying | 3 |
| `subtotal` | numeric | ❌ | 0 | - |
| `tax_amount` | numeric | ❌ | 0 | - |
| `discount_amount` | numeric | ❌ | 0 | - |
| `total_amount` | numeric | ❌ | 0 | - |
| `due_date` | date | ✅ | - | - |
| `paid_at` | timestamp with time zone | ✅ | - | - |
| `items` | jsonb | ✅ | '[]'::jsonb | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `knowledge_bases`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `kb_id` | uuid | ❌ | gen_random_uuid() | - |
| `title` | text | ❌ | - | - |
| `content` | jsonb | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `llms`

**Registros:** 55

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `name` | character varying | ❌ | - | 100 |
| `provider` | character varying | ❌ | - | 50 |
| `model_version` | character varying | ✅ | - | 50 |
| `cost_per_token_input` | double precision | ❌ | 0.0 | - |
| `cost_per_token_output` | double precision | ❌ | 0.0 | - |
| `max_tokens_supported` | integer | ✅ | - | - |
| `supports_function_calling` | boolean | ✅ | false | - |
| `supports_vision` | boolean | ✅ | false | - |
| `supports_streaming` | boolean | ✅ | true | - |
| `context_window` | integer | ✅ | - | - |
| `is_active` | boolean | ✅ | true | - |
| `llm_metadata` | jsonb | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `health_status` | character varying | ✅ | 'unknown'::character varying | 20 |
| `response_time_avg_ms` | integer | ✅ | 0 | - |
| `availability_percentage` | numeric | ✅ | 99.9 | - |

### Tabela: `llms_conversations`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `agent_id` | uuid | ✅ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `title` | character varying | ✅ | - | 255 |
| `status` | character varying | ✅ | - | 50 |
| `message_count` | integer | ✅ | - | - |
| `total_tokens_used` | integer | ✅ | - | - |
| `context` | jsonb | ✅ | - | - |
| `settings` | jsonb | ✅ | - | - |
| `last_message_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ❌ | - | - |

### Tabela: `llms_conversations_turns`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `conversation_id` | uuid | ❌ | - | - |
| `llm_id` | uuid | ❌ | - | - |
| `first_used_at` | timestamp with time zone | ❌ | now() | - |
| `last_used_at` | timestamp with time zone | ❌ | now() | - |
| `message_count` | integer | ✅ | 0 | - |
| `total_input_tokens` | integer | ✅ | 0 | - |
| `total_output_tokens` | integer | ✅ | 0 | - |
| `total_cost_usd` | double precision | ✅ | 0.0 | - |
| `tenant_id` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `llms_messages`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `conversation_id` | uuid | ❌ | - | - |
| `role` | character varying | ❌ | - | 20 |
| `content` | text | ❌ | - | - |
| `attachments` | jsonb | ✅ | - | - |
| `model_used` | character varying | ✅ | - | 100 |
| `model_provider` | character varying | ✅ | - | 50 |
| `tokens_used` | integer | ✅ | - | - |
| `processing_time_ms` | integer | ✅ | - | - |
| `temperature` | double precision | ✅ | - | - |
| `max_tokens` | integer | ✅ | - | - |
| `status` | character varying | ✅ | - | 50 |
| `error_message` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `llms_usage_logs`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `message_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `conversation_id` | uuid | ❌ | - | - |
| `llm_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `input_tokens` | integer | ❌ | 0 | - |
| `output_tokens` | integer | ❌ | 0 | - |
| `total_tokens` | integer | ❌ | 0 | - |
| `cost_usd` | double precision | ❌ | 0.0 | - |
| `latency_ms` | integer | ✅ | - | - |
| `api_status_code` | integer | ✅ | - | - |
| `api_request_payload` | jsonb | ✅ | - | - |
| `api_response_metadata` | jsonb | ✅ | - | - |
| `user_api_key_used` | boolean | ✅ | false | - |
| `model_settings` | jsonb | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `status` | character varying | ✅ | 'success'::character varying | 20 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `marketplace_components`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ❌ | - | 100 |
| `component_type` | character varying | ❌ | - | 50 |
| `tags` | ARRAY | ✅ | - | - |
| `price` | numeric | ❌ | 0.00 | - |
| `is_free` | boolean | ❌ | true | - |
| `author_id` | uuid | ❌ | - | - |
| `version` | character varying | ❌ | '1.0.0'::character varying | 50 |
| `content` | text | ✅ | - | - |
| `component_metadata` | text | ✅ | - | - |
| `downloads_count` | integer | ❌ | 0 | - |
| `rating_average` | double precision | ❌ | - | - |
| `rating_count` | integer | ❌ | - | - |
| `is_featured` | boolean | ❌ | false | - |
| `is_approved` | boolean | ❌ | false | - |
| `status` | character varying | ❌ | 'pending'::character varying | 20 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `title` | character varying | ❌ | - | 200 |
| `short_description` | character varying | ✅ | - | 500 |
| `subcategory` | character varying | ✅ | - | 50 |
| `organization` | character varying | ✅ | - | 100 |
| `configuration_schema` | jsonb | ✅ | - | - |
| `dependencies` | jsonb | ✅ | - | - |
| `compatibility` | jsonb | ✅ | - | - |
| `documentation` | text | ✅ | - | - |
| `readme` | text | ✅ | - | - |
| `changelog` | text | ✅ | - | - |
| `examples` | jsonb | ✅ | - | - |
| `icon_url` | character varying | ✅ | - | 500 |
| `screenshots` | jsonb | ✅ | - | - |
| `demo_url` | character varying | ✅ | - | 500 |
| `video_url` | character varying | ✅ | - | 500 |
| `currency` | character varying | ✅ | - | 3 |
| `license_type` | character varying | ✅ | - | 50 |
| `install_count` | integer | ❌ | - | - |
| `view_count` | integer | ❌ | - | - |
| `like_count` | integer | ❌ | - | - |
| `is_verified` | boolean | ❌ | - | - |
| `moderation_notes` | text | ✅ | - | - |
| `keywords` | jsonb | ✅ | - | - |
| `search_vector` | text | ✅ | - | - |
| `popularity_score` | double precision | ❌ | - | - |
| `published_at` | timestamp with time zone | ✅ | - | - |
| `last_download_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `message_feedbacks`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `message_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `rating_type` | character varying | ❌ | - | 20 |
| `rating_value` | integer | ✅ | - | - |
| `feedback_text` | text | ✅ | - | - |
| `feedback_category` | character varying | ✅ | - | 50 |
| `improvement_suggestions` | text | ✅ | - | - |
| `is_public` | boolean | ✅ | false | - |
| `feedback_metadata` | jsonb | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `node_categories`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `icon` | character varying | ✅ | - | 10 |
| `color` | character varying | ✅ | - | 7 |
| `parent_id` | uuid | ✅ | - | - |
| `sort_order` | integer | ✅ | - | - |
| `is_active` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `node_executions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.node_executions_id_seq'::regclass) | - |
| `execution_id` | character varying | ✅ | - | 36 |
| `workflow_execution_id` | uuid | ❌ | - | - |
| `node_id` | uuid | ❌ | - | - |
| `node_key` | character varying | ❌ | - | 255 |
| `node_type` | character varying | ❌ | - | 100 |
| `node_name` | character varying | ✅ | - | 255 |
| `execution_order` | integer | ❌ | - | - |
| `input_data` | jsonb | ✅ | - | - |
| `output_data` | jsonb | ✅ | - | - |
| `config_data` | jsonb | ✅ | - | - |
| `started_at` | timestamp with time zone | ✅ | - | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `timeout_at` | timestamp with time zone | ✅ | - | - |
| `duration_ms` | integer | ✅ | - | - |
| `execution_log` | text | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `error_details` | jsonb | ✅ | - | - |
| `debug_info` | jsonb | ✅ | - | - |
| `retry_count` | integer | ✅ | - | - |
| `max_retries` | integer | ✅ | - | - |
| `retry_delay` | integer | ✅ | - | - |
| `dependencies` | jsonb | ✅ | - | - |
| `dependents` | jsonb | ✅ | - | - |
| `metadata` | jsonb | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `node_ratings`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `node_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `rating` | integer | ❌ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `node_templates`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 200 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ✅ | - | 100 |
| `code_template` | text | ❌ | - | - |
| `input_schema` | jsonb | ❌ | - | - |
| `output_schema` | jsonb | ❌ | - | - |
| `parameters_schema` | jsonb | ✅ | - | - |
| `icon` | character varying | ✅ | - | 10 |
| `color` | character varying | ✅ | - | 7 |
| `documentation` | text | ✅ | - | - |
| `examples` | jsonb | ✅ | - | - |
| `is_system` | boolean | ✅ | - | - |
| `is_active` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `nodes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `category` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `version` | character varying | ❌ | '1.0.0'::character varying | 50 |
| `definition` | jsonb | ❌ | - | - |
| `is_public` | boolean | ❌ | false | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `code_template` | text | ❌ | - | - |
| `input_schema` | jsonb | ❌ | - | - |
| `output_schema` | jsonb | ❌ | - | - |
| `parameters_schema` | jsonb | ✅ | - | - |
| `icon` | character varying | ✅ | - | 10 |
| `color` | character varying | ✅ | - | 7 |
| `documentation` | text | ✅ | - | - |
| `examples` | jsonb | ✅ | - | - |
| `downloads_count` | integer | ✅ | - | - |
| `usage_count` | integer | ✅ | - | - |
| `rating_average` | integer | ✅ | - | - |
| `rating_count` | integer | ✅ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `timeout_seconds` | integer | ✅ | 300 | - |
| `retry_count` | integer | ✅ | 3 | - |

### Tabela: `password_reset_tokens`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `token` | character varying | ❌ | - | 500 |
| `user_id` | uuid | ❌ | - | - |
| `expires_at` | timestamp with time zone | ❌ | - | - |
| `is_used` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `payment_customers`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `provider_id` | uuid | ❌ | - | - |
| `external_customer_id` | character varying | ❌ | - | 255 |
| `customer_data` | jsonb | ✅ | '{}'::jsonb | - |
| `is_active` | boolean | ✅ | true | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `payment_methods`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `customer_id` | uuid | ❌ | - | - |
| `external_method_id` | character varying | ❌ | - | 255 |
| `type` | character varying | ❌ | - | 50 |
| `last4` | character varying | ✅ | - | 4 |
| `brand` | character varying | ✅ | - | 50 |
| `exp_month` | integer | ✅ | - | - |
| `exp_year` | integer | ✅ | - | - |
| `is_default` | boolean | ✅ | false | - |
| `is_active` | boolean | ✅ | true | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `payment_providers`

**Registros:** 3

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `name` | character varying | ❌ | - | 100 |
| `display_name` | character varying | ❌ | - | 255 |
| `is_active` | boolean | ✅ | true | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `webhook_secret` | character varying | ✅ | - | 255 |
| `api_version` | character varying | ✅ | - | 50 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `plan_entitlements`

**Registros:** 20

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `plan_id` | uuid | ❌ | - | - |
| `feature_id` | uuid | ❌ | - | - |
| `limit_value` | integer | ✅ | - | - |
| `is_unlimited` | boolean | ✅ | false | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `plan_features`

**Registros:** 27

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `plan_id` | uuid | ❌ | - | - |
| `feature_id` | uuid | ❌ | - | - |
| `is_enabled` | boolean | ✅ | true | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `plan_provider_mappings`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `plan_id` | uuid | ❌ | - | - |
| `provider_id` | uuid | ❌ | - | - |
| `external_plan_id` | character varying | ❌ | - | 255 |
| `external_price_id` | character varying | ✅ | - | 255 |
| `is_active` | boolean | ✅ | true | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `plans`

**Registros:** 4

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `slug` | character varying | ❌ | - | 50 |
| `description` | text | ✅ | - | - |
| `price_monthly` | double precision | ❌ | 0.0 | - |
| `price_yearly` | double precision | ❌ | 0.0 | - |
| `max_workspaces` | integer | ❌ | 1 | - |
| `max_members_per_workspace` | integer | ❌ | 1 | - |
| `max_projects_per_workspace` | integer | ❌ | 10 | - |
| `max_storage_mb` | integer | ❌ | 100 | - |
| `max_executions_per_month` | integer | ❌ | 100 | - |
| `allow_collaborative_workspaces` | boolean | ❌ | false | - |
| `allow_custom_domains` | boolean | ❌ | false | - |
| `allow_api_access` | boolean | ❌ | false | - |
| `allow_advanced_analytics` | boolean | ❌ | false | - |
| `allow_priority_support` | boolean | ❌ | false | - |
| `is_active` | boolean | ❌ | true | - |
| `is_public` | boolean | ❌ | true | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `version` | character varying | ✅ | '1.0.0'::character varying | 20 |
| `sort_order` | integer | ✅ | 0 | - |

### Tabela: `project_collaborators`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `project_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `can_edit` | boolean | ❌ | - | - |
| `can_comment` | boolean | ❌ | - | - |
| `can_share` | boolean | ❌ | - | - |
| `can_delete` | boolean | ❌ | - | - |
| `is_online` | boolean | ❌ | - | - |
| `current_cursor_position` | jsonb | ✅ | - | - |
| `last_edit_at` | timestamp with time zone | ✅ | - | - |
| `added_at` | timestamp with time zone | ❌ | - | - |
| `last_seen_at` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `project_comments`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `project_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `parent_id` | uuid | ✅ | - | - |
| `content` | text | ❌ | - | - |
| `content_type` | character varying | ❌ | - | 20 |
| `node_id` | character varying | ✅ | - | 36 |
| `position_x` | double precision | ✅ | - | - |
| `position_y` | double precision | ✅ | - | - |
| `is_resolved` | boolean | ❌ | - | - |
| `is_edited` | boolean | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `updated_at` | timestamp with time zone | ❌ | - | - |
| `resolved_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `project_versions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `project_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `version_number` | integer | ❌ | - | - |
| `version_name` | character varying | ✅ | - | 100 |
| `description` | text | ✅ | - | - |
| `workflow_data` | jsonb | ❌ | - | - |
| `changes_summary` | jsonb | ✅ | - | - |
| `file_size` | integer | ✅ | - | - |
| `checksum` | character varying | ✅ | - | 64 |
| `is_major` | boolean | ❌ | - | - |
| `is_auto_save` | boolean | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `rbac_permissions`

**Registros:** 19

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `key` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ✅ | - | 100 |
| `resource` | character varying | ✅ | - | 100 |
| `action` | character varying | ✅ | - | 100 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `rbac_role_permissions`

**Registros:** 17

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `role_id` | uuid | ❌ | - | - |
| `permission_id` | uuid | ❌ | - | - |
| `granted` | boolean | ✅ | true | - |
| `conditions` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `rbac_roles`

**Registros:** 10

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `is_system` | boolean | ✅ | false | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `refresh_tokens`

**Registros:** 128

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `token` | character varying | ❌ | - | 500 |
| `user_id` | uuid | ❌ | - | - |
| `expires_at` | timestamp with time zone | ❌ | - | - |
| `is_revoked` | boolean | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `report_executions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `report_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ✅ | - | - |
| `execution_type` | character varying | ❌ | - | 20 |
| `parameters` | json | ✅ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `result_data` | json | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `execution_time_ms` | integer | ✅ | - | - |
| `rows_processed` | integer | ✅ | - | - |
| `data_size_bytes` | integer | ✅ | - | - |
| `started_at` | timestamp with time zone | ❌ | - | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `subscriptions`

**Registros:** 2

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `plan_id` | uuid | ❌ | - | - |
| `provider_id` | uuid | ✅ | - | - |
| `external_subscription_id` | character varying | ✅ | - | 255 |
| `status` | character varying | ❌ | 'active'::character varying | 50 |
| `current_period_start` | timestamp with time zone | ✅ | - | - |
| `current_period_end` | timestamp with time zone | ✅ | - | - |
| `trial_start` | timestamp with time zone | ✅ | - | - |
| `trial_end` | timestamp with time zone | ✅ | - | - |
| `cancel_at_period_end` | boolean | ✅ | false | - |
| `canceled_at` | timestamp with time zone | ✅ | - | - |
| `ended_at` | timestamp with time zone | ✅ | - | - |
| `payment_method_id` | uuid | ✅ | - | - |
| `coupon_id` | uuid | ✅ | - | - |
| `quantity` | integer | ✅ | 1 | - |
| `discount_amount` | numeric | ✅ | 0 | - |
| `tax_percent` | numeric | ✅ | 0 | - |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `system_health`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `component` | text | ✅ | - | - |
| `status` | text | ✅ | - | - |
| `last_check` | timestamp with time zone | ✅ | - | - |
| `metrics` | json | ✅ | - | - |

### Tabela: `system_performance_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.system_performance_metrics_id_seq'::regclass) | - |
| `metric_name` | character varying | ❌ | - | 100 |
| `metric_type` | character varying | ❌ | - | 20 |
| `service` | character varying | ❌ | - | 50 |
| `environment` | character varying | ❌ | - | 20 |
| `value` | double precision | ❌ | - | - |
| `unit` | character varying | ✅ | - | 20 |
| `tags` | jsonb | ✅ | - | - |
| `timestamp` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `tags`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `target_type` | character varying | ❌ | - | 50 |
| `target_id` | uuid | ❌ | - | - |
| `tag_name` | character varying | ❌ | - | 100 |
| `tag_value` | text | ✅ | - | - |
| `tag_category` | character varying | ✅ | - | 50 |
| `is_system_tag` | boolean | ✅ | false | - |
| `created_by_user_id` | uuid | ✅ | - | - |
| `auto_generated` | boolean | ✅ | false | - |
| `confidence_score` | double precision | ✅ | - | - |
| `tag_metadata` | jsonb | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `template_collections`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.template_collections_id_seq'::regclass) | - |
| `collection_id` | character varying | ✅ | - | 36 |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `creator_id` | uuid | ❌ | - | - |
| `is_public` | boolean | ✅ | - | - |
| `is_featured` | boolean | ✅ | - | - |
| `template_ids` | jsonb | ❌ | - | - |
| `tags` | jsonb | ✅ | - | - |
| `thumbnail_url` | character varying | ✅ | - | 500 |
| `view_count` | integer | ✅ | - | - |
| `follow_count` | integer | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `template_downloads`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.template_downloads_id_seq'::regclass) | - |
| `template_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `download_type` | character varying | ✅ | - | 20 |
| `ip_address` | character varying | ✅ | - | 45 |
| `user_agent` | character varying | ✅ | - | 500 |
| `template_version` | character varying | ✅ | - | 20 |
| `downloaded_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `template_favorites`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.template_favorites_id_seq'::regclass) | - |
| `template_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `notes` | text | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `template_reviews`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.template_reviews_id_seq'::regclass) | - |
| `template_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `rating` | integer | ❌ | - | - |
| `title` | character varying | ✅ | - | 255 |
| `comment` | text | ✅ | - | - |
| `ease_of_use` | integer | ✅ | - | - |
| `documentation_quality` | integer | ✅ | - | - |
| `performance` | integer | ✅ | - | - |
| `value_for_money` | integer | ✅ | - | - |
| `is_verified_purchase` | boolean | ✅ | - | - |
| `is_helpful_count` | integer | ✅ | - | - |
| `is_reported` | boolean | ✅ | - | - |
| `version_reviewed` | character varying | ✅ | - | 20 |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `template_usage`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.template_usage_id_seq'::regclass) | - |
| `template_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ✅ | - | - |
| `usage_type` | character varying | ❌ | - | 20 |
| `success` | boolean | ✅ | - | - |
| `template_version` | character varying | ✅ | - | 20 |
| `modifications_made` | jsonb | ✅ | - | - |
| `execution_time` | integer | ✅ | - | - |
| `ip_address` | character varying | ✅ | - | 45 |
| `user_agent` | character varying | ✅ | - | 500 |
| `used_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `tenant_features`

**Registros:** 40

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `feature_id` | uuid | ❌ | - | - |
| `is_enabled` | boolean | ✅ | true | - |
| `usage_count` | integer | ✅ | 0 | - |
| `limit_value` | integer | ✅ | - | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `expires_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `tenants`

**Registros:** 2

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `name` | character varying | ❌ | - | 255 |
| `slug` | character varying | ❌ | - | 100 |
| `domain` | character varying | ✅ | - | 255 |
| `status` | character varying | ❌ | 'active'::character varying | 50 |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `plan_id` | uuid | ❌ | - | - |
| `theme` | character varying | ✅ | 'light'::character varying | 20 |
| `default_language` | character varying | ✅ | 'en'::character varying | 10 |
| `timezone` | character varying | ✅ | 'UTC'::character varying | 50 |
| `mfa_required` | boolean | ✅ | false | - |
| `session_timeout` | integer | ✅ | 3600 | - |
| `ip_whitelist` | jsonb | ✅ | '[]'::jsonb | - |
| `max_storage_mb` | integer | ✅ | - | - |
| `max_workspaces` | integer | ✅ | - | - |
| `max_api_calls_per_day` | integer | ✅ | - | - |
| `max_members_per_workspace` | integer | ✅ | - | - |
| `enabled_features` | ARRAY | ✅ | - | - |

### Tabela: `tools`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `tool_id` | uuid | ❌ | gen_random_uuid() | - |
| `name` | text | ❌ | - | - |
| `category` | text | ✅ | - | - |
| `base_config` | jsonb | ❌ | '{}'::jsonb | - |
| `tenant_id` | uuid | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |

### Tabela: `user_behavior_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `date` | timestamp with time zone | ❌ | - | - |
| `period_type` | character varying | ❌ | - | 20 |
| `session_count` | integer | ❌ | - | - |
| `total_session_duration` | integer | ❌ | - | - |
| `avg_session_duration` | double precision | ❌ | - | - |
| `page_views` | integer | ❌ | - | - |
| `unique_pages_visited` | integer | ❌ | - | - |
| `workflows_created` | integer | ❌ | - | - |
| `workflows_executed` | integer | ❌ | - | - |
| `components_used` | integer | ❌ | - | - |
| `collaborations_initiated` | integer | ❌ | - | - |
| `marketplace_purchases` | integer | ❌ | - | - |
| `revenue_generated` | double precision | ❌ | - | - |
| `components_published` | integer | ❌ | - | - |
| `error_count` | integer | ❌ | - | - |
| `support_tickets` | integer | ❌ | - | - |
| `feature_requests` | integer | ❌ | - | - |
| `engagement_score` | double precision | ❌ | - | - |
| `satisfaction_score` | double precision | ❌ | - | - |
| `value_score` | double precision | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `updated_at` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `user_insights`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `insight_type` | character varying | ❌ | - | 50 |
| `category` | character varying | ❌ | - | 50 |
| `priority` | character varying | ❌ | - | 20 |
| `title` | character varying | ❌ | - | 200 |
| `description` | text | ❌ | - | - |
| `recommendation` | text | ✅ | - | - |
| `supporting_data` | jsonb | ✅ | - | - |
| `confidence_score` | double precision | ❌ | - | - |
| `suggested_action` | character varying | ✅ | - | 100 |
| `action_url` | character varying | ✅ | - | 500 |
| `action_data` | jsonb | ✅ | - | - |
| `is_read` | boolean | ❌ | - | - |
| `is_dismissed` | boolean | ❌ | - | - |
| `is_acted_upon` | boolean | ❌ | - | - |
| `user_feedback` | character varying | ✅ | - | 20 |
| `expires_at` | timestamp with time zone | ✅ | - | - |
| `is_evergreen` | boolean | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `read_at` | timestamp with time zone | ✅ | - | - |
| `acted_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `user_subscriptions`

**Registros:** 2

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `plan_id` | uuid | ❌ | - | - |
| `started_at` | timestamp with time zone | ❌ | now() | - |
| `expires_at` | timestamp with time zone | ✅ | - | - |
| `cancelled_at` | timestamp with time zone | ✅ | - | - |
| `payment_method` | character varying | ✅ | - | 50 |
| `payment_provider` | character varying | ✅ | - | 50 |
| `external_subscription_id` | character varying | ✅ | - | 255 |
| `billing_cycle` | character varying | ✅ | 'monthly'::character varying | 20 |
| `current_period_start` | timestamp with time zone | ✅ | - | - |
| `current_period_end` | timestamp with time zone | ✅ | - | - |
| `current_workspaces` | integer | ❌ | 0 | - |
| `current_storage_mb` | double precision | ❌ | 0.0 | - |
| `current_executions_this_month` | integer | ❌ | 0 | - |
| `subscription_metadata` | jsonb | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `status` | character varying | ✅ | 'active'::character varying | 50 |

### Tabela: `user_tenant_roles`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `user_id` | uuid | ❌ | - | - |
| `tenant_id` | uuid | ❌ | - | - |
| `role_id` | uuid | ❌ | - | - |
| `granted_by` | uuid | ✅ | - | - |
| `granted_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `expires_at` | timestamp with time zone | ✅ | - | - |
| `is_active` | boolean | ✅ | true | - |
| `conditions` | jsonb | ✅ | '{}'::jsonb | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `user_variables`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `key` | character varying | ❌ | - | 255 |
| `value` | text | ❌ | - | - |
| `is_secret` | boolean | ❌ | false | - |
| `user_id` | uuid | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `category` | character varying | ✅ | - | 100 |
| `description` | text | ✅ | - | - |
| `is_encrypted` | boolean | ❌ | false | - |
| `is_active` | boolean | ❌ | true | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `users`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `email` | character varying | ❌ | - | 255 |
| `username` | character varying | ❌ | - | 255 |
| `hashed_password` | character varying | ❌ | - | 255 |
| `full_name` | character varying | ❌ | - | 200 |
| `is_active` | boolean | ✅ | true | - |
| `is_verified` | boolean | ✅ | false | - |
| `is_superuser` | boolean | ✅ | false | - |
| `profile_image_url` | character varying | ✅ | - | 500 |
| `bio` | character varying | ✅ | - | 1000 |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `status` | character varying | ✅ | 'active'::character varying | 20 |
| `metadata` | jsonb | ✅ | '{}'::jsonb | - |
| `last_login_at` | timestamp with time zone | ✅ | - | - |
| `login_count` | integer | ✅ | 0 | - |
| `failed_login_attempts` | integer | ✅ | 0 | - |
| `account_locked_until` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `webhook_logs`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `provider_id` | uuid | ❌ | - | - |
| `event_type` | character varying | ❌ | - | 100 |
| `event_id` | character varying | ✅ | - | 255 |
| `payload` | jsonb | ❌ | - | - |
| `headers` | jsonb | ✅ | '{}'::jsonb | - |
| `status` | character varying | ✅ | 'pending'::character varying | 50 |
| `processed_at` | timestamp with time zone | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `retry_count` | integer | ✅ | 0 | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `workflow_connections`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ❌ | - | - |
| `source_node_id` | uuid | ❌ | - | - |
| `target_node_id` | uuid | ❌ | - | - |
| `source_port` | character varying | ✅ | - | 100 |
| `target_port` | character varying | ✅ | - | 100 |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `workflow_execution_metrics`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.execution_metrics_id_seq'::regclass) | - |
| `workflow_execution_id` | uuid | ❌ | - | - |
| `node_execution_id` | integer | ✅ | - | - |
| `metric_type` | character varying | ❌ | - | 100 |
| `metric_name` | character varying | ❌ | - | 255 |
| `value_numeric` | integer | ✅ | - | - |
| `value_float` | character varying | ✅ | - | 50 |
| `value_text` | text | ✅ | - | - |
| `value_json` | jsonb | ✅ | - | - |
| `context` | character varying | ✅ | - | 255 |
| `tags` | jsonb | ✅ | - | - |
| `measured_at` | timestamp with time zone | ✅ | now() | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `workflow_execution_queue`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.execution_queue_id_seq'::regclass) | - |
| `queue_id` | character varying | ✅ | - | 36 |
| `workflow_execution_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `priority` | integer | ✅ | - | - |
| `scheduled_at` | timestamp with time zone | ✅ | - | - |
| `started_at` | timestamp with time zone | ✅ | - | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `status` | character varying | ✅ | - | 50 |
| `worker_id` | character varying | ✅ | - | 100 |
| `max_execution_time` | integer | ✅ | - | - |
| `retry_count` | integer | ✅ | - | - |
| `max_retries` | integer | ✅ | - | - |
| `meta_data` | jsonb | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `workflow_executions`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `execution_id` | character varying | ✅ | - | 36 |
| `workflow_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `status` | character varying | ❌ | 'pending'::character varying | 20 |
| `priority` | integer | ✅ | - | - |
| `input_data` | jsonb | ✅ | - | - |
| `output_data` | jsonb | ✅ | - | - |
| `context_data` | jsonb | ✅ | - | - |
| `variables` | jsonb | ✅ | - | - |
| `total_nodes` | integer | ✅ | - | - |
| `completed_nodes` | integer | ✅ | - | - |
| `failed_nodes` | integer | ✅ | - | - |
| `progress_percentage` | integer | ✅ | - | - |
| `started_at` | timestamp with time zone | ❌ | now() | - |
| `completed_at` | timestamp with time zone | ✅ | - | - |
| `timeout_at` | timestamp with time zone | ✅ | - | - |
| `estimated_duration` | integer | ✅ | - | - |
| `actual_duration` | integer | ✅ | - | - |
| `execution_log` | text | ✅ | - | - |
| `error_message` | text | ✅ | - | - |
| `error_details` | jsonb | ✅ | - | - |
| `debug_info` | jsonb | ✅ | - | - |
| `retry_count` | integer | ✅ | - | - |
| `max_retries` | integer | ✅ | - | - |
| `auto_retry` | boolean | ✅ | - | - |
| `notify_on_completion` | boolean | ✅ | - | - |
| `notify_on_failure` | boolean | ✅ | - | - |
| `tags` | jsonb | ✅ | - | - |
| `metadata` | json | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `updated_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `workflow_nodes`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ❌ | - | - |
| `node_id` | uuid | ❌ | - | - |
| `instance_name` | character varying | ✅ | - | 200 |
| `position_x` | integer | ❌ | - | - |
| `position_y` | integer | ❌ | - | - |
| `configuration` | jsonb | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | now() | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `workflow_templates`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `category` | character varying | ❌ | - | 100 |
| `tags` | jsonb | ✅ | - | - |
| `workflow_definition` | jsonb | ❌ | - | - |
| `preview_image` | character varying | ✅ | - | 500 |
| `author_id` | uuid | ❌ | - | - |
| `version` | character varying | ❌ | '1.0.0'::character varying | 50 |
| `is_public` | boolean | ❌ | false | - |
| `is_featured` | boolean | ❌ | false | - |
| `downloads_count` | integer | ❌ | 0 | - |
| `rating_average` | numeric | ❌ | 0.00 | - |
| `rating_count` | integer | ❌ | 0 | - |
| `price` | numeric | ❌ | 0.00 | - |
| `is_free` | boolean | ❌ | true | - |
| `license` | character varying | ❌ | 'MIT'::character varying | 50 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `title` | character varying | ❌ | - | 255 |
| `short_description` | character varying | ✅ | - | 500 |
| `original_workflow_id` | uuid | ✅ | - | - |
| `status` | character varying | ✅ | - | 20 |
| `is_verified` | boolean | ✅ | - | - |
| `license_type` | character varying | ✅ | - | 20 |
| `workflow_data` | jsonb | ❌ | - | - |
| `nodes_data` | jsonb | ❌ | - | - |
| `connections_data` | jsonb | ✅ | - | - |
| `required_variables` | jsonb | ✅ | - | - |
| `optional_variables` | jsonb | ✅ | - | - |
| `default_config` | jsonb | ✅ | - | - |
| `compatibility_version` | character varying | ✅ | - | 20 |
| `estimated_duration` | integer | ✅ | - | - |
| `complexity_level` | integer | ✅ | - | - |
| `download_count` | integer | ✅ | - | - |
| `usage_count` | integer | ✅ | - | - |
| `view_count` | integer | ✅ | - | - |
| `keywords` | jsonb | ✅ | - | - |
| `use_cases` | jsonb | ✅ | - | - |
| `industries` | jsonb | ✅ | - | - |
| `thumbnail_url` | character varying | ✅ | - | 500 |
| `preview_images` | jsonb | ✅ | - | - |
| `demo_video_url` | character varying | ✅ | - | 500 |
| `documentation` | text | ✅ | - | - |
| `setup_instructions` | text | ✅ | - | - |
| `changelog` | jsonb | ✅ | - | - |
| `support_email` | character varying | ✅ | - | 255 |
| `repository_url` | character varying | ✅ | - | 500 |
| `documentation_url` | character varying | ✅ | - | 500 |
| `published_at` | timestamp with time zone | ✅ | - | - |
| `last_used_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `workflows`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `description` | text | ✅ | - | - |
| `definition` | jsonb | ❌ | - | - |
| `is_active` | boolean | ❌ | true | - |
| `user_id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ✅ | - | - |
| `is_public` | boolean | ✅ | false | - |
| `category` | character varying | ✅ | - | 100 |
| `tags` | jsonb | ✅ | - | - |
| `version` | character varying | ✅ | - | 20 |
| `thumbnail_url` | character varying | ✅ | - | 500 |
| `downloads_count` | integer | ✅ | - | - |
| `rating_average` | integer | ✅ | - | - |
| `rating_count` | integer | ✅ | - | - |
| `execution_count` | integer | ✅ | - | - |
| `last_executed_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `tenant_id` | uuid | ❌ | - | - |
| `status` | character varying | ✅ | 'draft'::character varying | 20 |
| `priority` | integer | ✅ | 1 | - |
| `timeout_seconds` | integer | ✅ | 3600 | - |
| `retry_count` | integer | ✅ | 3 | - |

### Tabela: `workspace_activities`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `action` | character varying | ❌ | - | 50 |
| `resource_type` | character varying | ❌ | - | 50 |
| `resource_id` | character varying | ✅ | - | 255 |
| `description` | character varying | ❌ | - | 500 |
| `metadata` | jsonb | ✅ | - | - |
| `ip_address` | character varying | ✅ | - | 45 |
| `user_agent` | character varying | ✅ | - | 500 |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `meta_data` | jsonb | ✅ | '{}'::jsonb | - |

### Tabela: `workspace_features`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | gen_random_uuid() | - |
| `workspace_id` | uuid | ❌ | - | - |
| `feature_id` | uuid | ❌ | - | - |
| `is_enabled` | boolean | ✅ | true | - |
| `config` | jsonb | ✅ | '{}'::jsonb | - |
| `usage_count` | integer | ✅ | 0 | - |
| `limit_value` | integer | ✅ | - | - |
| `expires_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ✅ | - | - |

### Tabela: `workspace_invitations`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ❌ | - | - |
| `inviter_id` | uuid | ❌ | - | - |
| `invited_user_id` | uuid | ✅ | - | - |
| `email` | character varying | ❌ | - | 255 |
| `message` | text | ✅ | - | - |
| `token` | character varying | ❌ | - | 100 |
| `status` | character varying | ❌ | - | 20 |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `expires_at` | timestamp with time zone | ❌ | - | - |
| `responded_at` | timestamp with time zone | ✅ | - | - |
| `tenant_id` | uuid | ✅ | - | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### Tabela: `workspace_members`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | integer | ❌ | nextval('synapscale_db.workspace_members_id_seq'::regclass) | - |
| `workspace_id` | uuid | ❌ | - | - |
| `user_id` | uuid | ❌ | - | - |
| `custom_permissions` | jsonb | ✅ | - | - |
| `status` | character varying | ❌ | 'active'::character varying | 20 |
| `is_favorite` | boolean | ❌ | false | - |
| `notification_preferences` | jsonb | ✅ | - | - |
| `last_seen_at` | timestamp with time zone | ❌ | - | - |
| `joined_at` | timestamp with time zone | ❌ | - | - |
| `left_at` | timestamp with time zone | ✅ | - | - |
| `created_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `updated_at` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `tenant_id` | uuid | ❌ | - | - |
| `role` | character varying | ❌ | 'member'::character varying | 50 |

### Tabela: `workspace_projects`

**Registros:** 0

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `workspace_id` | uuid | ❌ | - | - |
| `workflow_id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 100 |
| `description` | text | ✅ | - | - |
| `color` | character varying | ✅ | - | 7 |
| `allow_concurrent_editing` | boolean | ❌ | - | - |
| `auto_save_interval` | integer | ✅ | - | - |
| `version_control_enabled` | boolean | ❌ | - | - |
| `status` | character varying | ❌ | - | 20 |
| `is_template` | boolean | ❌ | - | - |
| `is_public` | boolean | ❌ | - | - |
| `collaborator_count` | integer | ❌ | - | - |
| `edit_count` | integer | ❌ | - | - |
| `comment_count` | integer | ❌ | - | - |
| `created_at` | timestamp with time zone | ❌ | - | - |
| `updated_at` | timestamp with time zone | ❌ | - | - |
| `last_edited_at` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ❌ | - | - |

### Tabela: `workspaces`

**Registros:** 1

| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |
|--------|------|------|--------|-------------|
| `id` | uuid | ❌ | - | - |
| `name` | character varying | ❌ | - | 255 |
| `slug` | character varying | ❌ | - | 120 |
| `description` | text | ✅ | - | - |
| `avatar_url` | character varying | ✅ | - | 500 |
| `color` | character varying | ✅ | - | 7 |
| `owner_id` | uuid | ❌ | - | - |
| `is_public` | boolean | ❌ | false | - |
| `is_template` | boolean | ❌ | false | - |
| `allow_guest_access` | boolean | ❌ | false | - |
| `require_approval` | boolean | ❌ | - | - |
| `max_members` | integer | ✅ | - | - |
| `max_projects` | integer | ✅ | - | - |
| `max_storage_mb` | integer | ✅ | - | - |
| `enable_real_time_editing` | boolean | ❌ | - | - |
| `enable_comments` | boolean | ❌ | - | - |
| `enable_chat` | boolean | ❌ | - | - |
| `enable_video_calls` | boolean | ❌ | - | - |
| `member_count` | integer | ❌ | - | - |
| `project_count` | integer | ❌ | - | - |
| `activity_count` | integer | ❌ | - | - |
| `storage_used_mb` | double precision | ❌ | - | - |
| `status` | character varying | ❌ | 'active'::character varying | 20 |
| `created_at` | timestamp with time zone | ❌ | now() | - |
| `updated_at` | timestamp with time zone | ❌ | now() | - |
| `last_activity_at` | timestamp with time zone | ❌ | - | - |
| `tenant_id` | uuid | ❌ | - | - |
| `email_notifications` | boolean | ✅ | true | - |
| `push_notifications` | boolean | ✅ | false | - |
| `api_calls_today` | integer | ✅ | 0 | - |
| `api_calls_this_month` | integer | ✅ | 0 | - |
| `last_api_reset_daily` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `last_api_reset_monthly` | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| `feature_usage_count` | jsonb | ✅ | '{}'::jsonb | - |
| `type` | USER-DEFINED | ❌ | 'individual'::synapscale_db.workspacetype | - |

## Relacionamentos

| Tabela Origem | Coluna | Tabela Destino | Coluna Destino |
|---------------|--------|----------------|----------------|
| `banco_de_dados.platform_commission` | `participant_id` | `banco_de_dados.platform_commission_participants` | `id` |
| `banco_de_dados.platform_commission_participants` | `client_address_id` | `banco_de_dados.platform_sale_client_address` | `id` |
| `banco_de_dados.platform_commission_participants_doc` | `commission_participant_id` | `banco_de_dados.platform_commission_participants` | `id` |
| `banco_de_dados.platform_sale` | `client_id` | `banco_de_dados.platform_sale_client` | `id` |
| `banco_de_dados.platform_sale_client` | `client_address_id` | `banco_de_dados.platform_sale_client_address` | `id` |
| `banco_de_dados.platform_sale_client_history` | `platform_sale_client_id` | `banco_de_dados.platform_sale_client` | `id` |
| `banco_de_dados.platform_sale_client_platform_id` | `sale_client_id` | `banco_de_dados.platform_sale_client` | `id` |
| `banco_de_dados.platform_subscription` | `subscriber_id` | `banco_de_dados.platform_sale_client` | `id` |
| `banco_de_dados.platform_subscription__recurrency_history` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados.platform_transaction_commission` | `platform_commission_id` | `banco_de_dados.platform_commission` | `id` |
| `banco_de_dados.platform_transaction_commission` | `platform_sale_id` | `banco_de_dados.platform_sale` | `id` |
| `banco_de_dados.platform_transaction_commission` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados.platform_transaction_fee` | `platform_sale_id` | `banco_de_dados.platform_sale` | `id` |
| `banco_de_dados.platform_transaction_fee` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados.platform_transaction_invoice` | `platform_sale_id` | `banco_de_dados.platform_sale` | `id` |
| `banco_de_dados.platform_transaction_invoice` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados.platform_transaction_offer` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados.platform_transaction_offer` | `platform_sale_id` | `banco_de_dados.platform_sale` | `id` |
| `banco_de_dados.platform_transaction_payment` | `platform_sale_id` | `banco_de_dados.platform_sale` | `id` |
| `banco_de_dados.platform_transaction_payment` | `payment_history_id` | `banco_de_dados.platform_transaction_payment_history` | `id` |
| `banco_de_dados.platform_transaction_payment` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados.platform_transaction_plan` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados.platform_transaction_plan` | `platform_sale_id` | `banco_de_dados.platform_sale` | `id` |
| `banco_de_dados.platform_transaction_product` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados.platform_transaction_product` | `platform_sale_id` | `banco_de_dados.platform_sale` | `id` |
| `banco_de_dados.platform_transaction_status` | `platform_sale_id` | `banco_de_dados.platform_sale` | `id` |
| `banco_de_dados.platform_transaction_status` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados.platform_transaction_status` | `platform_status_id` | `banco_de_dados.platform_status` | `id` |
| `banco_de_dados.platform_transaction_utm` | `platform_sale_id` | `banco_de_dados.platform_sale` | `id` |
| `banco_de_dados.platform_transaction_utm` | `platform_subscription_id` | `banco_de_dados.platform_subscription` | `id` |
| `banco_de_dados_jc.fact_acessos_cademi` | `cliente_id` | `banco_de_dados_jc.dim_cliente` | `cliente_id` |
| `banco_de_dados_jc.fact_pesquisas` | `cliente_id` | `banco_de_dados_jc.dim_cliente` | `cliente_id` |
| `banco_de_dados_jc.fact_vendas` | `cliente_id` | `banco_de_dados_jc.dim_cliente` | `cliente_id` |
| `joaocastanheira_bancodedados.customer_external_ids` | `customer_id` | `joaocastanheira_bancodedados.customers` | `id` |
| `joaocastanheira_bancodedados.customer_logs` | `customer_id` | `joaocastanheira_bancodedados.customers` | `id` |
| `joaocastanheira_bancodedados.customers` | `address_id` | `joaocastanheira_bancodedados.addresses` | `id` |
| `joaocastanheira_bancodedados.offers` | `product_id` | `joaocastanheira_bancodedados.products` | `id` |
| `joaocastanheira_bancodedados.offers` | `plan_id` | `joaocastanheira_bancodedados.plans` | `id` |
| `joaocastanheira_bancodedados.participant_addresses` | `participant_id` | `joaocastanheira_bancodedados.commission_participants` | `id` |
| `joaocastanheira_bancodedados.plans` | `product_id` | `joaocastanheira_bancodedados.products` | `id` |
| `joaocastanheira_bancodedados.platform_commission` | `participant_id` | `joaocastanheira_bancodedados.commission_participants` | `id` |
| `joaocastanheira_bancodedados.platform_commission` | `transaction_id` | `joaocastanheira_bancodedados.transactions` | `id` |
| `joaocastanheira_bancodedados.platform_sale_offer_history` | `transaction_id` | `joaocastanheira_bancodedados.transactions` | `id` |
| `joaocastanheira_bancodedados.platform_software_invoice_history` | `transaction_id` | `joaocastanheira_bancodedados.transactions` | `id` |
| `joaocastanheira_bancodedados.platform_transaction_payment_history` | `transaction_id` | `joaocastanheira_bancodedados.transactions` | `id` |
| `joaocastanheira_bancodedados.platform_utm_history` | `transaction_id` | `joaocastanheira_bancodedados.transactions` | `id` |
| `joaocastanheira_bancodedados.subscription_status_history` | `subscription_id` | `joaocastanheira_bancodedados.subscriptions` | `id` |
| `joaocastanheira_bancodedados.subscription_status_history` | `status_id` | `joaocastanheira_bancodedados.transaction_statuses` | `id` |
| `joaocastanheira_bancodedados.subscriptions` | `plan_id` | `joaocastanheira_bancodedados.plans` | `id` |
| `joaocastanheira_bancodedados.subscriptions` | `customer_id` | `joaocastanheira_bancodedados.customers` | `id` |
| `joaocastanheira_bancodedados.subscriptions` | `status_id` | `joaocastanheira_bancodedados.transaction_statuses` | `id` |
| `joaocastanheira_bancodedados.subscriptions_summary` | `customer_id` | `joaocastanheira_bancodedados.customers` | `id` |
| `joaocastanheira_bancodedados.subscriptions_summary` | `plan_id` | `joaocastanheira_bancodedados.plans` | `id` |
| `joaocastanheira_bancodedados.subscriptions_summary` | `product_id` | `joaocastanheira_bancodedados.products` | `id` |
| `joaocastanheira_bancodedados.subscriptions_summary` | `offer_id` | `joaocastanheira_bancodedados.offers` | `id` |
| `joaocastanheira_bancodedados.subscriptions_summary` | `subscription_origin_id` | `joaocastanheira_bancodedados.subscriptions` | `id` |
| `joaocastanheira_bancodedados.subscriptions_summary` | `status_id` | `joaocastanheira_bancodedados.transaction_statuses` | `id` |
| `joaocastanheira_bancodedados.transaction_fees` | `transaction_id` | `joaocastanheira_bancodedados.transactions` | `id` |
| `joaocastanheira_bancodedados.transaction_items` | `transaction_id` | `joaocastanheira_bancodedados.transactions` | `id` |
| `joaocastanheira_bancodedados.transaction_items` | `offer_id` | `joaocastanheira_bancodedados.offers` | `id` |
| `joaocastanheira_bancodedados.transaction_items` | `product_id` | `joaocastanheira_bancodedados.products` | `id` |
| `joaocastanheira_bancodedados.transaction_items` | `plan_id` | `joaocastanheira_bancodedados.plans` | `id` |
| `joaocastanheira_bancodedados.transaction_status_history` | `status_id` | `joaocastanheira_bancodedados.transaction_statuses` | `id` |
| `joaocastanheira_bancodedados.transaction_status_history` | `transaction_id` | `joaocastanheira_bancodedados.transactions` | `id` |
| `joaocastanheira_bancodedados.transactions` | `status_id` | `joaocastanheira_bancodedados.transaction_statuses` | `id` |
| `joaocastanheira_bancodedados.transactions` | `subscription_id` | `joaocastanheira_bancodedados.subscriptions` | `id` |
| `joaocastanheira_bancodedados.transactions` | `customer_id` | `joaocastanheira_bancodedados.customers` | `id` |
| `modelo_saas_inicial.campaign_contacts` | `contact_id` | `modelo_saas_inicial.contacts` | `id` |
| `modelo_saas_inicial.campaign_contacts` | `campaign_id` | `modelo_saas_inicial.campaigns` | `id` |
| `modelo_saas_inicial.campaigns` | `created_by` | `modelo_saas_inicial.users` | `id` |
| `modelo_saas_inicial.contact_events` | `contact_id` | `modelo_saas_inicial.contacts` | `id` |
| `modelo_saas_inicial.contact_interactions` | `contact_id` | `modelo_saas_inicial.contacts` | `id` |
| `modelo_saas_inicial.contact_list_memberships` | `contact_id` | `modelo_saas_inicial.contacts` | `id` |
| `modelo_saas_inicial.contact_list_memberships` | `contact_list_id` | `modelo_saas_inicial.contact_lists` | `id` |
| `modelo_saas_inicial.contact_lists` | `created_by` | `modelo_saas_inicial.users` | `id` |
| `modelo_saas_inicial.contact_notes` | `contact_id` | `modelo_saas_inicial.contacts` | `id` |
| `modelo_saas_inicial.contact_notes` | `created_by` | `modelo_saas_inicial.users` | `id` |
| `modelo_saas_inicial.contact_tags` | `contact_id` | `modelo_saas_inicial.contacts` | `id` |
| `modelo_saas_inicial.contacts` | `tenant_id` | `modelo_saas_inicial.tenants` | `id` |
| `modelo_saas_inicial.conversion_journeys` | `contact_id` | `modelo_saas_inicial.contacts` | `id` |
| `modelo_saas_inicial.conversion_journeys` | `converted_to_tenant_id` | `modelo_saas_inicial.tenants` | `id` |
| `modelo_saas_inicial.invoices` | `provider_id` | `modelo_saas_inicial.payment_providers` | `id` |
| `modelo_saas_inicial.invoices` | `tenant_id` | `modelo_saas_inicial.tenants` | `id` |
| `modelo_saas_inicial.invoices` | `subscription_id` | `modelo_saas_inicial.subscriptions` | `id` |
| `modelo_saas_inicial.invoices` | `payment_method_id` | `modelo_saas_inicial.payment_methods` | `id` |
| `modelo_saas_inicial.invoices` | `coupon_id` | `modelo_saas_inicial.coupons` | `id` |
| `modelo_saas_inicial.payment_customers` | `provider_id` | `modelo_saas_inicial.payment_providers` | `id` |
| `modelo_saas_inicial.payment_customers` | `tenant_id` | `modelo_saas_inicial.tenants` | `id` |
| `modelo_saas_inicial.payment_methods` | `provider_id` | `modelo_saas_inicial.payment_providers` | `id` |
| `modelo_saas_inicial.payment_methods` | `tenant_id` | `modelo_saas_inicial.tenants` | `id` |
| `modelo_saas_inicial.plan_entitlements` | `plan_id` | `modelo_saas_inicial.plans` | `id` |
| `modelo_saas_inicial.plan_features` | `feature_id` | `modelo_saas_inicial.features` | `id` |
| `modelo_saas_inicial.plan_features` | `plan_id` | `modelo_saas_inicial.plans` | `id` |
| `modelo_saas_inicial.plan_provider_mappings` | `provider_id` | `modelo_saas_inicial.payment_providers` | `id` |
| `modelo_saas_inicial.plan_provider_mappings` | `plan_id` | `modelo_saas_inicial.plans` | `id` |
| `modelo_saas_inicial.role_permissions` | `role_id` | `modelo_saas_inicial.roles` | `id` |
| `modelo_saas_inicial.role_permissions` | `feature_id` | `modelo_saas_inicial.features` | `id` |
| `modelo_saas_inicial.role_permissions` | `permission_id` | `modelo_saas_inicial.permissions` | `id` |
| `modelo_saas_inicial.subscriptions` | `tenant_id` | `modelo_saas_inicial.tenants` | `id` |
| `modelo_saas_inicial.subscriptions` | `coupon_id` | `modelo_saas_inicial.coupons` | `id` |
| `modelo_saas_inicial.subscriptions` | `payment_method_id` | `modelo_saas_inicial.payment_methods` | `id` |
| `modelo_saas_inicial.subscriptions` | `provider_id` | `modelo_saas_inicial.payment_providers` | `id` |
| `modelo_saas_inicial.subscriptions` | `plan_id` | `modelo_saas_inicial.plans` | `id` |
| `modelo_saas_inicial.tenants` | `plan_id` | `modelo_saas_inicial.plans` | `id` |
| `modelo_saas_inicial.webhook_logs` | `provider_id` | `modelo_saas_inicial.payment_providers` | `id` |
| `modelo_saas_inicial.workspace_features` | `workspace_id` | `modelo_saas_inicial.workspaces` | `id` |
| `modelo_saas_inicial.workspace_features` | `feature_id` | `modelo_saas_inicial.features` | `id` |
| `modelo_saas_inicial.workspace_members` | `workspace_id` | `modelo_saas_inicial.workspaces` | `id` |
| `modelo_saas_inicial.workspace_members` | `role_id` | `modelo_saas_inicial.roles` | `id` |
| `modelo_saas_inicial.workspace_members` | `user_id` | `modelo_saas_inicial.users` | `id` |
| `modelo_saas_inicial.workspaces` | `tenant_id` | `modelo_saas_inicial.tenants` | `id` |
| `synapscale_db.agent_acl` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.agent_acl` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_configurations` | `created_by` | `synapscale_db.users` | `id` |
| `synapscale_db.agent_configurations` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_error_logs` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_hierarchy` | `descendant` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_hierarchy` | `ancestor` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_kbs` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_kbs` | `kb_id` | `synapscale_db.knowledge_bases` | `kb_id` |
| `synapscale_db.agent_models` | `llm_id` | `synapscale_db.llms` | `id` |
| `synapscale_db.agent_models` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_quotas` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.agent_quotas` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_tools` | `tool_id` | `synapscale_db.tools` | `tool_id` |
| `synapscale_db.agent_tools` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_triggers` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.agent_usage_metrics` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.agents` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.agents` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.agents` | `current_config` | `synapscale_db.agent_configurations` | `config_id` |
| `synapscale_db.agents` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.analytics_alerts` | `owner_id` | `synapscale_db.users` | `id` |
| `synapscale_db.analytics_alerts` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.analytics_dashboards` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.analytics_dashboards` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.analytics_events` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.analytics_events` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.analytics_events` | `project_id` | `synapscale_db.workspace_projects` | `id` |
| `synapscale_db.analytics_exports` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.analytics_exports` | `owner_id` | `synapscale_db.users` | `id` |
| `synapscale_db.analytics_metrics` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.analytics_reports` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.analytics_reports` | `owner_id` | `synapscale_db.users` | `id` |
| `synapscale_db.audit_log` | `changed_by` | `synapscale_db.users` | `id` |
| `synapscale_db.billing_events` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.billing_events` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.billing_events` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.billing_events` | `related_usage_log_id` | `synapscale_db.llms_usage_logs` | `id` |
| `synapscale_db.billing_events` | `related_message_id` | `synapscale_db.llms_messages` | `id` |
| `synapscale_db.business_metrics` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.campaign_contacts` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.campaign_contacts` | `contact_id` | `synapscale_db.contacts` | `id` |
| `synapscale_db.campaign_contacts` | `campaign_id` | `synapscale_db.campaigns` | `id` |
| `synapscale_db.campaigns` | `created_by` | `synapscale_db.users` | `id` |
| `synapscale_db.campaigns` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.component_downloads` | `component_id` | `synapscale_db.marketplace_components` | `id` |
| `synapscale_db.component_downloads` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.component_downloads` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.component_purchases` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.component_purchases` | `component_id` | `synapscale_db.marketplace_components` | `id` |
| `synapscale_db.component_purchases` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.component_ratings` | `component_id` | `synapscale_db.marketplace_components` | `id` |
| `synapscale_db.component_ratings` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.component_ratings` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.component_versions` | `component_id` | `synapscale_db.marketplace_components` | `id` |
| `synapscale_db.component_versions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.contact_events` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.contact_events` | `contact_id` | `synapscale_db.contacts` | `id` |
| `synapscale_db.contact_interactions` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.contact_interactions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.contact_interactions` | `contact_id` | `synapscale_db.contacts` | `id` |
| `synapscale_db.contact_list_memberships` | `contact_id` | `synapscale_db.contacts` | `id` |
| `synapscale_db.contact_list_memberships` | `added_by` | `synapscale_db.users` | `id` |
| `synapscale_db.contact_list_memberships` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.contact_list_memberships` | `list_id` | `synapscale_db.contact_lists` | `id` |
| `synapscale_db.contact_lists` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.contact_notes` | `contact_id` | `synapscale_db.contacts` | `id` |
| `synapscale_db.contact_notes` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.contact_notes` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.contact_sources` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.contact_tags` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.contacts` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.contacts` | `source_id` | `synapscale_db.contact_sources` | `id` |
| `synapscale_db.conversion_journeys` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.conversion_journeys` | `contact_id` | `synapscale_db.contacts` | `id` |
| `synapscale_db.coupons` | `created_by` | `synapscale_db.users` | `id` |
| `synapscale_db.coupons` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.custom_reports` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.custom_reports` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.custom_reports` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.email_verification_tokens` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.files` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.files` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.invoices` | `subscription_id` | `synapscale_db.subscriptions` | `id` |
| `synapscale_db.invoices` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.llms` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.llms_conversations` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.llms_conversations` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.llms_conversations` | `agent_id` | `synapscale_db.agents` | `id` |
| `synapscale_db.llms_conversations` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.llms_conversations` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.llms_conversations_turns` | `llm_id` | `synapscale_db.llms` | `id` |
| `synapscale_db.llms_conversations_turns` | `conversation_id` | `synapscale_db.llms_conversations` | `id` |
| `synapscale_db.llms_conversations_turns` | `conversation_id` | `synapscale_db.llms_conversations` | `id` |
| `synapscale_db.llms_conversations_turns` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.llms_conversations_turns` | `llm_id` | `synapscale_db.llms` | `id` |
| `synapscale_db.llms_messages` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.llms_messages` | `conversation_id` | `synapscale_db.llms_conversations` | `id` |
| `synapscale_db.llms_messages` | `conversation_id` | `synapscale_db.llms_conversations` | `id` |
| `synapscale_db.llms_usage_logs` | `llm_id` | `synapscale_db.llms` | `id` |
| `synapscale_db.llms_usage_logs` | `conversation_id` | `synapscale_db.llms_conversations` | `id` |
| `synapscale_db.llms_usage_logs` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.llms_usage_logs` | `message_id` | `synapscale_db.llms_messages` | `id` |
| `synapscale_db.llms_usage_logs` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.llms_usage_logs` | `conversation_id` | `synapscale_db.llms_conversations` | `id` |
| `synapscale_db.llms_usage_logs` | `llm_id` | `synapscale_db.llms` | `id` |
| `synapscale_db.llms_usage_logs` | `message_id` | `synapscale_db.llms_messages` | `id` |
| `synapscale_db.llms_usage_logs` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.marketplace_components` | `author_id` | `synapscale_db.users` | `id` |
| `synapscale_db.marketplace_components` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.message_feedbacks` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.message_feedbacks` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.message_feedbacks` | `message_id` | `synapscale_db.llms_messages` | `id` |
| `synapscale_db.message_feedbacks` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.message_feedbacks` | `message_id` | `synapscale_db.llms_messages` | `id` |
| `synapscale_db.node_categories` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.node_categories` | `parent_id` | `synapscale_db.node_categories` | `id` |
| `synapscale_db.node_executions` | `workflow_execution_id` | `synapscale_db.workflow_executions` | `id` |
| `synapscale_db.node_executions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.node_ratings` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.node_ratings` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.node_ratings` | `node_id` | `synapscale_db.nodes` | `id` |
| `synapscale_db.node_templates` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.nodes` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.nodes` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.nodes` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.password_reset_tokens` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.payment_customers` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.payment_customers` | `provider_id` | `synapscale_db.payment_providers` | `id` |
| `synapscale_db.payment_methods` | `customer_id` | `synapscale_db.payment_customers` | `id` |
| `synapscale_db.payment_methods` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.payment_providers` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.plan_entitlements` | `plan_id` | `synapscale_db.plans` | `id` |
| `synapscale_db.plan_entitlements` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.plan_entitlements` | `feature_id` | `synapscale_db.features` | `id` |
| `synapscale_db.plan_features` | `feature_id` | `synapscale_db.features` | `id` |
| `synapscale_db.plan_features` | `plan_id` | `synapscale_db.plans` | `id` |
| `synapscale_db.plan_provider_mappings` | `plan_id` | `synapscale_db.plans` | `id` |
| `synapscale_db.plan_provider_mappings` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.plan_provider_mappings` | `provider_id` | `synapscale_db.payment_providers` | `id` |
| `synapscale_db.project_collaborators` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.project_collaborators` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.project_comments` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.project_comments` | `parent_id` | `synapscale_db.project_comments` | `id` |
| `synapscale_db.project_comments` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.project_versions` | `project_id` | `synapscale_db.workspace_projects` | `id` |
| `synapscale_db.project_versions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.project_versions` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.rbac_permissions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.rbac_role_permissions` | `role_id` | `synapscale_db.rbac_roles` | `id` |
| `synapscale_db.rbac_role_permissions` | `permission_id` | `synapscale_db.rbac_permissions` | `id` |
| `synapscale_db.rbac_role_permissions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.rbac_roles` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.refresh_tokens` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.report_executions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.report_executions` | `report_id` | `synapscale_db.custom_reports` | `id` |
| `synapscale_db.report_executions` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.subscriptions` | `provider_id` | `synapscale_db.payment_providers` | `id` |
| `synapscale_db.subscriptions` | `coupon_id` | `synapscale_db.coupons` | `id` |
| `synapscale_db.subscriptions` | `plan_id` | `synapscale_db.plans` | `id` |
| `synapscale_db.subscriptions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.subscriptions` | `payment_method_id` | `synapscale_db.payment_methods` | `id` |
| `synapscale_db.system_performance_metrics` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.tags` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.tags` | `created_by_user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.template_collections` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.template_collections` | `creator_id` | `synapscale_db.users` | `id` |
| `synapscale_db.template_downloads` | `template_id` | `synapscale_db.workflow_templates` | `id` |
| `synapscale_db.template_downloads` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.template_downloads` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.template_favorites` | `template_id` | `synapscale_db.workflow_templates` | `id` |
| `synapscale_db.template_favorites` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.template_favorites` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.template_reviews` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.template_reviews` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.template_reviews` | `template_id` | `synapscale_db.workflow_templates` | `id` |
| `synapscale_db.template_usage` | `workflow_id` | `synapscale_db.workflows` | `id` |
| `synapscale_db.template_usage` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.template_usage` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.template_usage` | `template_id` | `synapscale_db.workflow_templates` | `id` |
| `synapscale_db.tenant_features` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.tenant_features` | `feature_id` | `synapscale_db.features` | `id` |
| `synapscale_db.tenants` | `plan_id` | `synapscale_db.plans` | `id` |
| `synapscale_db.user_behavior_metrics` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.user_behavior_metrics` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.user_insights` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.user_insights` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.user_subscriptions` | `plan_id` | `synapscale_db.plans` | `id` |
| `synapscale_db.user_subscriptions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.user_subscriptions` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.user_tenant_roles` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.user_tenant_roles` | `role_id` | `synapscale_db.rbac_roles` | `id` |
| `synapscale_db.user_tenant_roles` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.user_tenant_roles` | `granted_by` | `synapscale_db.users` | `id` |
| `synapscale_db.user_variables` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.user_variables` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.users` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.webhook_logs` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.webhook_logs` | `provider_id` | `synapscale_db.payment_providers` | `id` |
| `synapscale_db.workflow_connections` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workflow_connections` | `target_node_id` | `synapscale_db.workflow_nodes` | `id` |
| `synapscale_db.workflow_connections` | `workflow_id` | `synapscale_db.workflows` | `id` |
| `synapscale_db.workflow_connections` | `source_node_id` | `synapscale_db.workflow_nodes` | `id` |
| `synapscale_db.workflow_execution_metrics` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workflow_execution_queue` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workflow_execution_queue` | `workflow_execution_id` | `synapscale_db.workflow_executions` | `id` |
| `synapscale_db.workflow_execution_queue` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.workflow_executions` | `workflow_id` | `synapscale_db.workflows` | `id` |
| `synapscale_db.workflow_executions` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.workflow_executions` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workflow_nodes` | `workflow_id` | `synapscale_db.workflows` | `id` |
| `synapscale_db.workflow_nodes` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workflow_templates` | `author_id` | `synapscale_db.users` | `id` |
| `synapscale_db.workflow_templates` | `original_workflow_id` | `synapscale_db.workflows` | `id` |
| `synapscale_db.workflow_templates` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workflows` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.workflows` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workflows` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.workspace_activities` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.workspace_activities` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.workspace_activities` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workspace_features` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workspace_features` | `feature_id` | `synapscale_db.features` | `id` |
| `synapscale_db.workspace_features` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.workspace_invitations` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workspace_invitations` | `invited_user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.workspace_invitations` | `inviter_id` | `synapscale_db.users` | `id` |
| `synapscale_db.workspace_invitations` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.workspace_members` | `user_id` | `synapscale_db.users` | `id` |
| `synapscale_db.workspace_members` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.workspace_members` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workspace_projects` | `workspace_id` | `synapscale_db.workspaces` | `id` |
| `synapscale_db.workspace_projects` | `workflow_id` | `synapscale_db.workflows` | `id` |
| `synapscale_db.workspace_projects` | `tenant_id` | `synapscale_db.tenants` | `id` |
| `synapscale_db.workspaces` | `owner_id` | `synapscale_db.users` | `id` |
| `synapscale_db.workspaces` | `tenant_id` | `synapscale_db.tenants` | `id` |

---
*Documentação gerada automaticamente pelo Doc Generator*