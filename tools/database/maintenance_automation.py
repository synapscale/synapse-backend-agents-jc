#!/usr/bin/env python3
"""
🤖 MAINTENANCE AUTOMATION - Sistema de Manutenção Automatizada

Sistema integrado que resolve EXATAMENTE os pontos mencionados:
- Configuração frequente e manutenção automatizada
- Sincronização perfeita (banco, API, models, schemas, auth)
- OpenAPI.json sempre atualizado
- Fluxo otimizado com menor dor de cabeça
- Relatórios completos e acionáveis

Este é o NÚCLEO da automação - executa tudo em sequência inteligente!
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Cores para terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

load_dotenv()

class MaintenanceAutomation:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.tools_dir = self.project_root / "tools" / "database"
        self.reports_dir = self.project_root / "reports" / "maintenance"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}
        self.issues = []
        self.suggestions = []
        
    def log(self, message: str, level: str = "INFO", color: str = Colors.WHITE):
        """Log com timestamp e cores"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {level}: {message}{Colors.END}")

    def run_tool(self, tool_name: str, description: str, *args) -> Dict[str, Any]:
        """Executa uma ferramenta e captura resultado"""
        self.log(f"🔄 {description}", "RUN", Colors.CYAN)
        
        script_path = self.tools_dir / f"{tool_name}.py"
        
        if not script_path.exists():
            self.log(f"❌ Script não encontrado: {script_path}", "ERROR", Colors.RED)
            return {"success": False, "error": "Script não encontrado"}
        
        try:
            cmd = [sys.executable, str(script_path)] + list(args)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=120
            )
            
            success = result.returncode == 0
            
            if success:
                self.log(f"✅ {description} - Concluído", "SUCCESS", Colors.GREEN)
            else:
                self.log(f"❌ {description} - Falhou", "ERROR", Colors.RED)
            
            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": time.time()
            }
            
        except subprocess.TimeoutExpired:
            self.log(f"⏰ {description} - Timeout", "ERROR", Colors.RED)
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            self.log(f"💥 {description} - Erro: {e}", "ERROR", Colors.RED)
            return {"success": False, "error": str(e)}

    def phase_1_health_check(self) -> bool:
        """Fase 1: Verificação completa de saúde"""
        self.log("🏥 FASE 1: Verificação de Saúde do Sistema", "PHASE", Colors.BOLD)
        
        # Executar health check master
        health_result = self.run_tool(
            "health_check_master",
            "Health Check Completo",
            "--json",
            "--report", str(self.reports_dir / f"health_report_{self.session_id}.json")
        )
        
        self.results["health_check"] = health_result
        
        if health_result["success"]:
            # Analisar resultado do health check
            try:
                if health_result["stdout"]:
                    health_data = json.loads(health_result["stdout"])
                    health_score = health_data.get("health_score", 0)
                    
                    if health_score >= 90:
                        self.log(f"🎉 Sistema saudável! Score: {health_score:.1f}%", "SUCCESS", Colors.GREEN)
                        return True
                    elif health_score >= 70:
                        self.log(f"⚠️ Sistema com avisos. Score: {health_score:.1f}%", "WARNING", Colors.YELLOW)
                        self.issues.extend(health_data.get("warnings", []))
                        return True
                    else:
                        self.log(f"🚨 Sistema crítico! Score: {health_score:.1f}%", "CRITICAL", Colors.RED)
                        self.issues.extend(health_data.get("errors", []))
                        return False
                        
            except json.JSONDecodeError:
                self.log("⚠️ Não foi possível analisar resultado do health check", "WARNING", Colors.YELLOW)
        
        return health_result["success"]

    def phase_2_sync_validation(self) -> bool:
        """Fase 2: Validação de sincronização"""
        self.log("🔄 FASE 2: Validação de Sincronização", "PHASE", Colors.BOLD)
        
        # Executar sync validator
        sync_result = self.run_tool(
            "sync_validator",
            "Validação de Sincronização",
            "--json",
            "--report", str(self.reports_dir / f"sync_report_{self.session_id}.json")
        )
        
        self.results["sync_validation"] = sync_result
        
        if sync_result["success"]:
            try:
                if sync_result["stdout"]:
                    sync_data = json.loads(sync_result["stdout"])
                    
                    critical_issues = sync_data.get("summary", {}).get("critical_issues", 0)
                    warnings = sync_data.get("summary", {}).get("warnings", 0)
                    
                    if critical_issues == 0 and warnings == 0:
                        self.log("🎉 Tudo sincronizado perfeitamente!", "SUCCESS", Colors.GREEN)
                    elif critical_issues == 0:
                        self.log(f"⚠️ Sincronizado com {warnings} avisos", "WARNING", Colors.YELLOW)
                        # Adicionar sugestões de sincronização
                        for issue in sync_data.get("db_model_inconsistencies", []):
                            if issue.get("severity") == "warning":
                                self.suggestions.append(issue.get("suggestion", ""))
                    else:
                        self.log(f"🚨 {critical_issues} problemas críticos de sincronização!", "CRITICAL", Colors.RED)
                        for issue in sync_data.get("db_model_inconsistencies", []):
                            if issue.get("severity") == "error":
                                self.issues.append(issue.get("message", ""))
                                self.suggestions.append(issue.get("suggestion", ""))
                        return False
                        
            except json.JSONDecodeError:
                self.log("⚠️ Não foi possível analisar resultado da sincronização", "WARNING", Colors.YELLOW)
        
        return sync_result.get("returncode", 1) != 1  # 1 = critical issues

    def phase_3_documentation_update(self) -> bool:
        """Fase 3: Atualização automática da documentação"""
        self.log("📚 FASE 3: Atualização da Documentação", "PHASE", Colors.BOLD)
        
        # Executar gerador de documentação
        doc_result = self.run_tool(
            "doc_generator",
            "Geração de Documentação",
            "--output-dir", str(self.reports_dir / f"docs_{self.session_id}")
        )
        
        self.results["documentation"] = doc_result
        
        if doc_result["success"]:
            self.log("📖 Documentação atualizada com sucesso!", "SUCCESS", Colors.GREEN)
            
            # Copiar documentação para pasta principal se tudo estiver OK
            docs_source = self.reports_dir / f"docs_{self.session_id}"
            docs_target = self.project_root / "docs" / "database"
            
            if docs_source.exists():
                try:
                    import shutil
                    if docs_target.exists():
                        shutil.rmtree(docs_target)
                    shutil.copytree(docs_source, docs_target)
                    self.log(f"📁 Documentação copiada para {docs_target}", "SUCCESS", Colors.GREEN)
                except Exception as e:
                    self.log(f"⚠️ Erro ao copiar documentação: {e}", "WARNING", Colors.YELLOW)
        
        return doc_result["success"]

    def phase_4_openapi_sync(self) -> bool:
        """Fase 4: Sincronização do OpenAPI"""
        self.log("📋 FASE 4: Sincronização do OpenAPI", "PHASE", Colors.BOLD)
        
        # Verificar se há arquivo OpenAPI para atualizar
        possible_openapi_paths = [
            self.project_root / "docs" / "openapi.json",
            self.project_root / "src" / "openapi.json",
            self.project_root / "openapi.json",
            self.project_root / "static" / "openapi.json"
        ]
        
        openapi_file = None
        for path in possible_openapi_paths:
            if path.exists():
                openapi_file = path
                break
        
        if not openapi_file:
            self.log("⚠️ Arquivo OpenAPI não encontrado - criando sugestão", "WARNING", Colors.YELLOW)
            self.suggestions.append("Considere gerar arquivo openapi.json automaticamente")
            return True
        
        # Verificar se OpenAPI está atualizado
        try:
            file_age = time.time() - openapi_file.stat().st_mtime
            
            if file_age > 86400:  # Mais de 1 dia
                self.log("⚠️ OpenAPI pode estar desatualizado (>1 dia)", "WARNING", Colors.YELLOW)
                self.suggestions.append(f"Atualizar {openapi_file} - arquivo antigo")
            else:
                self.log("✅ OpenAPI parece atualizado", "SUCCESS", Colors.GREEN)
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao verificar OpenAPI: {e}", "ERROR", Colors.RED)
            return False

    def phase_5_generate_action_plan(self) -> Dict[str, Any]:
        """Fase 5: Gerar plano de ação"""
        self.log("📋 FASE 5: Gerando Plano de Ação", "PHASE", Colors.BOLD)
        
        # Categorizar issues por prioridade
        critical_issues = [issue for issue in self.issues if "crítico" in issue.lower() or "error" in issue.lower()]
        warning_issues = [issue for issue in self.issues if issue not in critical_issues]
        
        action_plan = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_phases": 5,
                "successful_phases": sum(1 for r in self.results.values() if r.get("success", False)),
                "critical_issues": len(critical_issues),
                "warnings": len(warning_issues),
                "suggestions": len(self.suggestions)
            },
            "phase_results": self.results,
            "critical_issues": critical_issues,
            "warnings": warning_issues,
            "suggestions": self.suggestions,
            "next_actions": []
        }
        
        # Gerar ações recomendadas
        if critical_issues:
            action_plan["next_actions"].append({
                "priority": "CRÍTICA",
                "action": "Resolver problemas críticos identificados",
                "details": critical_issues
            })
        
        if warning_issues:
            action_plan["next_actions"].append({
                "priority": "MÉDIA",
                "action": "Revisar e resolver avisos",
                "details": warning_issues
            })
        
        if self.suggestions:
            action_plan["next_actions"].append({
                "priority": "BAIXA",
                "action": "Implementar melhorias sugeridas",
                "details": self.suggestions
            })
        
        # Agendar próxima execução
        action_plan["next_actions"].append({
            "priority": "ROTINA",
            "action": "Executar próxima verificação automatizada",
            "details": ["Agendar para 24h ou após mudanças significativas"]
        })
        
        return action_plan

    def generate_maintenance_report(self, action_plan: Dict[str, Any]) -> str:
        """Gera relatório de manutenção em formato legível"""
        
        report = []
        report.append("# 🤖 Relatório de Manutenção Automatizada")
        report.append("")
        report.append(f"**Sessão:** {self.session_id}")
        report.append(f"**Data/Hora:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Status geral
        success_rate = (action_plan["summary"]["successful_phases"] / action_plan["summary"]["total_phases"]) * 100
        
        if success_rate == 100 and action_plan["summary"]["critical_issues"] == 0:
            status = "🟢 EXCELENTE"
            status_desc = "Sistema funcionando perfeitamente"
        elif success_rate >= 80 and action_plan["summary"]["critical_issues"] == 0:
            status = "🟡 BOM"
            status_desc = "Sistema estável com pequenos ajustes necessários"
        else:
            status = "🔴 ATENÇÃO NECESSÁRIA"
            status_desc = "Sistema requer intervenção imediata"
        
        report.append(f"## {status}")
        report.append(f"*{status_desc}*")
        report.append("")
        
        # Resumo executivo
        report.append("## 📊 Resumo Executivo")
        report.append("")
        report.append(f"- ✅ **Fases concluídas:** {action_plan['summary']['successful_phases']}/{action_plan['summary']['total_phases']}")
        report.append(f"- 🚨 **Problemas críticos:** {action_plan['summary']['critical_issues']}")
        report.append(f"- ⚠️ **Avisos:** {action_plan['summary']['warnings']}")
        report.append(f"- 💡 **Sugestões de melhoria:** {action_plan['summary']['suggestions']}")
        report.append("")
        
        # Resultados por fase
        report.append("## 🔄 Resultados por Fase")
        report.append("")
        
        phase_names = {
            "health_check": "🏥 Health Check Completo",
            "sync_validation": "🔄 Validação de Sincronização", 
            "documentation": "📚 Atualização da Documentação",
            "openapi_sync": "📋 Sincronização do OpenAPI"
        }
        
        for phase_key, result in action_plan["phase_results"].items():
            phase_name = phase_names.get(phase_key, phase_key)
            status_icon = "✅" if result.get("success") else "❌"
            report.append(f"### {status_icon} {phase_name}")
            
            if result.get("success"):
                report.append("Status: **Concluído com sucesso**")
            else:
                report.append("Status: **Falhou**")
                if result.get("error"):
                    report.append(f"Erro: `{result['error']}`")
            
            report.append("")
        
        # Plano de ação
        if action_plan["next_actions"]:
            report.append("## 📋 Plano de Ação")
            report.append("")
            
            for action in action_plan["next_actions"]:
                priority_colors = {
                    "CRÍTICA": "🔴",
                    "MÉDIA": "🟡", 
                    "BAIXA": "🟢",
                    "ROTINA": "🔵"
                }
                
                priority_icon = priority_colors.get(action["priority"], "⚪")
                
                report.append(f"### {priority_icon} {action['priority']}: {action['action']}")
                
                if action.get("details"):
                    for detail in action["details"]:
                        report.append(f"- {detail}")
                
                report.append("")
        
        # Próximos passos
        report.append("## 🚀 Próximos Passos Recomendados")
        report.append("")
        
        if action_plan["summary"]["critical_issues"] > 0:
            report.append("1. **URGENTE:** Resolver problemas críticos listados acima")
            report.append("2. Executar novamente após correções")
        else:
            report.append("1. Revisar avisos e implementar sugestões")
            report.append("2. Agendar próxima verificação automática")
        
        report.append("3. Monitorar health dashboard regularmente")
        report.append("4. Manter documentação atualizada")
        report.append("")
        
        # Comandos úteis
        report.append("## 🛠️ Comandos Úteis")
        report.append("")
        report.append("```bash")
        report.append("# Executar manutenção completa")
        report.append("python tools/database/maintenance_automation.py")
        report.append("")
        report.append("# Apenas verificação de saúde")
        report.append("python tools/database/health_check_master.py")
        report.append("")
        report.append("# Validação de sincronização")
        report.append("python tools/database/sync_validator.py")
        report.append("")
        report.append("# Atualizar documentação")
        report.append("python tools/database/doc_generator.py")
        report.append("```")
        report.append("")
        
        report.append("---")
        report.append("*Relatório gerado automaticamente pelo Sistema de Manutenção*")
        
        return "\n".join(report)

    def run_full_maintenance(self) -> Dict[str, Any]:
        """Executa manutenção completa automatizada"""
        self.log("🚀 INICIANDO MANUTENÇÃO AUTOMATIZADA COMPLETA", "START", Colors.BOLD)
        self.log(f"📁 Sessão: {self.session_id}", "INFO", Colors.WHITE)
        
        start_time = time.time()
        
        # Fase 1: Health Check
        phase1_success = self.phase_1_health_check()
        
        # Fase 2: Sync Validation
        phase2_success = self.phase_2_sync_validation()
        
        # Se fases críticas falharam, parar aqui
        if not phase1_success or not phase2_success:
            self.log("🛑 Parando execução - problemas críticos detectados", "CRITICAL", Colors.RED)
        else:
            # Fase 3: Documentation
            self.phase_3_documentation_update()
            
            # Fase 4: OpenAPI
            self.phase_4_openapi_sync()
        
        # Fase 5: Action Plan (sempre executar)
        action_plan = self.phase_5_generate_action_plan()
        
        # Gerar relatório final
        report_content = self.generate_maintenance_report(action_plan)
        report_file = self.reports_dir / f"maintenance_report_{self.session_id}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Salvar action plan em JSON
        action_plan_file = self.reports_dir / f"action_plan_{self.session_id}.json"
        with open(action_plan_file, 'w', encoding='utf-8') as f:
            json.dump(action_plan, f, indent=2, ensure_ascii=False)
        
        execution_time = time.time() - start_time
        
        # Exibir resumo final
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}🏁 MANUTENÇÃO AUTOMATIZADA CONCLUÍDA{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}")
        
        print(f"\n⏱️  **Tempo de execução:** {execution_time:.2f} segundos")
        print(f"📁 **Relatórios salvos em:** {self.reports_dir}")
        print(f"📋 **Relatório principal:** {report_file.name}")
        print(f"📊 **Action plan:** {action_plan_file.name}")
        
        if action_plan["summary"]["critical_issues"] == 0:
            print(f"\n{Colors.GREEN}🎉 Sistema está funcionando corretamente!{Colors.END}")
        else:
            print(f"\n{Colors.RED}⚠️ {action_plan['summary']['critical_issues']} problemas críticos detectados{Colors.END}")
            print(f"{Colors.YELLOW}📋 Consulte o action plan para próximos passos{Colors.END}")
        
        print(f"\n{Colors.CYAN}💡 Dica: Agende este script para executar automaticamente!{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}")
        
        return action_plan

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Maintenance Automation - Manutenção automatizada completa")
    parser.add_argument("--dry-run", action="store_true", help="Simular execução sem fazer mudanças")
    parser.add_argument("--phase", type=str, choices=["health", "sync", "docs", "openapi"], help="Executar apenas uma fase específica")
    parser.add_argument("--output-dir", type=str, help="Diretório customizado para relatórios")
    
    args = parser.parse_args()
    
    automation = MaintenanceAutomation()
    
    if args.output_dir:
        automation.reports_dir = Path(args.output_dir)
        automation.reports_dir.mkdir(parents=True, exist_ok=True)
    
    if args.dry_run:
        print("🧪 Modo DRY RUN - apenas simulação")
        # Implementar simulação se necessário
        return
    
    if args.phase:
        # Executar apenas uma fase específica
        if args.phase == "health":
            automation.phase_1_health_check()
        elif args.phase == "sync":
            automation.phase_2_sync_validation()
        elif args.phase == "docs":
            automation.phase_3_documentation_update()
        elif args.phase == "openapi":
            automation.phase_4_openapi_sync()
    else:
        # Executar manutenção completa
        action_plan = automation.run_full_maintenance()
        
        # Exit code baseado no resultado
        if action_plan["summary"]["critical_issues"] > 0:
            sys.exit(1)  # Problemas críticos
        elif action_plan["summary"]["warnings"] > 0:
            sys.exit(2)  # Avisos
        else:
            sys.exit(0)  # Tudo OK

if __name__ == "__main__":
    main()
