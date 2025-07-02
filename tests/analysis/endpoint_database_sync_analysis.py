#!/usr/bin/env python3
"""
Endpoint-Database Synchronization Analysis for SynapScale

This script analyzes the synchronization between:
1. PostgreSQL database tables (from database structure analysis)
2. API endpoints (from current_openapi.json)
3. CRUD operation coverage
4. Missing endpoints or orphaned tables

The analysis helps ensure that database structure is properly exposed via API endpoints.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple
from pathlib import Path


def load_database_analysis() -> Dict[str, Any]:
    """Load the most recent database structure analysis"""
    analysis_files = [f for f in os.listdir('.') if f.startswith('database_structure_analysis_') and f.endswith('.json')]
    
    if not analysis_files:
        raise FileNotFoundError("No database structure analysis file found. Run check_database_structure.py first.")
    
    # Get the most recent file
    latest_file = sorted(analysis_files)[-1]
    print(f"📊 Loading database analysis from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)


def load_openapi_spec() -> Dict[str, Any]:
    """Load the OpenAPI specification"""
    openapi_file = 'current_openapi.json'
    
    if not os.path.exists(openapi_file):
        raise FileNotFoundError(f"OpenAPI specification file not found: {openapi_file}")
    
    print(f"🔗 Loading OpenAPI specification from: {openapi_file}")
    
    with open(openapi_file, 'r') as f:
        return json.load(f)


def extract_table_names(db_analysis: Dict[str, Any]) -> Set[str]:
    """Extract all table names from database analysis"""
    return set(db_analysis.get('tables', {}).keys())


def extract_api_endpoints(openapi_spec: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extract and organize API endpoints by resource/entity"""
    paths = openapi_spec.get('paths', {})
    endpoints = {}
    
    for path, methods in paths.items():
        # Skip non-API paths
        if not path.startswith('/api/v1/'):
            continue
            
        # Extract resource name from path
        path_parts = path.strip('/').split('/')
        if len(path_parts) < 3:
            continue
            
        resource = path_parts[2]  # Skip 'api' and 'v1'
        
        # Handle nested resources (e.g., /api/v1/users/{id}/workspaces)
        if len(path_parts) > 3 and not path_parts[3].startswith('{'):
            resource = f"{resource}_{path_parts[3]}"
        
        if resource not in endpoints:
            endpoints[resource] = {
                'paths': [],
                'operations': {},
                'crud_operations': {
                    'create': False,
                    'read': False,
                    'update': False,
                    'delete': False,
                    'list': False
                }
            }
        
        endpoints[resource]['paths'].append(path)
        
        # Analyze HTTP methods for CRUD operations
        for method, operation in methods.items():
            if method.upper() == 'POST':
                endpoints[resource]['crud_operations']['create'] = True
            elif method.upper() == 'GET':
                if '{id}' in path or '{' in path:
                    endpoints[resource]['crud_operations']['read'] = True
                else:
                    endpoints[resource]['crud_operations']['list'] = True
            elif method.upper() in ['PUT', 'PATCH']:
                endpoints[resource]['crud_operations']['update'] = True
            elif method.upper() == 'DELETE':
                endpoints[resource]['crud_operations']['delete'] = True
            
            endpoints[resource]['operations'][f"{method.upper()} {path}"] = {
                'summary': operation.get('summary', ''),
                'description': operation.get('description', ''),
                'tags': operation.get('tags', [])
            }
    
    return endpoints


