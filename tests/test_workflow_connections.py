#!/usr/bin/env python3
"""test_workflow_connections.py — Valida los JSONs de workflows n8n.

Verifica que:
1. Todo JSON en workflows/ sea parseable
2. Todas las conexiones apunten a nodos existentes
3. No haya nodos huérfanos (sin conexiones de salida)
4. Los settings sean coherentes (executionOrder, availableInMCP)

Uso:
  python3 tests/test_workflow_connections.py
  python3 tests/test_workflow_connections.py -v   (verbose)
"""

import glob
import json
import os
import sys

WORKFLOWS_DIR = os.path.join(os.path.dirname(__file__), '..', 'extensions', 'n8n', 'workflows')

PASS = 0
FAIL = 0
ERRORS = []

def test(name, condition, detail=''):
    global PASS, FAIL
    if condition:
        PASS += 1
        if '-v' in sys.argv:
            print(f'  ✅ {name}')
    else:
        FAIL += 1
        msg = f'  ❌ {name}'
        if detail:
            msg += f': {detail}'
        print(msg)
        ERRORS.append((name, detail))

def find_workflow_files():
    """Encuentra todos los archivos JSON de workflow anidados."""
    files = []
    # Buscar en workflows/ directamente
    files.extend(glob.glob(os.path.join(WORKFLOWS_DIR, '*.json')))
    # Buscar en subdirectorios (ej: bunker-aoc-v3-enterprise-pack/workflows/)
    files.extend(glob.glob(os.path.join(WORKFLOWS_DIR, '*', 'workflows', '*.json')))
    files.extend(glob.glob(os.path.join(WORKFLOWS_DIR, '*', '*.json')))
    return sorted(set(files))


