import json
import os
import re
from datetime import datetime

# Configuración
INPUT_FILE = 'Tasks.json'
OUTPUT_DIR = 'Google-Tasks'

def sanitize_filename(name):
    """Limpia el nombre para que sea un archivo válido."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip() or "Untitled_List"

def format_date(iso_str):
    """Convierte timestamp ISO a formato legible (YYYY-MM-DD HH:MM)."""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except ValueError:
        return iso_str

def build_task_tree(tasks):
    """Organiza lista plana de tareas en árbol jerárquico usando 'parent'."""
    task_map = {t['id']: t for t in tasks}
    tree = {}
    
    # Inicializar hijos para todos
    for t_id in task_map:
        task_map[t_id]['children'] = []

    # Asignar padres e hijos
    for task in tasks:
        parent_id = task.get('parent')
        if parent_id and parent_id in task_map:
            task_map[parent_id]['children'].append(task)
        else:
            # Es una tarea raíz
            tree[task['id']] = task
            
    # Ordenar por 'position' si existe, o por creación
    return tree

def render_task(task, indent_level=0):
    """Genera el string Markdown para una tarea y sus hijos recursivamente."""
    indent = "\t" * indent_level
    status = "x" if task.get('status') == 'completed' else " "
    title = task.get('title', 'Sin título').replace('\n', ' ')
    
    # Línea principal de tarea
    md_output = f"{indent}- [{status}] {title}"
    
    # == DATOS ADICIONALES (No perder nada) ==
    details = []
    
    # 1. Notas / Descripción
    if task.get('notes'):
        # Las notas en Obsidian quedan bien como bloque de cita o sub-bullets
        notes = task['notes'].replace('\n', f"\n{indent}\t> ")
        details.append(f"> {notes}")

    # 2. Fechas importantes (inline fields de Obsidian o texto plano)
    dates = []
    if task.get('due'):
        dates.append(f"📅 Due: {format_date(task['due'])}")
    if task.get('completed'):
        dates.append(f"✅ Completed: {format_date(task['completed'])}")
    if task.get('updated'):
        dates.append(f"🔄 Updated: {format_date(task['updated'])}")
    
    if dates:
        details.append(f"_{' | '.join(dates)}_")

    # Agregar detalles debajo de la tarea
    for detail in details:
        md_output += f"\n{indent}\t{detail}"

    # Renderizar hijos recursivamente
    # Ordenar hijos por posición si es posible (la exportación a veces trae string positions)
    children = task.get('children', [])
    # Orden simple: completadas al final, o por orden de llegada si no hay posición
    children.sort(key=lambda x: x.get('position', '')) 
    
    for child in children:
        md_output += "\n" + render_task(child, indent_level + 1)

    return md_output

def process_json():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: No se encuentra {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    task_lists = data.get('items', []) if isinstance(data, dict) else data

    for task_list in task_lists:
        if task_list.get('kind') != 'tasks#taskLists':
            # Intentar procesar como lista si la estructura difiere
            pass

        list_title = sanitize_filename(task_list.get('title', 'Lista_Sin_Titulo'))
        filename = f"{OUTPUT_DIR}/{list_title}.md"
        
        # Cabecera / Frontmatter
        content = "---\n"
        content += f"created: {format_date(task_list.get('updated'))}\n" # Usamos updated de la lista como referencia
        content += f"type: google-tasks-list\n"
        content += f"id: {task_list.get('id')}\n"
        content += "---\n\n"
        
        content += f"# {task_list.get('title')}\n\n"

        # Procesar tareas
        tasks = task_list.get('items', [])
        if not tasks:
            content += "_Lista vacía_\n"
        else:
            # Construir árbol para respetar subtareas
            task_tree = build_task_tree(tasks)
            
            # Renderizar tareas raíz (las que no tienen parent en este contexto)
            # Ordenar por posición
            root_tasks = [t for t in task_tree.values()]
            root_tasks.sort(key=lambda x: x.get('position', ''))

            for task in root_tasks:
                content += render_task(task) + "\n"

        with open(filename, 'w', encoding='utf-8') as f_out:
            f_out.write(content)
        
        print(f"Generado: {filename} ({len(tasks)} tareas)")

if __name__ == "__main__":
    process_json()
