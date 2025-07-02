#!/usr/bin/env python3
"""
Script para validação de relacionamentos RBAC
Task 2.5: Estabelecer relacionamentos RBAC
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def validate_rbac_relationships():
    """Valida todos os relacionamentos RBAC"""
    print("🔍 Validação de Relacionamentos RBAC")
    print("=" * 80)

    issues = []
    success_count = 0

    try:
        # Importar todos os modelos RBAC
        from synapse.models.rbac_permission import RBACPermission
        from synapse.models.rbac_role import RBACRole
        from synapse.models.rbac_role_permission import RBACRolePermission
        from synapse.models.user_tenant_role import UserTenantRole
        from synapse.models.user import User
        from synapse.models.tenant import Tenant

        print("✅ Todos os modelos RBAC importados com sucesso")
        success_count += 1

        # Verificar relacionamentos do RBACPermission
        print("\n📋 Validando relacionamentos de RBACPermission:")
        perm_attrs = dir(RBACPermission)

        # Relacionamentos esperados
        expected_perm_relationships = [
            "tenant",  # RBACPermission -> Tenant
            "role_permissions",  # RBACPermission -> RBACRolePermission (one-to-many)
        ]

        for rel in expected_perm_relationships:
            if rel in perm_attrs:
                print(f"  ✅ {rel} - Relacionamento configurado")
                success_count += 1
            else:
                issues.append(f"❌ RBACPermission.{rel} - Relacionamento faltando")

        # Verificar relacionamentos do RBACRole
        print("\n🎭 Validando relacionamentos de RBACRole:")
        role_attrs = dir(RBACRole)

        expected_role_relationships = [
            "tenant",  # RBACRole -> Tenant
            "permissions",  # RBACRole -> RBACRolePermission (one-to-many)
            "user_assignments",  # RBACRole -> UserTenantRole (one-to-many)
        ]

        for rel in expected_role_relationships:
            if rel in role_attrs:
                print(f"  ✅ {rel} - Relacionamento configurado")
                success_count += 1
            else:
                issues.append(f"❌ RBACRole.{rel} - Relacionamento faltando")

        # Verificar relacionamentos do RBACRolePermission
        print("\n🔗 Validando relacionamentos de RBACRolePermission:")
        role_perm_attrs = dir(RBACRolePermission)

        expected_role_perm_relationships = [
            "role",  # RBACRolePermission -> RBACRole
            "permission",  # RBACRolePermission -> RBACPermission
            "tenant",  # RBACRolePermission -> Tenant
        ]

        for rel in expected_role_perm_relationships:
            if rel in role_perm_attrs:
                print(f"  ✅ {rel} - Relacionamento configurado")
                success_count += 1
            else:
                issues.append(f"❌ RBACRolePermission.{rel} - Relacionamento faltando")

        # Verificar relacionamentos do UserTenantRole
        print("\n👤 Validando relacionamentos de UserTenantRole:")
        user_role_attrs = dir(UserTenantRole)

        expected_user_role_relationships = [
            "user",  # UserTenantRole -> User
            "tenant",  # UserTenantRole -> Tenant
            "role",  # UserTenantRole -> RBACRole
            "granter",  # UserTenantRole -> User (foreign_keys=[granted_by])
        ]

        for rel in expected_user_role_relationships:
            if rel in user_role_attrs:
                print(f"  ✅ {rel} - Relacionamento configurado")
                success_count += 1
            else:
                issues.append(f"❌ UserTenantRole.{rel} - Relacionamento faltando")

        # Verificar back_populates em User
        print("\n👥 Validando back_populates em User:")
        user_attrs = dir(User)

        expected_user_back_refs = [
            "tenant_roles"  # User -> UserTenantRole (back_populates)
        ]

        for rel in expected_user_back_refs:
            if rel in user_attrs:
                print(f"  ✅ {rel} - Back reference configurado")
                success_count += 1
            else:
                issues.append(f"❌ User.{rel} - Back reference faltando")

        # Verificar back_populates em Tenant
        print("\n🏢 Validando back_populates em Tenant:")
        tenant_attrs = dir(Tenant)

        expected_tenant_back_refs = [
            "rbac_permissions",  # Tenant -> RBACPermission
            "rbac_roles",  # Tenant -> RBACRole
            "user_roles",  # Tenant -> UserTenantRole
        ]

        for rel in expected_tenant_back_refs:
            if rel in tenant_attrs:
                print(f"  ✅ {rel} - Back reference configurado")
                success_count += 1
            else:
                issues.append(f"❌ Tenant.{rel} - Back reference faltando")

        # Testar métodos de relacionamento
        print("\n🧪 Testando métodos de relacionamento:")

        # Testar métodos de RBACPermission
        try:
            import uuid

            test_perm = RBACPermission.create_global_permission(
                key="test.read", description="Test permission"
            )
            print("  ✅ RBACPermission.create_global_permission() funciona")
            success_count += 1
        except Exception as e:
            issues.append(f"❌ RBACPermission.create_global_permission() falhou: {e}")

        # Testar métodos de RBACRole
        try:
            test_role = RBACRole.create_system_role(
                name="test_role", description="Test role"
            )
            print("  ✅ RBACRole.create_system_role() funciona")
            success_count += 1
        except Exception as e:
            issues.append(f"❌ RBACRole.create_system_role() falhou: {e}")

        # Testar métodos de RBACRolePermission
        try:
            test_role_perm = RBACRolePermission.create_assignment(
                role_id=str(uuid.uuid4()), permission_id=str(uuid.uuid4())
            )
            print("  ✅ RBACRolePermission.create_assignment() funciona")
            success_count += 1
        except Exception as e:
            issues.append(f"❌ RBACRolePermission.create_assignment() falhou: {e}")

        # Testar métodos de UserTenantRole
        try:
            test_user_role = UserTenantRole.assign_role(
                user_id=str(uuid.uuid4()),
                tenant_id=str(uuid.uuid4()),
                role_id=str(uuid.uuid4()),
            )
            print("  ✅ UserTenantRole.assign_role() funciona")
            success_count += 1
        except Exception as e:
            issues.append(f"❌ UserTenantRole.assign_role() falhou: {e}")

    except Exception as e:
        issues.append(f"❌ Erro crítico na importação: {e}")
        import traceback

        traceback.print_exc()

    # Resumo
    print(f"\n📊 RESUMO DA VALIDAÇÃO RBAC")
    print("=" * 80)
    print(f"✅ Sucessos: {success_count}")
    print(f"❌ Issues: {len(issues)}")

    if issues:
        print(f"\n🚨 PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"\n🎉 TODOS OS RELACIONAMENTOS RBAC ESTÃO FUNCIONANDO PERFEITAMENTE!")

    # Salvar relatório
    report_path = Path(".taskmaster/reports/rbac_relationships_validation.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        f.write("RELATÓRIO DE VALIDAÇÃO DE RELACIONAMENTOS RBAC\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total de sucessos: {success_count}\n")
        f.write(f"Total de issues: {len(issues)}\n\n")

        if issues:
            f.write("PROBLEMAS ENCONTRADOS:\n")
            for issue in issues:
                f.write(f"- {issue}\n")
        else:
            f.write("TODOS OS RELACIONAMENTOS FUNCIONANDO PERFEITAMENTE!\n")

    print(f"\n📄 Relatório salvo em: {report_path}")

    return len(issues) == 0


if __name__ == "__main__":
    success = validate_rbac_relationships()
    sys.exit(0 if success else 1)