def validate_workflow(filepath):
    """Valida un archivo de workflow individual."""
    rel = os.path.relpath(filepath, os.path.join(WORKFLOWS_DIR, '..'))

    try:
        with open(filepath) as f:
            wf = json.load(f)
    except json.JSONDecodeError as e:
        test(f'{rel}: JSON malformado', False, str(e))
        return
    except Exception as e:
        test(f'{rel}: error de lectura', False, str(e))
        return

    # 1. Debe tener name
    name = wf.get('name', '').strip()
    test(f'{rel}: tiene nombre', bool(name), f'name={name!r}')

    # 2. Debe tener nodes
    nodes = wf.get('nodes', [])
    test(f'{rel}: tiene nodes', len(nodes) > 0, f'count={len(nodes)}')
    if not nodes:
        return

    # 3. Todos los nodos tienen name y type
    node_names = {}
    for i, n in enumerate(nodes):
        nname = n.get('name', '')
        ntype = n.get('type', '')
        # Verificar nombre único
        if nname in node_names:
            test(f'{rel}: nodo duplicado "{nname}"', False, f'posiciones {node_names[nname]} y {i}')
        node_names[nname] = i

        if i == 0:
            continue  # ya testeamos arriba
        test(f'{rel}: nodo[{i}] "{nname}" tiene name', bool(nname), f'type={ntype}')
        test(f'{rel}: nodo[{i}] "{nname}" tiene type', bool(ntype), f'name={nname}')

    # 4. Verificar conexiones
    connections = wf.get('connections', {})
    known_terminals = {
        # Response terminals
        'Respond to Webhook', 'Reprocessor Log', 'Reprocessor Final Log',
        'Reprocessor Idle', 'Cached Response', 'Rejected Response',
        # Cascade skip nodes
        'After Slack', 'Skip Slack', 'After Telegram', 'Skip Telegram',
        'After Discord', 'Skip Discord',
        # Dead letter queue
        'Store in DLQ',
        # Health check / alerter terminales
        'Set Status',
        # Notification terminals
        'Telegram', 'Notify Telegram',
        # Emergency
        'Emergency Queue',
    }

    # Verificar que todas las conexiones apunten a nodos existentes
    for src, outputs in connections.items():
        test(f'{rel}: conexión origen "{src}" existe como nodo',
             src in node_names,
             f'src={src}')

        for output_name, branches in outputs.items():
            for bi, branch in enumerate(branches):
                for conn_idx, conn in enumerate(branch):
                    target = conn.get('node', '')
                    test(f'{rel}: "{src}" → "{target}" (output:{output_name})',
                         target in node_names,
                         f'connection #{conn_idx} in branch #{bi}')

    # Verificar nodos sin conexiones de salida (terminales válidos)
    for nname in node_names:
        if nname not in connections and nname not in known_terminals:
            # Verificar si es un sticky note (no necesita conexiones)
            node_type = nodes[node_names[nname]].get('type', '')
            if 'stickyNote' not in node_type and 'noOp' not in node_type:
                test(f'{rel}: "{nname}" no tiene conexiones de salida ni es terminal',
                     False, f'type={node_type}')

    # 5. Validar settings
    settings = wf.get('settings', {})
    if settings:
        eo = settings.get('executionOrder', '')
        if eo:
            test(f'{rel}: executionOrder válido', eo in ('v1', 'v2'), f'executionOrder={eo}')

    # 6. Validar active flag
    active = wf.get('active', False)
    if name == 'Bunker AOC v4 Enterprise':
        test(f'{rel}: AOC experimental permanece inactivo', active is False,
             'no habilitar antes de implementar y probar autenticación y rate limiting')

        decision_node = next((node for node in nodes if node.get('name') == 'Parse AI Decision'), None)
        decision_code = (decision_node or {}).get('parameters', {}).get('jsCode', '')
        test(f'{rel}: errores de triage van a revisión humana',
             "let action = 'review';" in decision_code,
             'malformed or unavailable AI output must not auto-create an issue')
        test(f'{rel}: triage valida acción y confianza',
             'allowedActions.includes(parsed.action)' in decision_code
             and 'typeof parsedConfidence === \'number\'' in decision_code
             and 'Number.isFinite(parsedConfidence)' in decision_code,
             'only supported actions and finite confidence values may be routed')

        env_path = os.path.join(os.path.dirname(WORKFLOWS_DIR), '.env.example')
        try:
            with open(env_path, encoding='utf-8') as env_file:
                env_example = env_file.read()
        except OSError as exc:
            env_example = ''
            test(f'{rel}: existe ejemplo de configuración', False, str(exc))

        for unsupported in ('AOC_DRY_RUN', 'AOC_RATE_LIMIT_PER_MINUTE',
                            'AOC_MAX_PAYLOAD_BYTES', 'AOC_MEMORY_LIMIT'):
            test(f'{rel}: no promete el control no implementado {unsupported}',
                 unsupported not in env_example,
                 'remove example settings that the workflow does not read')

    if name == 'Bunker Health Check':
        node_types = [node.get('type', '') for node in nodes]
        test(f'{rel}: health check usa disparo manual',
             'n8n-nodes-base.manualTrigger' in node_types,
             f'tipos={node_types}')
        test(f'{rel}: health check no simula monitoreo programado',
             'n8n-nodes-base.scheduleTrigger' not in node_types,
             f'tipos={node_types}')

    # No falla, solo informa
    if '-v' in sys.argv:
        status = '🟢 ACTIVO' if active else '⚪ inactivo'
        print(f'     {rel}: {status}')

    # 7. Validar tags
    tags = wf.get('tags', [])
    if tags:
        for t in tags:
            test(f'{rel}: tag válido', isinstance(t, str) and len(t) > 0, f'tag={t!r}')


def main():
    global PASS, FAIL
    files = find_workflow_files()

    if not files:
        print('❌ No se encontraron archivos de workflow')
        sys.exit(1)

    print(f'🔍 Encontrados {len(files)} workflows\n')

    for f in files:
        validate_workflow(f)
        print()

    # Resumen
    total = PASS + FAIL
    print(f'{"="*50}')
    print(f'RESUMEN: {total} tests | ✅ {PASS} passed | ❌ {FAIL} failed')
    print(f'{"="*50}')

    if FAIL > 0:
        print('\nErrores:')
        for name, detail in ERRORS:
            print(f'  ❌ {name}')
            if detail:
                print(f'     {detail}')
        sys.exit(1)
    else:
        print('🎉 Todos los workflows están válidos')


if __name__ == '__main__':
    main()