def analyze_table_endpoint_mapping(tables: Set[str], endpoints: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze mapping between database tables and API endpoints"""
    
    mapping_analysis = {
        'mapped_tables': {},
        'unmapped_tables': set(),
        'endpoint_only_resources': set(),
        'mapping_quality': {},
        'recommendations': []
    }
    
    # Convert endpoint resource names to potential table name variations
    endpoint_resources = set(endpoints.keys())
    
    for table in tables:
        # Try to find matching endpoint resource
        potential_matches = []
        
        # Direct match
        if table in endpoint_resources:
            potential_matches.append(table)
        
        # Singular/plural variations
        singular_table = table.rstrip('s') if table.endswith('s') else table
        plural_table = table + 's' if not table.endswith('s') else table
        
        for resource in endpoint_resources:
            resource_base = resource.split('_')[0]  # Handle composite resources
            
            # Check various naming patterns
            if (table == resource_base or 
                singular_table == resource_base or 
                plural_table == resource_base or
                table.replace('_', '') == resource_base.replace('_', '') or
                table in resource or resource in table):
                potential_matches.append(resource)
        
        if potential_matches:
            # Choose the best match (prefer exact match, then closest)
            best_match = potential_matches[0]
            if table in potential_matches:
                best_match = table
            
            mapping_analysis['mapped_tables'][table] = {
                'endpoint_resource': best_match,
                'potential_matches': potential_matches,
                'crud_coverage': endpoints[best_match]['crud_operations'],
                'endpoints': endpoints[best_match]['paths']
            }
            
            # Analyze CRUD coverage quality
            crud_ops = endpoints[best_match]['crud_operations']
            coverage_score = sum(crud_ops.values()) / len(crud_ops)
            
            mapping_analysis['mapping_quality'][table] = {
                'crud_coverage_score': coverage_score,
                'missing_operations': [op for op, exists in crud_ops.items() if not exists],
                'has_full_crud': coverage_score >= 0.8
            }
        else:
            mapping_analysis['unmapped_tables'].add(table)
    
    # Find endpoint resources without corresponding tables
    mapped_resources = {data['endpoint_resource'] for data in mapping_analysis['mapped_tables'].values()}
    mapping_analysis['endpoint_only_resources'] = endpoint_resources - mapped_resources
    
    return mapping_analysis


def categorize_tables_by_importance(tables: Set[str]) -> Dict[str, List[str]]:
    """Categorize tables by their importance/role in the system"""
    
    categories = {
        'core_entities': [],
        'relationship_tables': [],
        'audit_logs': [],
        'system_tables': [],
        'feature_specific': [],
        'analytics': [],
        'configuration': []
    }
    
    for table in tables:
        table_lower = table.lower()
        
        if any(core in table_lower for core in ['user', 'workspace', 'agent', 'workflow', 'llm', 'file']):
            categories['core_entities'].append(table)
        elif any(rel in table_lower for rel in ['_member', '_permission', '_role', '_acl', 'mapping']):
            categories['relationship_tables'].append(table)
        elif any(audit in table_lower for audit in ['audit', '_log', 'history', 'tracking']):
            categories['audit_logs'].append(table)
        elif any(sys in table_lower for sys in ['alembic', 'system_', 'health', 'performance']):
            categories['system_tables'].append(table)
        elif any(analytics in table_lower for analytics in ['analytic', 'metric', 'report', 'insight', 'event']):
            categories['analytics'].append(table)
        elif any(config in table_lower for config in ['config', 'setting', 'template', 'feature']):
            categories['configuration'].append(table)
        else:
            categories['feature_specific'].append(table)
    
    return categories


def generate_sync_recommendations(mapping_analysis: Dict[str, Any], table_categories: Dict[str, List[str]]) -> List[str]:
    """Generate recommendations for improving endpoint-database synchronization"""
    
    recommendations = []
    
    # Critical missing endpoints for core entities
    core_unmapped = [table for table in mapping_analysis['unmapped_tables'] 
                    if table in table_categories['core_entities']]
    
    if core_unmapped:
        recommendations.append(f"🚨 CRITICAL: Add API endpoints for core entities: {', '.join(core_unmapped)}")
    
    # Incomplete CRUD coverage for important tables
    incomplete_crud = []
    for table, quality in mapping_analysis['mapping_quality'].items():
        if table in table_categories['core_entities'] and not quality['has_full_crud']:
            missing_ops = ', '.join(quality['missing_operations'])
            incomplete_crud.append(f"{table} (missing: {missing_ops})")
    
    if incomplete_crud:
        recommendations.append(f"⚠️  Add missing CRUD operations for: {'; '.join(incomplete_crud)}")
    
    # Feature-specific tables that might need endpoints
    feature_unmapped = [table for table in mapping_analysis['unmapped_tables'] 
                       if table in table_categories['feature_specific']]
    
    if feature_unmapped:
        recommendations.append(f"📋 Consider adding endpoints for feature tables: {', '.join(feature_unmapped[:5])}")
    
    # Orphaned endpoints (endpoints without corresponding tables)
    if mapping_analysis['endpoint_only_resources']:
        recommendations.append(f"🔍 Review endpoints without corresponding tables: {', '.join(list(mapping_analysis['endpoint_only_resources'])[:3])}")
    
    # Analytics and reporting endpoints
    analytics_unmapped = [table for table in mapping_analysis['unmapped_tables'] 
                         if table in table_categories['analytics']]
    
    if analytics_unmapped:
        recommendations.append(f"📊 Consider analytics endpoints for: {', '.join(analytics_unmapped[:3])}")
    
    return recommendations


def generate_comprehensive_report(analysis_results: Dict[str, Any]) -> str:
    """Generate a comprehensive markdown report"""
    
    report = f"""# SynapScale Endpoint-Database Synchronization Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

- **Total Database Tables**: {analysis_results['database_summary']['total_tables']}
- **Total API Resources**: {analysis_results['api_summary']['total_resources']}
- **Mapped Tables**: {len(analysis_results['mapping']['mapped_tables'])}
- **Unmapped Tables**: {len(analysis_results['mapping']['unmapped_tables'])}
- **Sync Coverage**: {analysis_results['sync_metrics']['coverage_percentage']:.1f}%

## Synchronization Metrics

| Metric | Value |
|--------|-------|
| Database Tables | {analysis_results['database_summary']['total_tables']} |
| API Resources | {analysis_results['api_summary']['total_resources']} |
| Mapped Tables | {len(analysis_results['mapping']['mapped_tables'])} |
| Unmapped Tables | {len(analysis_results['mapping']['unmapped_tables'])} |
| Coverage Score | {analysis_results['sync_metrics']['coverage_percentage']:.1f}% |
| Full CRUD Coverage | {analysis_results['sync_metrics']['full_crud_count']} tables |

## Table Categories Analysis

"""
    
    for category, tables in analysis_results['table_categories'].items():
        if tables:
            report += f"### {category.replace('_', ' ').title()}\n"
            report += f"- Count: {len(tables)}\n"
            report += f"- Tables: {', '.join(tables[:10])}"
            if len(tables) > 10:
                report += f" (and {len(tables) - 10} more)"
            report += "\n\n"
    
    report += f"""## Mapping Quality

### Well-Mapped Tables (Full CRUD)
"""
    
    full_crud_tables = []
    for table, data in analysis_results['mapping']['mapped_tables'].items():
        quality = analysis_results['mapping']['mapping_quality'][table]
        if quality['has_full_crud']:
            full_crud_tables.append(f"- **{table}** → `{data['endpoint_resource']}` (Score: {quality['crud_coverage_score']:.1f})")
    
    report += '\n'.join(full_crud_tables[:10])
    if len(full_crud_tables) > 10:
        report += f"\n\n... and {len(full_crud_tables) - 10} more"
    
    report += f"""

### Tables with Incomplete CRUD Coverage
"""
    
    incomplete_tables = []
    for table, data in analysis_results['mapping']['mapped_tables'].items():
        quality = analysis_results['mapping']['mapping_quality'][table]
        if not quality['has_full_crud']:
            missing = ', '.join(quality['missing_operations'])
            incomplete_tables.append(f"- **{table}** → `{data['endpoint_resource']}` (Missing: {missing})")
    
    report += '\n'.join(incomplete_tables)
    
    report += f"""

### Unmapped Tables
"""
    
    for table in sorted(analysis_results['mapping']['unmapped_tables']):
        report += f"- **{table}**\n"
    
    report += f"""

## Recommendations

"""
    
    for i, rec in enumerate(analysis_results['recommendations'], 1):
        report += f"{i}. {rec}\n"
    
    report += f"""

## API Resources Without Database Tables

"""
    
    for resource in sorted(analysis_results['mapping']['endpoint_only_resources']):
        report += f"- `{resource}`\n"
    
    return report


def analyze_endpoint_database_sync():
    """Main function to analyze endpoint-database synchronization"""
    
    print("🔍 Starting Endpoint-Database Synchronization Analysis")
    print("=" * 70)
    
    # Load data
    try:
        db_analysis = load_database_analysis()
        openapi_spec = load_openapi_spec()
    except FileNotFoundError as e:
        print(f"❌ Error loading required files: {e}")
        return None
    
    # Extract information
    print("📊 Extracting database tables...")
    tables = extract_table_names(db_analysis)
    print(f"Found {len(tables)} database tables")
    
    print("🔗 Extracting API endpoints...")
    endpoints = extract_api_endpoints(openapi_spec)
    print(f"Found {len(endpoints)} API resources")
    
    # Categorize tables
    print("📋 Categorizing tables by importance...")
    table_categories = categorize_tables_by_importance(tables)
    
    # Analyze mapping
    print("🔄 Analyzing table-endpoint mapping...")
    mapping_analysis = analyze_table_endpoint_mapping(tables, endpoints)
    
    # Generate metrics
    total_tables = len(tables)
    mapped_tables = len(mapping_analysis['mapped_tables'])
    coverage_percentage = (mapped_tables / total_tables) * 100 if total_tables > 0 else 0
    
    full_crud_count = sum(1 for quality in mapping_analysis['mapping_quality'].values() 
                         if quality['has_full_crud'])
    
    # Generate recommendations
    print("💡 Generating recommendations...")
    recommendations = generate_sync_recommendations(mapping_analysis, table_categories)
    
    # Compile results
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'database_summary': {
            'total_tables': total_tables,
            'schema': db_analysis['database_config']['schema']
        },
        'api_summary': {
            'total_resources': len(endpoints),
            'version': openapi_spec['info']['version']
        },
        'table_categories': table_categories,
        'mapping': mapping_analysis,
        'sync_metrics': {
            'coverage_percentage': coverage_percentage,
            'mapped_count': mapped_tables,
            'unmapped_count': len(mapping_analysis['unmapped_tables']),
            'full_crud_count': full_crud_count
        },
        'recommendations': recommendations,
        'endpoints_detail': endpoints
    }
    
    # Save analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"endpoint_sync_analysis_{timestamp}.json"
    
    with open(json_filename, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    # Generate report
    report_content = generate_comprehensive_report(analysis_results)
    report_filename = f"endpoint_sync_report_{timestamp}.md"
    
    with open(report_filename, 'w') as f:
        f.write(report_content)
    
    # Print summary
    print(f"\n📊 SYNCHRONIZATION ANALYSIS SUMMARY")
    print(f"=" * 50)
    print(f"Database Tables: {total_tables}")
    print(f"API Resources: {len(endpoints)}")
    print(f"Mapped Tables: {mapped_tables} ({coverage_percentage:.1f}%)")
    print(f"Unmapped Tables: {len(mapping_analysis['unmapped_tables'])}")
    print(f"Full CRUD Coverage: {full_crud_count} tables")
    
    print(f"\n📋 KEY UNMAPPED CORE TABLES:")
    core_unmapped = [table for table in mapping_analysis['unmapped_tables'] 
                    if table in table_categories['core_entities']]
    
    for table in core_unmapped[:5]:
        print(f"  ❌ {table}")
    
    print(f"\n📈 WELL-SYNCHRONIZED TABLES:")
    for table, data in list(mapping_analysis['mapped_tables'].items())[:5]:
        quality = mapping_analysis['mapping_quality'][table]
        if quality['has_full_crud']:
            print(f"  ✅ {table} → {data['endpoint_resource']} (Full CRUD)")
    
    print(f"\n💡 TOP RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n💾 Analysis saved to: {json_filename}")
    print(f"📄 Report saved to: {report_filename}")
    
    return analysis_results


if __name__ == "__main__":
    try:
        results = analyze_endpoint_database_sync()
        if results:
            print(f"\n✅ Endpoint-database synchronization analysis completed successfully!")
        else:
            print(f"\n❌ Analysis failed!")
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        raise 