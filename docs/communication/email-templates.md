# 📧 **Templates de Email - Migração LLM**

Coleção completa de templates de email para diferentes fases e segmentos da migração dos endpoints LLM.

---

## 🔄 **Template Base - Migração LLM**

### **Subject Line Variables**
```
{PHASE_EMOJI} {URGENCY_LEVEL} - {MAIN_MESSAGE} | SynapScale API
```

### **Header Template**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{subject}}</title>
    <style>
        .container { max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .content { padding: 30px; }
        .phase-badge { background: {{phase_color}}; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; }
        .cta-button { background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #6c757d; }
        .urgent { border-left: 5px solid #dc3545; background: #f8d7da; padding: 15px; margin: 20px 0; }
        .info { border-left: 5px solid #0dcaf0; background: #d1ecf1; padding: 15px; margin: 20px 0; }
        .success { border-left: 5px solid #198754; background: #d1e7dd; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{header_title}}</h1>
            <p>{{header_subtitle}}</p>
            <span class="phase-badge">{{phase_name}}</span>
        </div>
        <div class="content">
```

### **Footer Template**
```html
        </div>
        <div class="footer">
            <p><strong>🔗 Recursos Úteis:</strong></p>
            <p>
                <a href="https://docs.synapscale.com/llm-migration">📖 Guia de Migração</a> | 
                <a href="https://docs.synapscale.com/api">🔧 Documentação API</a> | 
                <a href="mailto:support@synapscale.com">📧 Suporte Técnico</a>
            </p>
            <p>
                <a href="https://discord.gg/synapscale">💬 Discord Community</a> | 
                <a href="https://status.synapscale.com">📊 Status da Plataforma</a>
            </p>
            <hr style="margin: 20px 0;">
            <p>SynapScale - Unified AI Platform</p>
            <p>Se você não deseja mais receber esses emails, <a href="{{unsubscribe_url}}">clique aqui</a>.</p>
        </div>
    </div>
</body>
</html>
```

---

## 🟦 **FASE 1 - Compatibilidade Total**

### 📧 **Email de Anúncio - Novos Endpoints**

**Subject**: `🚀 Nova API LLM Unificada Disponível - Performance Aprimorada | SynapScale`

```html
<h2>🎉 Novos Endpoints LLM Já Disponíveis!</h2>

<p>Olá <strong>{{user_name}}</strong>,</p>

<p>Temos o prazer de anunciar o lançamento da nossa <strong>nova API LLM unificada</strong>! 
Desenvolvida para oferecer uma experiência mais consistente e performática.</p>

<div class="info">
    <h3>✨ Principais Benefícios:</h3>
    <ul>
        <li><strong>Performance 40% melhor</strong> - Respostas mais rápidas</li>
        <li><strong>Interface unificada</strong> - Um endpoint para todos os providers</li>
        <li><strong>Melhor tratamento de erros</strong> - Mensagens mais claras</li>
        <li><strong>Rate limiting otimizado</strong> - Limites mais generosos</li>
        <li><strong>Caching inteligente</strong> - Redução de custos operacionais</li>
    </ul>
</div>

<h3>🔄 Migração Gradual e Sem Pressa</h3>
<p>Não se preocupe! Seus endpoints atuais continuam funcionando normalmente. 
A migração é <strong>totalmente opcional</strong> por enquanto, dando tempo para você testar e se familiarizar.</p>

<h3>🔗 Novos Endpoints:</h3>
<ul>
    <li><code>GET /api/v1/llm/models</code> - Lista modelos disponíveis</li>
    <li><code>POST /api/v1/llm/chat</code> - Chat completion unificado</li>
    <li><code>POST /api/v1/llm/generate</code> - Text generation unificado</li>
</ul>

<a href="https://docs.synapscale.com/llm-migration" class="cta-button">
    📖 Ver Guia Completo de Migração
</a>

<h3>🧪 Como Testar:</h3>
<ol>
    <li>Acesse sua <a href="{{dashboard_url}}">dashboard de desenvolvimento</a></li>
    <li>Gere uma nova API key (opcional, pode usar a atual)</li>
    <li>Teste os novos endpoints em paralelo</li>
    <li>Compare performance e funcionalidades</li>
</ol>

<p><strong>Precisa de ajuda?</strong> Nossa equipe está pronta para apoiar sua migração:</p>
<ul>
    <li>📧 <a href="mailto:migration-support@synapscale.com">migration-support@synapscale.com</a></li>
    <li>💬 Canal #migration no <a href="https://discord.gg/synapscale">Discord</a></li>
    <li>📞 Suporte prioritário: +55 (11) 1234-5678</li>
</ul>

<p>Obrigado por ser parte da família SynapScale!</p>

<p>
<strong>Equipe SynapScale</strong><br>
<em>Unifying AI for Everyone</em>
</p>
```

---

## 🟨 **FASE 2 - Incentivo à Migração**

### 📧 **Email de Incentivo - Desenvolvedores**

**Subject**: `⚠️ Migração Recomendada - Endpoints LLM Legacy serão Descontinuados | SynapScale`

```html
<h2>⏰ Hora de Migrar para a Nova API LLM!</h2>

<p>Olá <strong>{{user_name}}</strong>,</p>

<p>Este é um lembrete importante sobre a migração dos endpoints LLM legacy. 
Detectamos que você ainda está utilizando:</p>

<div class="info">
    <h3>📊 Seu Uso de Endpoints Legacy:</h3>
    <ul>
        <li><strong>{{legacy_endpoint_1}}</strong> - {{usage_count_1}} chamadas/dia</li>
        <li><strong>{{legacy_endpoint_2}}</strong> - {{usage_count_2}} chamadas/dia</li>
        <li><strong>{{legacy_endpoint_3}}</strong> - {{usage_count_3}} chamadas/dia</li>
    </ul>
    <p><em>Última utilização: {{last_legacy_usage}}</em></p>
</div>

<h3>🚨 Cronograma de Descontinuação:</h3>
<ul>
    <li><strong>Até {{phase_2_end}}</strong> - Endpoints legacy funcionam normalmente</li>
    <li><strong>A partir de {{phase_3_start}}</strong> - Redirecionamento automático começará</li>
    <li><strong>{{phase_4_date}}</strong> - Remoção completa dos endpoints legacy</li>
</ul>

<div class="urgent">
    <h3>⚡ Ação Recomendada: Migrar Agora</h3>
    <p>Para evitar qualquer interrupção futura, recomendamos <strong>migrar nas próximas 2 semanas</strong>.</p>
</div>

<h3>🔄 Mapeamento de Migração:</h3>
<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <tr style="background: #f8f9fa;">
        <th style="padding: 10px; border: 1px solid #dee2e6;">Endpoint Legacy</th>
        <th style="padding: 10px; border: 1px solid #dee2e6;">Novo Endpoint</th>
    </tr>
    <tr>
        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>/api/v1/openai/chat</code></td>
        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>/api/v1/llm/chat</code></td>
    </tr>
    <tr>
        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>/api/v1/anthropic/generate</code></td>
        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>/api/v1/llm/generate</code></td>
    </tr>
    <tr>
        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>/api/v1/google/models</code></td>
        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>/api/v1/llm/models</code></td>
    </tr>
</table>

<a href="https://migration.synapscale.com/start?user={{user_id}}" class="cta-button">
    🚀 Iniciar Migração Assistida
</a>

<h3>🎁 Benefícios Exclusivos para Quem Migra Agora:</h3>
<ul>
    <li><strong>30 dias de suporte prioritário</strong> gratuito</li>
    <li><strong>Credits bonus</strong> de R$ 100 para testes</li>
    <li><strong>Rate limits aumentados</strong> em 50% nos primeiros 60 dias</li>
    <li><strong>Consultoria técnica</strong> gratuita de 2 horas</li>
</ul>

<h3>🛠️ Ferramentas de Migração:</h3>
<ul>
    <li>🔧 <strong><a href="{{migration_tool_url}}">Migration Assistant</a></strong> - Ferramenta automática</li>
    <li>📋 <strong><a href="{{checklist_url}}">Migration Checklist</a></strong> - Passo a passo</li>
    <li>🔍 <strong><a href="{{diff_tool_url}}">API Diff Tool</a></strong> - Compare requests/responses</li>
    <li>🧪 <strong><a href="{{sandbox_url}}">Testing Sandbox</a></strong> - Teste antes de migrar</li>
</ul>

<p>Nossa equipe está aqui para tornar sua migração <strong>simples e sem riscos</strong>:</p>

<div class="success">
    <h3>💬 Agende uma Conversa com Nosso Time:</h3>
    <p>📅 <a href="{{calendar_booking_url}}">Agendar reunião de 30 min</a> para planning personalizado</p>
    <p>📧 <a href="mailto:{{dedicated_engineer_email}}">{{dedicated_engineer_name}}</a> - Seu engenheiro dedicado</p>
    <p>💬 WhatsApp: <a href="https://wa.me/{{whatsapp_number}}">{{whatsapp_number}}</a> - Suporte direto</p>
</div>

<p>Juntos, vamos garantir uma migração tranquila! 🤝</p>
```

---

## 🟧 **FASE 3 - Deprecação Ativa**

### 📧 **Email Urgente - Enterprise**

**Subject**: `🚨 URGENTE: Endpoints Legacy Sendo Removidos em 30 Dias - Ação Necessária | SynapScale`

```html
<h2>🚨 Ação Urgente Necessária - 30 Dias Restantes</h2>

<p>Olá <strong>{{enterprise_contact_name}}</strong>,</p>

<p>Como cliente Enterprise da SynapScale, estamos entrando em contato prioritário sobre a 
<strong>remoção iminente dos endpoints LLM legacy</strong>.</p>

<div class="urgent">
    <h3>⏰ CRONOGRAMA CRÍTICO:</h3>
    <ul>
        <li><strong>HOJE</strong> - Redirecionamento automático ativo (50% do tráfego)</li>
        <li><strong>{{countdown_15_days}}</strong> - Redirecionamento aumenta para 90%</li>
        <li><strong>{{countdown_7_days}}</strong> - Apenas fallback de emergência disponível</li>
        <li><strong>{{removal_date}}</strong> - 🔴 <strong>REMOÇÃO COMPLETA</strong></li>
    </ul>
</div>

<h3>📊 Status da Sua Integração:</h3>
<div class="info">
    <table style="width: 100%; border-collapse: collapse;">
        <tr style="background: #f8f9fa;">
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Aplicação</th>
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Status</th>
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Volume Diário</th>
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Risco</th>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #dee2e6;">{{app_1_name}}</td>
            <td style="padding: 12px; border: 1px solid #dee2e6;">❌ Legacy</td>
            <td style="padding: 12px; border: 1px solid #dee2e6;">{{app_1_volume}}</td>
            <td style="padding: 12px; border: 1px solid #dee2e6;">🔴 ALTO</td>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #dee2e6;">{{app_2_name}}</td>
            <td style="padding: 12px; border: 1px solid #dee2e6;">⚠️ Híbrido</td>
            <td style="padding: 12px; border: 1px solid #dee2e6;">{{app_2_volume}}</td>
            <td style="padding: 12px; border: 1px solid #dee2e6;">🟡 MÉDIO</td>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #dee2e6;">{{app_3_name}}</td>
            <td style="padding: 12px; border: 1px solid #dee2e6;">✅ Migrado</td>
            <td style="padding: 12px; border: 1px solid #dee2e6;">{{app_3_volume}}</td>
            <td style="padding: 12px; border: 1px solid #dee2e6;">🟢 BAIXO</td>
        </tr>
    </table>
</div>

<h3>🆘 Suporte Enterprise Emergencial Ativado:</h3>
<div class="success">
    <h4>👨‍💼 Seu Dedicated Success Manager:</h4>
    <p><strong>{{success_manager_name}}</strong><br>
    📧 <a href="mailto:{{success_manager_email}}">{{success_manager_email}}</a><br>
    📱 WhatsApp: <a href="https://wa.me/{{success_manager_phone}}">{{success_manager_phone}}</a><br>
    🗓️ <a href="{{emergency_calendar_url}}">Agendar call de emergência</a></p>

    <h4>🔧 Engenheiro Técnico Dedicado:</h4>
    <p><strong>{{tech_engineer_name}}</strong><br>
    📧 <a href="mailto:{{tech_engineer_email}}">{{tech_engineer_email}}</a><br>
    💬 Slack: <a href="{{slack_connect_url}}">Canal dedicado criado</a></p>
</div>

<h3>🚀 Plano de Migração Express Enterprise:</h3>
<ol>
    <li><strong>Hoje (Dia 0)</strong>
        <ul>
            <li>✅ Call de emergência agendada</li>
            <li>✅ Ambiente de staging dedicado criado</li>
            <li>✅ Engenheiro técnico alocado</li>
        </ul>
    </li>
    <li><strong>Amanhã (Dia 1-2)</strong>
        <ul>
            <li>🔍 Auditoria técnica das integrações</li>
            <li>📋 Plano de migração personalizado</li>
            <li>🧪 Testes em ambiente controlado</li>
        </ul>
    </li>
    <li><strong>Esta Semana (Dia 3-7)</strong>
        <ul>
            <li>⚡ Migração assistida em produção</li>
            <li>📊 Monitoramento 24/7 ativo</li>
            <li>🔧 Ajustes e otimizações</li>
        </ul>
    </li>
    <li><strong>Próxima Semana (Dia 8-14)</strong>
        <ul>
            <li>✅ Validação final</li>
            <li>📈 Análise de performance</li>
            <li>🎯 Otimizações avançadas</li>
        </ul>
    </li>
</ol>

<a href="{{emergency_migration_url}}" class="cta-button" style="background: #dc3545; font-size: 18px; padding: 20px 40px;">
    🆘 INICIAR MIGRAÇÃO EMERGENCIAL AGORA
</a>

<h3>💰 Compensação por Inconvenientes:</h3>
<p>Reconhecemos que essa transição pode causar inconvenientes. Como compensação Enterprise:</p>
<ul>
    <li><strong>3 meses de credits bonus</strong> equivalente a 50% do seu uso atual</li>
    <li><strong>Rate limits dobrados</strong> pelos próximos 6 meses</li>
    <li><strong>SLA aprimorado</strong> para 99.99% uptime garantido</li>
    <li><strong>Suporte dedicado</strong> por 6 meses sem custo adicional</li>
</ul>

<h3>📞 Contatos de Emergência 24/7:</h3>
<ul>
    <li>🆘 <strong>Emergência Técnica:</strong> <a href="tel:{{emergency_phone}}">{{emergency_phone}}</a></li>
    <li>📧 <strong>Escalation Executiva:</strong> <a href="mailto:cto@synapscale.com">cto@synapscale.com</a></li>
    <li>💬 <strong>Status Updates:</strong> <a href="{{status_page_url}}">{{status_page_url}}</a></li>
</ul>

<p><strong>Vamos superar isso juntos!</strong> Nossa equipe está 100% dedicada a garantir que sua migração seja bem-sucedida.</p>

<p>
<strong>Atenciosamente,</strong><br>
<strong>{{cto_name}}</strong><br>
<em>CTO & Co-founder, SynapScale</em><br>
<a href="mailto:{{cto_email}}">{{cto_email}}</a>
</p>
```

---

## 🔴 **FASE 4 - Remoção Final**

### 📧 **Email de Confirmação - Remoção Completa**

**Subject**: `✅ Migração LLM Concluída - Endpoints Legacy Removidos | SynapScale`

```html
<h2>🎉 Migração LLM Concluída com Sucesso!</h2>

<p>Olá <strong>{{user_name}}</strong>,</p>

<p>É com grande satisfação que comunicamos a <strong>conclusão oficial da migração</strong> 
para nossa API LLM unificada!</p>

<div class="success">
    <h3>✅ Status Final da Migração:</h3>
    <ul>
        <li><strong>100% dos endpoints legacy removidos</strong> ✅</li>
        <li><strong>Nova API LLM funcionando perfeitamente</strong> ✅</li>
        <li><strong>Performance otimizada ativa</strong> ✅</li>
        <li><strong>Monitoramento aprimorado ativo</strong> ✅</li>
    </ul>
</div>

<h3>📊 Resultados da Migração:</h3>
<div class="info">
    <h4>🚀 Melhorias de Performance Realizadas:</h4>
    <ul>
        <li><strong>+42% velocidade de resposta</strong> média</li>
        <li><strong>-35% redução de custos</strong> operacionais</li>
        <li><strong>99.98% uptime</strong> nos últimos 30 dias</li>
        <li><strong>+28% satisfaction score</strong> dos desenvolvedores</li>
    </ul>
    
    <h4>📈 Estatísticas da Sua Migração:</h4>
    <ul>
        <li>Data de migração: <strong>{{migration_date}}</strong></li>
        <li>Tempo total: <strong>{{migration_duration}}</strong></li>
        <li>Endpoints migrados: <strong>{{endpoints_migrated}}</strong></li>
        <li>Zero downtime: <strong>✅ Confirmado</strong></li>
    </ul>
</div>

<h3>🔗 Novos Recursos Disponíveis:</h3>
<p>Agora que a migração está completa, você tem acesso a recursos exclusivos da nova API:</p>

<ul>
    <li><strong>🧠 Smart Caching</strong> - Respostas instantâneas para queries repetidas</li>
    <li><strong>⚡ Batch Processing</strong> - Processe múltiplas requests em paralelo</li>
    <li><strong>📊 Analytics Avançado</strong> - Insights detalhados de uso e performance</li>
    <li><strong>🛡️ Enhanced Security</strong> - Autenticação e autorização aprimoradas</li>
    <li><strong>🔄 Auto Retry Logic</strong> - Recuperação automática de falhas transitórias</li>
    <li><strong>📈 Dynamic Scaling</strong> - Rate limits que se ajustam ao seu padrão de uso</li>
</ul>

<a href="https://docs.synapscale.com/llm-api-v2" class="cta-button">
    📖 Explorar Novos Recursos
</a>

<h3>🎁 Benefícios Pós-Migração:</h3>
<p>Como agradecimento pela migração bem-sucedida, você recebeu automaticamente:</p>

<div class="success">
    <ul>
        <li><strong>💳 R$ 200 em credits bonus</strong> - Válidos por 90 dias</li>
        <li><strong>📈 Rate limits Premium</strong> - +50% nos próximos 3 meses</li>
        <li><strong>🎯 Suporte Prioritário</strong> - Fila VIP por 60 dias</li>
        <li><strong>📊 Dashboard Premium</strong> - Analytics avançados gratuitos</li>
        <li><strong>🔔 Early Access</strong> - Novos recursos em preview</li>
    </ul>
</div>

<h3>📚 Recursos para Otimização:</h3>
<p>Maximize o potencial da nova API com nossos recursos:</p>

<ul>
    <li>🎓 <strong><a href="{{optimization_guide_url}}">Guia de Otimização</a></strong> - Best practices avançadas</li>
    <li>🔧 <strong><a href="{{sdk_url}}">SDKs Atualizados</a></strong> - Python, Node.js, PHP, Java</li>
    <li>📖 <strong><a href="{{cookbook_url}}">API Cookbook</a></strong> - Receitas práticas</li>
    <li>💡 <strong><a href="{{examples_url}}">Code Examples</a></strong> - Implementações de referência</li>
    <li>🧪 <strong><a href="{{playground_url}}">API Playground</a></strong> - Teste recursos interativamente</li>
</ul>

<h3>🤝 Feedback e Suporte Contínuo:</h3>
<p>Sua experiência é muito importante para nós:</p>

<ul>
    <li>📝 <strong><a href="{{feedback_form_url}}">Compartilhe seu feedback</a></strong> sobre a migração</li>
    <li>⭐ <strong><a href="{{review_url}}">Avalie nossa API</a></strong> nas plataformas de desenvolvedores</li>
    <li>💬 <strong><a href="{{community_url}}">Junte-se à comunidade</a></strong> de desenvolvedores SynapScale</li>
    <li>📧 <strong><a href="mailto:success@synapscale.com">Contate nosso Success Team</a></strong> para otimizações</li>
</ul>

<h3>🔮 O Que Vem Por Aí:</h3>
<p>Estamos continuamente inovando. Próximos lançamentos:</p>

<ul>
    <li><strong>Q1 2025:</strong> 🧠 AI-Powered Request Optimization</li>
    <li><strong>Q2 2025:</strong> 🌐 Global Edge Deployment</li>
    <li><strong>Q3 2025:</strong> 🔗 Advanced Chain-of-Thought APIs</li>
    <li><strong>Q4 2025:</strong> 🤖 Autonomous Agent Framework</li>
</ul>

<div class="info">
    <h3>📞 Suporte Sempre Disponível:</h3>
    <p>Nossa equipe continua à disposição para qualquer dúvida ou otimização:</p>
    <ul>
        <li>📧 <strong>Suporte Técnico:</strong> <a href="mailto:support@synapscale.com">support@synapscale.com</a></li>
        <li>💬 <strong>Discord Community:</strong> <a href="https://discord.gg/synapscale">#general</a></li>
        <li>📚 <strong>Knowledge Base:</strong> <a href="https://help.synapscale.com">help.synapscale.com</a></li>
        <li>🎥 <strong>Video Tutorials:</strong> <a href="https://youtube.com/@synapscale">YouTube Channel</a></li>
    </ul>
</div>

<p><strong>Obrigado por ser parte da evolução da SynapScale!</strong> 🚀</p>

<p>Juntos, continuamos construindo o futuro da IA unificada.</p>

<p>
<strong>Com gratidão,</strong><br>
<strong>Equipe SynapScale</strong><br>
<em>Unifying AI for Everyone</em>
</p>

<div class="success">
    <h3>🏆 Certificado de Migração</h3>
    <p>Parabéns! Você completou oficialmente a migração para a API LLM v2.</p>
    <a href="{{certificate_url}}" class="cta-button" style="background: #198754;">
        🎖️ Baixar Certificado de Migração
    </a>
</div>
```

---

## 📊 **Personalização Avançada**

### **Variáveis Dinâmicas Disponíveis**

```javascript
// Variáveis de usuário
{{user_name}}
{{user_id}}
{{user_email}}
{{user_tier}} // free, pro, enterprise
{{user_registration_date}}
{{user_last_activity}}

// Variáveis de uso
{{daily_api_calls}}
{{monthly_api_calls}}
{{favorite_endpoints}}
{{last_legacy_usage}}
{{migration_readiness_score}}

// Variáveis de empresa
{{company_name}}
{{company_size}}
{{industry}}
{{technical_contact}}
{{business_contact}}

// Variáveis de migração
{{migration_phase}}
{{phase_progress}}
{{estimated_completion}}
{{recommended_actions}}
{{risk_level}}

// Variáveis de timing
{{current_date}}
{{phase_end_date}}
{{removal_countdown}}
{{business_hours}}
{{user_timezone}}
```

### **Regras de Segmentação**

```python
# Segmentação automática baseada em uso
segmentation_rules = {
    "heavy_users": {
        "criteria": "daily_api_calls > 1000",
        "template": "enterprise_urgent",
        "priority": "high"
    },
    "enterprise_clients": {
        "criteria": "user_tier == 'enterprise'",
        "template": "enterprise_dedicated",
        "priority": "critical"
    },
    "new_users": {
        "criteria": "user_registration_date < 30_days",
        "template": "gentle_introduction", 
        "priority": "low"
    },
    "inactive_users": {
        "criteria": "last_activity > 7_days",
        "template": "reengagement",
        "priority": "medium"
    }
}
```

### **A/B Testing para Templates**

```python
# Configuração de A/B testing
ab_test_config = {
    "subject_line_test": {
        "variant_a": "🚀 Nova API LLM Disponível",
        "variant_b": "⚡ API LLM 40% Mais Rápida Agora Disponível",
        "split": 50,
        "metric": "open_rate"
    },
    "cta_button_test": {
        "variant_a": "Iniciar Migração",
        "variant_b": "Ver Benefícios da Migração",
        "split": 50,
        "metric": "click_rate"
    }
}
```

---

Estes templates fornecem uma base sólida para comunicação eficaz durante todo o processo de migração, garantindo que cada usuário receba mensagens relevantes e acionáveis em cada fase do processo. 